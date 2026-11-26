"""PostgreSQL 읽기 전용 보고서 ID 파싱, 상태 뷰 정제, 벡터 최신성 검증 및 정책 함수를 통합 제공하는 모듈."""


def parse_report_id(value) -> int:
    """외부 입력값을 SQL 인젝션이나 task_id 혼용 없이 안전한 reports.report_id 정수로 변환."""
    # 도메인 ID 파싱·검증 함수를 호출 시점에만 지연 임포트
    # - report_id_from : 문자열/정수 입력의 양의 정수 변환 및 비정상 값 차단
    from coursekit.contracts import report_id_from

    # 검증 및 정규화된 report_id 반환
    return report_id_from(value)


def status_view(raw: dict) -> dict:
    """원시 DB 응답에서 인덱싱 상태(pending/ready/failed)와 벡터 정합성 지표를 분리해 반환."""
    # 조회 실패 시 불완전한 필드 참조를 피하고 최소 식별자만 포함한 not_found 응답 반환
    if raw["status"] != "ok":
        return {"status": "not_found", "report_id": raw["report_id"]}
    # DB 인덱싱 상태(index_status)와 실제 벡터 최신성(vector_fresh)을 나란히 노출해 오판 방지
    return {
        "report_id": raw["report_id"],
        "index_status": raw["index_status"],
        "revision": raw["revision"],
        "vector_fresh": raw["vector_fresh"],
    }


def status_is_usable(raw: dict) -> bool:
    """단순 ready 상태뿐 아니라 실제 벡터 최신성(vector_fresh)까지 충족하는지 엄격히 판별."""
    # DB 상태가 ready여도 벡터 동기화가 지연될 수 있으므로 세 조건을 모두 만족할 때만 사용 가능 판정
    return (
        raw.get("status") == "ok"
        and raw.get("index_status") == "ready"
        and raw.get("vector_fresh") is True
    )


# 책임이 분리된 읽기 정책 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - enforce_read_policy : 앱 카테고리 기반 상태 조회 접근 제어
from policy_05 import enforce_read_policy

"""
[설계 평가]
- parse_report_id로 입력 단계에서 문자열 SQL 결합 위험과 task_id 오용을 선제 차단
- index_status와 vector_fresh를 분리 검증해 스테일(stale) 벡터 기반 검색 오류 방지
- policy_05의 정책 함수를 re-export하여 모듈 분리와 호출 측 인터페이스 일관성 유지
"""
