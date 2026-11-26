"""RAG 응답 결과의 출처 ID 정규화 및 선택된 검색 컨텍스트 기반 근거 무결성을 검증하는 모듈."""


def format_evidence(result: dict) -> dict:
    """RAG 응답에서 처리 상태, 답변 본문, 출처 ID 목록만 추출해 간결한 근거 딕셔너리 생성."""
    # 후속 응답·로깅에서 원문 전체 대신 상태·답변·출처 식별자만 구분해 전달하기 위한 구조화
    return {
        "status": result["status"],
        "answer": result["answer"],
        "source_ids": [x["source_id"] for x in result["sources"]],
    }


def validate_evidence(result: dict) -> bool:
    """실제 검색 컨텍스트에 포함된 출처만 유효 근거로 인정하고 No-answer 상태의 허위 출처를 차단."""
    # 출처 계약 검증 함수를 호출 시점에만 지연 임포트
    # - validate_source_contract : 응답 출처와 허용된 검색 ID 집합 대조 및 무응답 상태 검증
    from coursekit.contracts import validate_source_contract

    # 실제 검색 결과(included_ids)를 표준 출처 ID 접두사(RPT-) 형식으로 변환해 허용 집합 구성
    verified = {f"RPT-{rid}" for rid in result["retrieval"]["included_ids"]}
    # LLM이 검색 컨텍스트 밖의 출처를 환각으로 인용하지 않았는지 최종 검증 결과 반환
    return validate_source_contract(result, verified)


"""
[설계 평가]
- retrieval.included_ids를 기준으로 허용 출처 집합을 동적 생성해 컨텍스트 외 출처 인용(환각) 방지
- 출력 포맷팅(format_evidence)과 근거 무결성 검증(validate_evidence)을 분리해 재사용성 확보
"""
