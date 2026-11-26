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

# Tool 호출 요청 생성·결과 매칭·쌍 검증 기능이 통합된 과제 모듈 임포트
# - tasks : 메시지 생성, 결과 연결, 쌍 무결성 감사 함수 제공
import tasks

"""CLI 실행 모드에 따라 함수 구조 자가 점검 또는 실제 DB 조회 기반 ToolMessage 매칭·감사를 수행하는 진입점 모듈."""


def main():
    """명령행 옵션을 해석해 구조 점검(--check) 또는 실제 DB 조회·메시지 매칭·감사 흐름을 실행."""
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

    # 63번 보고서의 실제 DB 상태를 조회해 Tool 실행 결과로 사용
    raw = fetch_report_status(63)
    # DB 상태 조회 Tool 호출을 모사한 표준 요청 메시지 생성
    call = tasks.make_request("lookup_status", {"report_id": 63}, "call_001")
    # 실제 DB 조회 결과를 원본 호출 ID(call_001)에 연결한 응답 메시지 생성
    message = tasks.match_result(call, raw)
    # 원본 DB 데이터, 생성된 ToolMessage, 요청-응답 쌍 감사 결과를 순차 출력
    print("[DB]", raw)
    print("[Message]", message)
    print("[Audit]", tasks.summarize_pairs([call], [message]))


# 모듈 임포트 시 의도치 않은 CLI 실행을 방지하기 위해 직접 실행 시에만 진입점 호출
if __name__ == "__main__":
    main()


"""
[설계 평가]
- DB 함수 지연 임포트와 --check 조기 반환을 통해 외부 인프라 없이도 함수 구조를 즉시 점검 가능
- 실제 DB 조회 데이터를 기반으로 요청 생성 -> 결과 매칭 -> 무결성 감사로 이어지는 종단 간 검증 흐름 구성
"""
