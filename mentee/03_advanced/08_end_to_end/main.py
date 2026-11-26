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

# 기본 질의, API 계약 변환, FastAPI 앱 빌더, 감사 게이트 함수가 통합된 과제 모듈 임포트
# - tasks : 웹 API 구성 및 에이전트 응답 검증 함수 제공
import tasks

"""CLI 실행 모드에 따라 함수 구조 점검, FastAPI 서버 구동(--serve), 또는 CLI 단건 에이전트 실행·감사를 수행하는 진입점 모듈."""


def main():
    """명령행 옵션을 해석해 구조 점검(--check), API 서버 구동(--serve), 또는 단건 에이전트 실행 흐름을 제어."""
    # 실습 실행 환경의 제약 사항을 안내하는 인자 파서 초기화
    ap = argparse.ArgumentParser(
        description="Day29 · 기존 DB 재사용 / CPU fallback 없음"
    )
    # 외부 DB·GPU·LLM 연결 없이 로컬 함수 정의만 빠르게 확인하기 위한 점검 플래그 등록
    ap.add_argument(
        "--check",
        action="store_true",
        help="실제 DB/API 없이 순수 함수 TODO 자가 점검 (실제 실습 아님)",
    )
    # 단건 CLI 테스트 대신 FastAPI 웹 서버를 띄우기 위한 서빙 플래그 등록
    ap.add_argument(
        "--serve", action="store_true", help="실습 08 FastAPI 실행(실제 DB·GPU·LLM)"
    )
    args = ap.parse_args()
    # --check 지정 시 실제 서버·에이전트 실행을 건너뛰고 tasks 내 공개 함수 목록만 출력 후 조기 종료
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
    # 서버 실행 여부 분기 플래그 보관
    serve = args.serve
    # 기본 테스트 질문 생성
    question = tasks.default_question()
    # --serve 지정 시 로컬 루프백(127.0.0.1:8008)으로 FastAPI 서버를 구동해 외부 노출을 제한
    if serve:
        # 서버 실행 모드에서만 ASGI 서버를 지연 임포트
        # - uvicorn : FastAPI 애플리케이션 실행
        import uvicorn

        uvicorn.run(tasks.make_api(), host="127.0.0.1", port=8008)
    # --serve 미지정 시 단건 에이전트 실행 후 API 응답 계약과 감사 게이트 결과를 CLI로 직접 검증
    else:
        # CLI 단건 실행 모드에서만 에이전트 실행 함수를 지연 임포트
        # - run_agent : 질의에 대한 실제 에이전트 추론 및 Tool 실행 수행
        from coursekit.agent import run_agent

        raw = run_agent(question)
        print("[API]", tasks.api_response(raw))
        print("[Evidence Gate]", tasks.audit_response(raw))


# 모듈 임포트 시 의도치 않은 서버 구동이나 에이전트 실행을 방지하기 위해 직접 실행 시에만 진입점 호출
if __name__ == "__main__":
    main()


"""
[설계 평가]
- --check, --serve, 기본 CLI 실행의 세 가지 모드를 단일 진입점에서 깔끔하게 분기
- 인증 미구현 교육용 API의 외부 접근을 막기 위해 서버 바인딩 호스트를 127.0.0.1로 제한
- uvicorn 및 run_agent의 지연 임포트로 모드별 불필요한 모듈 로딩 방지
"""
