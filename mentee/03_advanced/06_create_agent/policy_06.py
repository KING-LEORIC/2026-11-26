"""에이전트 대화 이력에서 모델의 Tool 호출 수와 실제 ToolMessage 수를 집계하고 최종 자연어 응답을 추출하는 모듈."""


def summarize_tool_messages(messages: list) -> dict:
    """대화 메시지 목록에서 모델의 Tool 호출 요청 수와 실제 ToolMessage 실행 수를 분리 집계."""
    # 메시지 집계 유틸리티를 호출 시점에만 지연 임포트
    # - count_tool_calls : AIMessage.tool_calls 수와 ToolMessage 수의 분리 산출
    from coursekit.contracts import count_tool_calls

    # 요청·응답 횟수 요약 딕셔너리 반환
    return count_tool_calls(messages)


def final_text(messages: list) -> str:
    """중간 Tool 호출 메시지를 제외하고 마지막 최종 AIMessage의 텍스트 본문만 추출."""
    # 대화 이력의 가장 마지막 응답부터 역순으로 탐색해 최종 답변을 빠르게 찾기 위함
    for m in reversed(messages):
        # Tool 호출을 동반한 중간 AIMessage가 아닌 순수 최종 답변 메시지만 선별
        if m.__class__.__name__ == "AIMessage" and not getattr(m, "tool_calls", []):
            # 일반 문자열 응답은 그대로 반환
            if isinstance(m.content, str):
                return m.content
            # 멀티파트/리소닝 모델 등에서 list 블록으로 반환된 경우 텍스트 조각만 추출해 결합
            if isinstance(m.content, list):
                parts = [
                    b if isinstance(b, str) else b.get("text", "")
                    for b in m.content
                    if isinstance(b, str)
                    or (isinstance(b, dict) and b.get("type") == "text")
                ]
                text = "".join(parts).strip()
                if text:
                    return text
            raise ValueError(
                "최종 응답은 문자열이 아닙니다. Structured Output 파서 필요."
            )
    # 탐색 종료 시점까지 유효한 최종 AIMessage가 없으면 비정상 종료로 간주해 예외 발생
    raise ValueError("최종 AIMessage가 없습니다.")


"""
[설계 평가]
- 역순 탐색과 tool_calls 유무 검사로 중간 추론 단계가 최종 응답으로 오인되는 현상 방지
- 문자열 외 응답 타입에 대해 명시적 예외를 발생시켜 후속 파서 누락을 조기 탐지
"""
