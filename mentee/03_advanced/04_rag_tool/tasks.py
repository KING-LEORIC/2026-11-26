"""RAG 검색 질의·카테고리 검증, pgvector/CUDA 기반 실제 RAG 호출, 근거 검증 함수를 통합 제공하는 모듈."""


def prepare_search(query: str, category: str = "ALL") -> dict:
    """허용된 6개 카테고리 및 질의 유효성을 검증한 뒤 정규화된 검색 요청 딕셔너리 생성."""
    # 검색 요청 규격 검증 함수를 호출 시점에만 지연 임포트
    # - search_request : 질의 공백·길이 및 허용 카테고리(6종+ALL) 검증
    from coursekit.contracts import search_request

    # 잘못된 카테고리나 빈 질의로 인한 불필요한 임베딩·DB 검색 비용 방지
    query, category = search_request(query, category)
    # RAG 호출 함수에 전달할 정제된 요청 페이로드 반환
    return {"query": query, "category": category}


def invoke_rag(request: dict) -> dict:
    """검증된 요청을 바탕으로 기존 DB의 pgvector/CUDA RAG 파이프라인을 직접 실행."""
    # 실제 벡터 검색 및 LLM 답변 생성 함수를 호출 시점에만 지연 임포트
    # - rag_answer : pgvector 기반 문서 검색 및 근거 포함 답변 생성
    from coursekit.rag import rag_answer

    # 가짜 목업 없이 실제 RAG 파이프라인 실행 결과 반환
    return rag_answer(request["query"], request["category"])


# 책임이 분리된 근거 검증 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - format_evidence : RAG 응답에서 상태·답변·출처 ID 추출
# - validate_evidence : 검색 컨텍스트 기반 출처 무결성 검증
from policy_04 import format_evidence, validate_evidence

"""
[설계 평가]
- 검색 전 입력 검증(prepare_search)과 실제 RAG 실행(invoke_rag)을 분리해 비정상 질의의 인프라 유입 차단
- 무거운 CUDA/pgvector/RAG 모듈을 함수 내부에서 지연 임포트해 --check 모드 경량 실행 보장
- policy_04의 근거 검증 함수를 re-export하여 모듈 분리와 호출 측 인터페이스 일관성 유지
"""
