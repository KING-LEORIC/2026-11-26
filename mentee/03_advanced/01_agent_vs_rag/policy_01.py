"""실행 계획의 Tool 구성 여부와 등록·중복 정책 준수 여부를 검증하는 모듈."""


def needs_two_sources(plan: dict) -> bool:
    """문서 검색과 DB 조회 Tool이 모두 포함된 복합 실행 계획인지 판별."""
    # 순서와 무관하게 두 핵심 소스가 모두 포함되었는지 집합 비교로 확인
    return set(plan["tools"]) == {"rag_search", "lookup_status"}


def validate_plan(plan: dict) -> dict:
    """계획에 포함된 Tool 목록의 타입, 공백, 중복, 허용 여부를 일괄 검증."""
    # 사전에 승인된 Tool만 실행되도록 허용 집합 정의
    allowed = {"rag_search", "lookup_status"}
    # tools 키 누락 시 안전하게 빈 리스트로 대체하여 검증 단계로 전달
    names = plan.get("tools", [])
    # 잘못된 타입·빈 목록·중복 Tool·미등록 Tool 실행을 사전에 차단하기 위한 방어 조건
    if (
        not isinstance(names, list)
        or not names
        or len(names) != len(set(names))
        or not set(names) <= allowed
    ):
        raise ValueError("Tool 계획이 등록 목록·중복 정책을 위반합니다.")
    # 모든 정책을 통과한 경우 유효 상태와 정제된 Tool 목록 반환
    return {"valid": True, "tools": names}


"""
[설계 평가]
- 집합 연산(set)을 활용해 Tool 순서와 무관한 복합 소스 판별 및 미등록/중복 검증을 간결하게 처리
- 실행 전 단계에서 타입·공백·권한을 선제적으로 검증하여 잘못된 Tool 호출로 인한 런타임 오류 방지
"""
