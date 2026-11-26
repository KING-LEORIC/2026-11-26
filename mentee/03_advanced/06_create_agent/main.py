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

# 복합 질의 생성, 에이전트 빌더, 메시지 감사 함수가 통합된 과제 모듈 임포트
# - tasks : 질문 생성, 에이전트 초기화, Tool 호출 집계 및 최종 응답 추출 함수 제공
import tasks

"""CLI 실행 모드에 따라 함수 구조 자가 점검 또는 실제 LLM·Tool 2종 기반 에이전트 실행 및 응답 감사를 수행하는 진입점 모듈."""


def main():
    """명령행 옵션을 해석해 구조 점검(--check) 또는 에이전트 생성·실행·메시지 감사 흐름을 실행."""
    # 실습 실행 환경의 제약 사항을 안내하는 인자 파서 초기화
    ap = argparse.ArgumentParser(
        description="Day29 · 기존 DB 재사용 / CPU fallback 없음"
    )
    # 외부 DB·LLM 연결 없이 로컬 함수 정의만 빠르게 확인하기 위한 점검 플래그 등록
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
    # --check 지정 시 실제 LLM·DB 호출을 건너뛰고 tasks 내 공개 함수 목록만 출력 후 조기 종료
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
    # 63번 보고서 대상 복합 질의(내용 검색 + 상태 조회) 생성
    question = tasks.question_for_agent(63)
    # 실제 Tool 2종과 호출 상한 미들웨어가 설정된 에이전트 인스턴스 생성
    agent = tasks.make_agent()
    # 그래프 재귀 상한(recursion_limit=20)을 명시해 비정상 순환 시 안전하게 중단되도록 실행
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit": 20},
    )
    # 모델의 Tool 요청 횟수와 실제 ToolMessage 반환 횟수 요약 출력
    print("[Tool Call]", tasks.summarize_tool_messages(result["messages"]))
    # 중간 Tool 메시지를 제외한 최종 AIMessage 답변 본문 출력
    print("[최종 메시지]", tasks.final_text(result["messages"]))


# 모듈 임포트 시 의도치 않은 CLI 실행을 방지하기 위해 직접 실행 시에만 진입점 호출
if __name__ == "__main__":
    main()


"""
[설계 평가]
- --check 조기 반환으로 LLM API 키나 DB 연결 없이도 함수 시그니처 구조 점검 가능
- 에이전트 미들웨어 상한과 별개로 그래프 수준의 recursion_limit(20)을 이중 안전장치로 적용
"""
