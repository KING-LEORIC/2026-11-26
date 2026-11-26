"""01 · AI Agent vs 고정 RAG/Workflow · 심화 · 수강생 TODO.



DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.

"""

"""사용자 질문의 키워드를 분석해 고정 규칙 기반 처리 전략과 Tool 실행 계획을 생성하고, 정책 검증 함수를 통합 제공하는 모듈."""


def classify_request(question: str) -> str:
    """질문 성격에 따라 'rag', 'db', 'agent' 중 하나의 처리 전략을 결정."""
    # 영문 키워드 매칭 시 대소문자 차이로 인한 누락 방지
    q = question.lower()
    # DB 상태 조회가 필요한 요청인지 키워드 기반으로 판별
    has_db = any(t in q for t in ("상태", "인덱싱", "revision", "ready", "pending"))
    # 문서 검색 근거가 필요한 요청인지 키워드 기반으로 판별
    has_doc = any(t in q for t in ("찾아", "내용", "설명", "근거", "검색"))
    # 문서 검색과 상태 조회가 모두 필요한 복합 질의는 에이전트 전략으로 분기
    if has_db and has_doc:
        return "agent"
    # 상태 조회 키워드만 존재할 경우 불필요한 문서 검색을 피하기 위해 DB 단일 전략 선택
    if has_db:
        return "db"
    # 특정 키워드가 없는 일반 질의는 기본값으로 문서 검색(RAG) 전략 반환
    return "rag"


def plan_for_request(question: str) -> dict:
    """분류된 전략에 대응하는 Tool 목록과 결정 근거를 포함한 실행 계획 딕셔너리 생성."""
    # 질문 유형에 맞는 전략을 먼저 산출
    mode = classify_request(question)
    # 전략별 허용 Tool 목록을 명시적으로 매핑하여 일관된 실행 계획 보장
    tools = {
        "rag": ["rag_search"],
        "db": ["lookup_status"],
        "agent": ["rag_search", "lookup_status"],
    }[mode]
    # 후속 검증 및 실행 단계에서 활용할 전략, Tool 목록, 판단 출처를 구조화하여 반환
    return {
        "strategy": mode,
        "tools": tools,
        "decision": "고정 조건에 따른 실습용 계획; 실제 Agent 선택은 06에서 LLM 수행",
    }


# 책임이 분리된 정책 검증 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - needs_two_sources : 문서 검색과 DB 조회가 모두 필요한 복합 계획 여부 판별
# - validate_plan : 실행 계획 내 허용 Tool 목록 및 중복 정책 준수 여부 검증
from policy_01 import needs_two_sources, validate_plan

"""
[설계 평가]
- 질의 분류(classify_request)와 계획 수립(plan_for_request) 책임을 분리하여 규칙 변경 시 수정 범위를 최소화
- 딕셔너리 매핑으로 전략별 Tool 구성을 명확히 고정해 예측 가능한 워크플로우 동작 보장
- policy_01의 검증 함수를 re-export하여 모듈 간 책임 분리를 유지하면서도 호출 측(main.py)의 인터페이스 일관성 확보
"""
