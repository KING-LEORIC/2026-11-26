"""DB 조회 결과에 앱 수준의 카테고리 허용 정책을 적용해 노출 가능한 상태 필드만 필터링하는 모듈."""


def enforce_read_policy(raw: dict, allowed: set[str]) -> dict:
    """조회 성공 여부와 허용 카테고리 포함 여부를 검사해 접근 제어된 상태 정보 반환."""
    # 존재하지 않거나 조회 실패한 레코드는 세부 정보를 노출하지 않고 not_found로 통일 반환
    if raw.get("status") != "ok":
        return {"status": "not_found"}
    # 비허용 카테고리의 레코드 존재 여부를 추론하지 못하도록 모호한 거부 상태 반환
    if raw["category_code"] not in allowed:
        return {"status": "not_found_or_forbidden"}
    # 정책을 통과한 경우에만 핵심 식별자·인덱싱 상태·리비전·벡터 최신성 필드 반환
    return {
        "report_id": raw["report_id"],
        "index_status": raw["index_status"],
        "revision": raw["revision"],
        "vector_fresh": raw["vector_fresh"],
    }


"""
[설계 평가]
- 비허용 카테고리 접근 시 존재 여부 유추(enumeration)를 막기 위해 not_found_or_forbidden 상태 반환
- 원시 DB 레코드 전체 대신 필요한 상태 필드만 선별 노출해 불필요한 내부 정보 유출 방지
"""
