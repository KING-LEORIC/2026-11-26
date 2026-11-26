"""복합 질의 생성, LLM·실제 Tool 2종·호출 상한 미들웨어를 결합한 에이전트 구성, 메시지 감사 함수를 통합 제공하는 모듈."""


def question_for_agent(report_id: int) -> str:
    """문서 내용 검색과 특정 보고서 인덱싱 상태 조회를 동시에 요구하는 복합 자연어 질문 생성."""
    # 도메인 ID 검증 함수를 호출 시점에만 지연 임포트
    # - report_id_from : 양의 정수 기반 보고서 ID 유효성 확인
    from coursekit.contracts import report_id_from

    # 비정상 ID가 프롬프트에 삽입되는 것을 막기 위해 먼저 정규화
    rid = report_id_from(report_id)
    # 에이전트가 rag_search와 lookup_status 두 Tool을 모두 호출하도록 유도하는 복합 질의 반환
    return f"RAG 근거 인용 정확도 향상과 관련된 보고서 내용을 설명하고, {rid}번 보고서의 인덱싱 상태도 알려줘."


def make_agent():
    """LLM 설정 검증 후 실제 Tool 2종과 호출 횟수 상한 미들웨어가 장착된 LangChain 에이전트 생성."""
    # 에이전트 시스템 프롬프트 및 실제 Tool 빌더 임포트
    # - SYSTEM_PROMPT : 에이전트 역할·도구 사용 지침 정의
    # - build_tools : rag_search 및 lookup_status Tool 인스턴스 목록 생성
    from coursekit.agent import SYSTEM_PROMPT, build_tools

    # LLM API 키·모델명 검증 및 런타임 설정 조회 유틸리티 임포트
    # - require_llm_settings : 필수 LLM 환경 변수 누락 시 조기 실패 유도
    # - settings : 설정된 llm_model 이름 로드
    from coursekit.settings import require_llm_settings, settings

    # Tool 호출 루프를 제어하는 LangChain 표준 에이전트 생성 함수 임포트
    # - create_agent : 모델·도구·프롬프트·미들웨어를 결합한 실행 그래프 구성
    from langchain.agents import create_agent

    # 무한 루프 및 과도한 API 비용 발생을 막기 위한 실행 제한 미들웨어 임포트
    # - ModelCallLimitMiddleware : 단일 실행당 LLM 호출 상한 제어
    # - ToolCallLimitMiddleware : 단일 실행당 Tool 호출 상한 제어
    from langchain.agents.middleware import (
        ModelCallLimitMiddleware,
        ToolCallLimitMiddleware,
    )

    # OpenAI 호환 LLM 클라이언트 래퍼 임포트
    # - ChatOpenAI : Tool Calling을 지원하는 채팅 모델 인스턴스 생성
    from langchain_openai import ChatOpenAI

    # 에이전트 생성 전 필수 LLM 설정이 유효한지 선제 검증
    require_llm_settings()
    # 네트워크 지연·무한 재시도·과다 호출을 방지하기 위해 타임아웃·재시도·미들웨어 상한을 함께 적용해 반환
    return create_agent(
        model=ChatOpenAI(model=settings().llm_model, timeout=45, max_retries=1),
        tools=build_tools(),
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            ToolCallLimitMiddleware(run_limit=4, exit_behavior="error"),
            ModelCallLimitMiddleware(run_limit=6, exit_behavior="error"),
        ],
    )


# 책임이 분리된 메시지 감사·추출 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - final_text : 최종 AIMessage 텍스트 추출
# - summarize_tool_messages : 모델 호출 수 및 ToolMessage 수 집계
from policy_06 import final_text, summarize_tool_messages

"""
[설계 평가]
- ToolCallLimitMiddleware(4회)와 ModelCallLimitMiddleware(6회)를 결합해 에이전트 무한 루프 및 비용 폭증 방지
- 무거운 LangChain·LLM·에이전트 의존성을 make_agent 내부로 지연 임포트해 --check 모드 경량 실행 보장
- policy_06의 메시지 감사 함수를 re-export하여 모듈 분리와 호출 측 인터페이스 일관성 유지
"""
