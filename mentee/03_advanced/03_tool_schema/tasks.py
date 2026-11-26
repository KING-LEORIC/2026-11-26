"""report_id 유효성 검증, 읽기 전용 DB 상태 조회 @tool 등록, 스키마 검증 함수를 통합 제공하는 모듈."""


def validate_id(report_id: int) -> int:
    """실제 DB의 reports.report_id 규격에 맞는 양의 정수만 통과."""
    # 도메인 ID 경계값 검증 함수를 호출 시점에만 지연 임포트
    # - report_id_from : 양의 정수 여부 확인 및 비정상 입력 차단
    from coursekit.contracts import report_id_from

    # 검증된 report_id 반환
    return report_id_from(report_id)


def register_status_tool():
    """@tool 데코레이터를 적용해 실제 DB 상태 조회 Tool을 생성 및 반환."""
    # DB 조회 결과를 LLM이 소비하기 쉬운 JSON 문자열로 직렬화하기 위한 표준 라이브러리 임포트
    # - json : 조회 결과 딕셔너리의 JSON 문자열 변환
    import json

    # 실제 보고서 인덱싱 상태를 읽기 전용으로 조회하는 DB 유틸리티 임포트
    # - fetch_report_status : report_id 기준 DB 상태 레코드 조회
    from coursekit.db import fetch_report_status

    # 파이썬 함수를 LangChain Tool 객체 및 Pydantic 스키마로 래핑하기 위한 데코레이터 임포트
    # - tool : 함수 시그니처와 docstring 기반 Tool 메타데이터 자동 생성
    from langchain.tools import tool

    @tool("lookup_status")
    def lookup_status(report_id: int) -> str:
        """기존 보고서 report_id의 인덱싱 상태를 읽기 전용으로 조회(task_id와 구분)."""
        # 입력 ID 검증 후 DB 조회 결과를 한글 유지(ensure_ascii=False) 및 비직렬화 타입 대응(default=str)으로 직렬화해 반환
        return json.dumps(
            fetch_report_status(validate_id(report_id)), ensure_ascii=False, default=str
        )

    # 생성된 LangChain Tool 객체 반환
    return lookup_status


# 책임이 분리된 스키마 검증 모듈의 함수를 tasks 네임스페이스로 다시 내보내기(re-export) 위해 임포트
# - enforce_explicit_schema : report_id 필수 스키마 준수 여부 검증
# - schema_fields : Tool 입력 스키마의 필드 목록 추출
from policy_03 import enforce_explicit_schema, schema_fields

"""
[설계 평가]
- Tool 내부에서 validate_id로 입력을 2차 검증해 스키마 우회나 잘못된 타입 유입 방지
- DB·LangChain 의존성을 register_status_tool 내부로 지연 임포트해 --check 모드에서의 불필요한 로딩 차단
- policy_03의 스키마 검증 함수를 re-export하여 모듈 분리와 호출 편의성을 동시에 확보
"""
