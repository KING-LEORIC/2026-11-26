"""기본 실습 질의 제공, 에이전트 실행 결과의 API 계약 변환, FastAPI 엔드포인트 구성 및 감사 함수를 통합 제공하는 모듈."""


def default_question() -> str:
    """실제 보고서 내용 검색과 63번 보고서 인덱싱 상태 조회를 함께 묻는 기본 데모 질문 반환."""
    # 실습용 기본 질의 생성 함수를 호출 시점에만 지연 임포트
    # - demo_question : 복합 Tool 호출 검증용 표준 질의 문자열 제공
    from coursekit.live import demo_question

    # 일관된 테스트 질의 반환
    return demo_question()


def api_response(run: dict) -> dict:
    """에이전트 원시 실행 결과를 완료 상태·답변·출처 검증 필드가 포함된 API 응답 계약으로 변환."""
    # 비정상 종료된 에이전트 결과가 클라이언트에 200 OK로 전달되는 것을 방지
    if run.get("status") != "completed":
        raise RuntimeError("Agent did not complete")
    # 출처 ID 검증이 실패한 환각 응답의 외부 노출을 차단하기 위한 계약 강제
    if run.get("citation_ids_valid") is not True:
        raise RuntimeError(
            "UNVERIFIED_CITATION: Agent가 제공되지 않은 출처 ID를 인용했습니다."
        )
    # API 스키마에 정의된 필수 필드만 선별해 일관된 응답 구조 반환
    return {
        "status": "completed",
        "answer": run["answer"],
        "tool_trace": run["tool_trace"],
        "citation_ids_valid": run["citation_ids_valid"],
        "verified_evidence_ids": run["verified_evidence_ids"],
    }


def make_api():
    """로컬 교육용 FastAPI 앱을 생성하고 POST /api/agent/ask 엔드포인트 등록(인증 미구현)."""
    # 실제 에이전트 실행 오케스트레이션 함수를 지연 임포트
    # - run_agent : 질문 입력에 대한 LLM 추론 및 Tool 실행 결과 딕셔너리 반환
    from coursekit.agent import run_agent

    # 웹 API 서버 프레임워크 및 HTTP 예외 클래스 임포트
    # - FastAPI : ASGI 애플리케이션 및 라우트 등록
    # - HTTPException : 오류 유형별 상태 코드 매핑 반환
    from fastapi import FastAPI, HTTPException

    # 요청 본문 유효성 검증을 위한 Pydantic 모델 임포트
    # - BaseModel : JSON 요청 스키마 정의
    # - Field : 질문 길이 제한 등 입력 경계값 제약 적용
    from pydantic import BaseModel, Field

    class Ask(BaseModel):
        """질문 요청 본문의 최소·최대 길이를 제한하는 입력 스키마."""

        question: str = Field(min_length=1, max_length=1000)

    # API 문서화 메타데이터를 포함한 FastAPI 인스턴스 초기화
    app = FastAPI(title="Day29 Existing Report DB Agent", version="1.0")

    @app.post("/api/agent/ask")
    def ask(body: Ask):
        """사용자 질문을 에이전트에 전달하고 예외 유형에 따라 정제된 HTTP 오류 코드로 변환."""
        # 내부 스택 트레이스나 DB/LLM 상세 오류 노출을 막고 원인별 표준 HTTP 상태 코드를 반환하기 위한 예외 분기
        try:
            return api_response(run_agent(body.question))
        except ValueError as exc:
            # 입력값 검증 실패 시 422 Unprocessable Entity 반환
            raise HTTPException(status_code=422, detail="잘못된 입력") from exc
        except PermissionError as exc:
            # 카테고리/권한 정책 위반 시 403 Forbidden 반환
            raise HTTPException(status_code=403, detail="접근 정책 위반") from exc
        except RuntimeError as exc:
            # 에이전트 미완료 또는 출처 계약 실패 시 502 Bad Gateway 반환
            raise HTTPException(
                status_code=502, detail="Agent 결과/출처 계약 검증 실패"
            ) from exc
        except Exception as exc:
            # DB·GPU·LLM 인프라 장애 등 예기치 못한 오류 시 503 Service Unavailable 반환
            raise HTTPException(
                status_code=503, detail="Agent/DB/GPU/LLM 실행 실패"
            ) from exc

    # 구성된 FastAPI 애플리케이션 객체 반환
    return app


# 책임이 분리된 응답 감사 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - audit_response : 에이전트 실행 완료 및 출처 유효성 최종 게이트 검증
from policy_08 import audit_response

"""
[설계 평가]
- Pydantic Field 제약(1~1000자)으로 과도한 길이의 프롬프트 유입을 입구 단계에서 차단
- 예외 계층(422/403/502/503)을 명확히 매핑해 내부 구현·스택 트레이스 노출 없이 장애 원인 구분 가능
- policy_08의 감사 함수를 re-export하여 모듈 분리와 호출 측 인터페이스 일관성 유지
"""
