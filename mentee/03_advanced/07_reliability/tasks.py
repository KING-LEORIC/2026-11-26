"""보고서 ID 사전 검증, 보안이 반영된 오류 코드 분류, 실행 상한·감사 로그 정책 함수를 통합 제공하는 모듈."""


def validate_report_id(value) -> int:
    """DB 쿼리 실행 전 비정상 인수를 차단하고 유효한 양의 정수 report_id만 반환."""
    # 도메인 ID 검증 함수를 호출 시점에만 지연 임포트
    # - report_id_from : 입력값의 양의 정수 변환 및 잘못된 인수 예외 처리
    from coursekit.contracts import report_id_from

    # DB 접근 전에 검증된 report_id 반환
    return report_id_from(value)


def classify_error(exc: Exception) -> dict:
    """예외 유형을 입력 오류와 도구 실행 오류로 구분하고 내부 상세·SQL·비밀정보 노출을 차단."""
    # ValueError는 사용자 입력 오류(INVALID_ARGS)로, 그 외 예외는 도구 장애(TOOL_FAILURE)로 추상화해 반환
    return {
        "status": "error",
        "error_code": "INVALID_ARGS" if isinstance(exc, ValueError) else "TOOL_FAILURE",
    }


# 책임이 분리된 정책 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - audit_log : 기밀 정보를 제거한 감사 메타데이터 생성
# - tool_budget_check : Tool 호출 횟수 상한 초과 여부 판별
from policy_07 import audit_log, tool_budget_check

"""
[설계 평가]
- 예외 메시지 원문 대신 표준화된 error_code만 노출해 SQL 구문이나 내부 시스템 정보 유출 방지
- DB 쿼리 전 validate_report_id 검증을 강제해 불필요한 DB 부하 및 오류 유발 차단
- policy_07의 상한·감사 함수를 re-export하여 모듈 분리와 호출 측 인터페이스 일관성 유지
"""
