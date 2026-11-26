"""에이전트 실행 결과의 완료 상태와 출처 검증 통과 여부를 최종 감사하는 정책 모듈."""


def audit_response(raw: dict) -> dict:
    """에이전트 실행 완료 여부와 출처 ID 유효성을 확인해 성공으로 위장된 오류 응답을 차단."""
    # 미완료 또는 실패한 실행 결과가 정상 응답으로 기록되는 것을 방지하기 위한 상태 검증
    if raw.get("status") != "completed":
        raise ValueError("agent incomplete")
    # 검색 컨텍스트에 없는 허위 출처 인용을 최종 게이트에서 거절하기 위한 불리언 엄격 비교
    if raw.get("citation_ids_valid") is not True:
        raise ValueError("invalid citations")
    # 모든 게이트를 통과한 경우 검증 완료 상태와 실행된 Tool 추적 건수 반환
    return {"status": "verified", "tools": len(raw.get("tool_trace", []))}


"""
[설계 평가]
- status와 citation_ids_valid를 독립 검증해 부분 성공이나 환각 출처가 통과하는 우회 경로 차단
- 최소한의 감사 결과(verified, tools)만 반환해 감사 단계의 결합도 최소화
"""
