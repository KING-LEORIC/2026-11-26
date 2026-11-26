"""AIMessage Tool 호출 요청 생성, ToolMessage 결과 매칭, 정책 검증 함수를 통합 제공하는 모듈."""


def make_request(tool_name: str, args: dict, call_id: str) -> dict:
    """실제 도구를 실행하지 않고 표준 Tool 호출 요청(AIMessage.tool_calls 항목) 딕셔너리 생성."""
    # 계약 스키마에 맞춘 요청 객체 생성 함수를 호출 시점에만 지연 임포트
    # - tool_call_request : tool_name, args, call_id 기반 표준 요청 페이로드 구성
    from coursekit.contracts import tool_call_request

    # 표준화된 Tool 호출 요청 스키마 반환
    return tool_call_request(tool_name, args, call_id)


def match_result(call: dict, result: dict) -> dict:
    """Tool 실행 결과를 원본 호출의 tool_call_id와 연결한 ToolMessage 딕셔너리 생성."""
    # 요청-응답 연결 규격을 강제하는 계약 함수를 호출 시점에만 지연 임포트
    # - tool_result_message : 호출 정보(call)와 실행 결과(result)를 동일 ID로 결합
    from coursekit.contracts import tool_result_message

    # 호출 ID가 바인딩된 결과 메시지 반환
    return tool_result_message(call, result)


# 책임이 분리된 정책 검증 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - summarize_pairs : 다중 Tool 호출·응답 쌍의 중복 검사 및 미매칭 요약
# - validate_message_pair : 단일 요청·응답 쌍의 ID 및 Tool 이름 일치 검증
from policy_02 import summarize_pairs, validate_message_pair

"""
[설계 평가]
- coursekit.contracts의 표준 빌더에 위임해 메시지 스키마 일관성 유지
- policy_02의 검증 함수를 re-export하여 역할 분리를 유지하면서도 호출 측 인터페이스 단순화
"""
