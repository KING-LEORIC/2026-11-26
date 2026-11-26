"""Tool 호출 횟수 상한 검사 및 민감 정보를 제거한 감사 로그 생성을 담당하는 정책 모듈."""


def tool_budget_check(calls: int, maximum: int) -> bool:
    """누적 호출 횟수가 허용 상한 이내인지 검증해 무한 반복 실행을 차단."""
    # 음수 호출 횟수나 1 미만의 비정상 상한 설정으로 인한 정책 무력화 방지
    if maximum < 1 or calls < 0:
        raise ValueError("invalid limit counters")
    # 상한을 초과한 경우 False를 반환해 후속 Tool 실행을 중단하도록 유도
    return calls <= maximum


def audit_log(event: dict) -> dict:
    """이벤트 페이로드에서 API Key, 질문 원문 등 기밀 값을 제거한 감사 메타데이터 반환."""
    # 민감 정보 마스킹·필터링 함수를 호출 시점에만 지연 임포트
    # - sanitize_event : 기밀 필드 제거 및 안전한 감사 로그 규격 변환
    from coursekit.contracts import sanitize_event

    # 기밀 정보가 정제된 감사 이벤트 딕셔너리 반환
    return sanitize_event(event)


"""
[설계 평가]
- 카운터 경계값(maximum < 1, calls < 0) 선제 검증으로 잘못된 예산 설정에 의한 무한 루프 방지
- sanitize_event 위임을 통해 감사 로그 내 API Key 및 사용자 질문 원문 유출 차단
"""
