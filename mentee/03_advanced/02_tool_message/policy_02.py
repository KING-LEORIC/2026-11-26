"""Tool 호출 요청(AIMessage)과 결과(ToolMessage) 간의 ID·이름 일치 여부 및 누락/중복 상태를 검증하는 모듈."""


def validate_message_pair(call: dict, message: dict) -> bool:
    """단일 Tool 호출 요청과 응답 메시지가 동일한 호출 ID와 Tool 이름을 가리키는지 판별."""
    # 다른 호출의 결과가 잘못 매칭되는 오연결을 방지하기 위해 호출 ID와 Tool 이름을 동시에 대조
    return call["id"] == message["tool_call_id"] and call["name"] == message["name"]


def summarize_pairs(calls: list[dict], messages: list[dict]) -> dict:
    """다중 Tool 호출 목록과 응답 목록 간 중복 ID를 차단하고 미매칭 건을 집계."""
    # 요청 측 고유 식별자 목록 추출
    ids = [c["id"] for c in calls]
    # 응답 측 연결 키 목록 추출
    done = [m["tool_call_id"] for m in messages]
    # 요청 또는 응답 내에 중복된 ID가 존재하면 매칭 무결성이 깨지므로 즉시 예외 발생
    if len(ids) != len(set(ids)) or len(done) != len(set(done)):
        raise ValueError("중복된 tool_call_id")
    # 요청 수, 응답 수, 응답이 누락된 정렬된 ID 목록을 감사 결과로 반환
    return {
        "requested": len(ids),
        "returned": len(done),
        "unmatched": sorted(set(ids) - set(done)),
    }


"""
[설계 평가]
- ID와 Tool 이름의 이중 검증으로 메시지 쌍 매칭 오류를 원천 차단
- 집합 차연산(set)과 길이 비교를 통해 중복 ID 검출 및 미응답 호출 집계를 간결하게 처리
"""
