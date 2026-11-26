# CLI 실행 인자(--check, --serve) 파싱 및 도움말 제공을 위한 표준 라이브러리 임포트
# - argparse : 명령행 옵션 정의 및 입력값 해석
import argparse

# 모듈 탐색 경로(sys.path)를 동적으로 확장하기 위한 시스템 모듈 임포트
# - sys : 상위 루트 경로 등록에 필요한 인터프리터 경로 목록 접근
import sys

# 실행 위치와 무관하게 프로젝트 루트 디렉터리를 안전하게 계산하기 위한 경로 모듈 임포트
# - Path : 현재 파일 기준 상대 부모 경로 탐색
from pathlib import Path

# 하위 폴더에서 직접 실행해도 루트 모듈을 불러올 수 있도록 프로젝트 루트를 탐색 경로 최상단에 추가
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# 입력 검증, 오류 분류, 호출 상한 검사, 감사 로그 함수가 통합된 과제 모듈 임포트
# - tasks : 보안·정책 검증 및 오류 분류 함수 제공
import tasks

"""CLI 실행 모드에 따라 함수 구조 자가 점검 또는 실제 DB 조회·호출 상한·로그 마스킹 검증을 수행하는 진입점 모듈."""


def main():
    """명령행 옵션을 해석해 구조 점검(--check) 또는 실제 DB 조회·상한 초과 판별·감사 로그 마스킹 흐름을 실행."""
    # 실습 실행 환경의 제약 사항을 안내하는 인자 파서 초기화
    ap = argparse.ArgumentParser(
        description="Day29 · 기존 DB 재사용 / CPU fallback 없음"
    )
    # 외부 DB 연결 없이 로컬 함수 정의만 빠르게 확인하기 위한 점검 플래그 등록
    ap.add_argument(
        "--check",
        action="store_true",
        help="실제 DB/API 없이 순수 함수 TODO 자가 점검 (실제 실습 아님)",
    )
    # 후속 FastAPI 서버 실행 여부를 제어하기 위한 서빙 플래그 등록
    ap.add_argument(
        "--serve", action="store_true", help="실습 08 FastAPI 실행(실제 DB·GPU·LLM)"
    )
    args = ap.parse_args()
    # --check 지정 시 실제 DB 호출을 건너뛰고 tasks 내 공개 함수 목록만 출력 후 조기 종료
    if args.check:
        print(
            "TODO 함수:",
            [
                name
                for name in dir(tasks)
                if not name.startswith("_") and callable(getattr(tasks, name))
            ],
        )
        print("실제 연동은 --check 없이 실행해야 합니다.")
        return
    # 향후 서버 실행 분기 확장용 플래그 보관
    serve = args.serve
    # --check 모드에서 DB 의존성 없이 동작하도록 실제 연동 시점에만 DB 조회 함수를 지연 임포트
    # - fetch_report_status : 특정 보고서의 실제 DB 상태 조회
    from coursekit.db import fetch_report_status

    # 63번 보고서의 실제 DB 상태 조회 결과 출력
    print("[실제 DB]", fetch_report_status(63))
    # 최대 상한(4회)을 초과한 호출(5회)에 대해 False가 반환되는지 경계값 동작 확인
    print("[실행 상한]", tasks.tool_budget_check(5, 4))
    # api_key와 question 등 기밀 필드가 감사 로그에서 정상적으로 마스킹/제거되는지 확인
    print(
        "[마스킹된 로그]",
        tasks.audit_log(
            {
                "event": "tool_call",
                "report_id": 63,
                "api_key": "SHOULD_NOT_LOG",
                "question": "secret",
            }
        ),
    )


# 모듈 임포트 시 의도치 않은 CLI 실행을 방지하기 위해 직접 실행 시에만 진입점 호출
if __name__ == "__main__":
    main()


"""
[설계 평가]
- DB 함수 지연 임포트와 --check 조기 반환으로 외부 인프라 없이도 함수 구조를 즉시 점검 가능
- 실행 상한 초과 테스트(5 > 4)와 기밀 포함 이벤트 마스킹 테스트를 통해 핵심 보안·안정성 정책을 직접 검증
"""
