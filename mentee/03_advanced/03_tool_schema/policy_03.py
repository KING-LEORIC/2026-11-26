"""LangChain Tool의 Pydantic 기반 입력 JSON Schema를 추출하고 필수 인수 포함 여부를 검증하는 모듈."""


def schema_fields(tool_obj) -> list[str]:
    """모델에게 노출되는 Tool 입력 파라미터 필드명 목록을 정렬하여 반환."""
    # Pydantic args_schema에서 JSON Schema 딕셔너리 추출
    schema = tool_obj.args_schema.model_json_schema()
    # 비교 및 출력 일관성을 유지하기 위해 properties 키를 알파벳순으로 정렬해 반환
    return sorted(schema.get("properties", {}))


def enforce_explicit_schema(tool_obj) -> dict:
    """Tool의 JSON Schema에 필수 파라미터(report_id)가 강제되어 있는지 검증."""
    # 모델에 전달될 입력 스키마의 required 제약 조건 확인을 위해 JSON Schema 조회
    schema = tool_obj.args_schema.model_json_schema()
    # LLM이 report_id 없이 Tool을 호출하는 모호한 실행을 사전에 차단하기 위한 방어 조건
    if "report_id" not in schema.get("required", []):
        raise ValueError("report_id 필수 인수 누락")
    # 검증을 통과한 Tool 이름과 필수 필드 목록 반환
    return {"name": tool_obj.name, "required": schema["required"]}


"""
[설계 평가]
- Pydantic의 model_json_schema()를 직접 검사해 런타임 이전에 Tool 입력 규격을 정적으로 보증
- 필수 인수 누락 시 즉시 ValueError를 발생시켜 LLM의 불완전한 Tool 호출을 선제적으로 방지
"""
