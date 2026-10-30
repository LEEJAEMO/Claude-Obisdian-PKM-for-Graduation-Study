# Shared Task Workspace 0.3.0

**사용자와 AI Agent가 같은 task의 목표·진행·판단·검증 근거를 공유하며 작업하는 정리 체계**다. 과제 내용을 받아 spec을 만들고, 구현하면서 계획·결정·검사·상태를 갱신해 대화가 길어져도 문맥을 이어간다.

이식하는 것은 **작업을 구조화하고 기록을 다시 찾아 이어가는 방식**이다. 특정 분야 지식이나 과제 정답을 옮기지 않는다. 이전 “운영 하네스” 표현은 행동 통제 장치처럼 읽힐 수 있어 0.3부터 공유 작업 공간으로 설명한다.

## 시작

[AGENT_GUIDE.md](AGENT_GUIDE.md)를 제공된 Codex가 명시적으로 읽게 한다. 기존 과제 AGENTS.md와 설정은 그대로 사용한다. Python 3.10 이상, 표준 라이브러리만 필요하다.

```text
git clone --depth 1 --single-branch --branch hackathon-kit-20261030 https://github.com/LEEJAEMO/Claude-Obisdian-PKM-for-Graduation-Study.git agent-workflow
python -B -X utf8 agent-workflow/workflow.py --workspace TASK init
python -B -X utf8 agent-workflow/workflow.py --workspace TASK brief
```

TASK는 이미 존재하는 실제 과제 폴더다. brief는 spec·plan·status·decisions·evidence의 현재 본문 발췌를 함께 반환한다. Agent는 실제 코드와 대조해 “목표 / 완료·진행 / 열린 질문 / 주요 판단 / 다음 행동”을 사용자에게 짧게 설명한다.

## 과제에 남는 것

```text
task/
  실제 구현 코드와 과제 파일
  .agent/
    spec.md                 무엇을 왜 만들지, 확인한 요구와 가정
    plan.md                 어떤 작업으로 풀고 있는지
    status.md               현재까지 한 것·남은 것·다음 행동
    decisions.md            선택과 변경 이유
    evidence.md             실제로 확인한 동작과 근거
    modules.md              이번 task의 반복 절차
    troubleshooting.md      실제 오류와 해결·재검증
    events.jsonl            시간순 중요 변화
    history/                문서 변경 전 본문
    manifest.json           저장 형식 정보
```

기록은 빈 양식으로 시작한다. 작은 task는 spec/status 중심으로 짧게 쓰고 필요할 때 확장한다. 문서가 모두 완성될 때까지 코딩을 기다리게 하는 승인 단계는 없다. [전체 흐름과 이식 범위](WHAT_IS_TRANSFERRED.md), [창작 사용 예시](EXAMPLE.md)를 참고한다.

요구 ID를 작업·코드 위치·검사에서 함께 참조하면 무엇을 어디까지 해결했는지 찾기 쉽다. 요구·설계·구현·검증을 진행하면서 함께 다듬는다. 매 편집마다 모든 문서를 다시 쓰지 않고 중요한 변화 때 관련 기록만 남긴다.

## CLI와 MCP

CLI는 init / brief / state / read / save / log를 제공한다.

```text
python -B -X utf8 agent-workflow/workflow.py --workspace TASK read spec
python -B -X utf8 agent-workflow/workflow.py --workspace TASK save spec --file TASK_SPEC_DRAFT.md --expected-sha HASH_FROM_READ
python -B -X utf8 agent-workflow/workflow.py --workspace TASK log decision "집계와 표시를 나누면 변경 영향을 설명하기 쉬워 이 구조를 선택"
python -B -X utf8 agent-workflow/workflow.py --workspace TASK brief
```

실제 경로/hash로 바꾼다. save는 이전 본문과 변경 사건을 보존한다. 직접 편집도 가능하지만 그 편집의 자동 이력은 생기지 않는다. 저장 충돌·경로·형식 검사와 잠금은 공동 기록의 무결성을 위한 장치다. 다른 구현 도구·명령·일반 파일 편집에 hook을 설치하거나 작업 진행을 막지 않는다.

정상 MCP 등록 기능이 제공되면 같은 기록을 도구 호출로 사용할 수 있다. 기존 안내와 같은 일반 Codex CLI 형식이며 실제 호스트 지원은 별도 확인한다.

```text
codex mcp add task-workflow -- /absolute/python -B -X utf8 /absolute/agent-workflow/server.py --workspace /absolute/task
```

| 도구 | 용도 |
|---|---|
| agent_brief(max_chars=1600) | 목표·계획·상태·결정·검증을 한 번에 읽기 |
| agent_state(limit=10) | 문서 hash와 최근 사건 확인 |
| agent_read(name) | 필요한 한 문서의 본문과 hash 읽기 |
| agent_save(name, content, expected_sha) | 개정 전 내용을 보존하며 기록 갱신 |
| agent_log(kind, summary, evidence) | 중요 변화·판단·오류·검증·재개 사건 추가 |

brief는 현재 발췌이며 추정 요약이나 완료 판정이 아니다. 출처·hash·잘림 표시를 반환하고 중복 요약 파일을 만들지 않는다. 현재 코드와 문서가 맞는지는 Agent가 실제 파일/출력과 대조한다.

실제 구현·검사는 제공된 Codex의 정상 도구로 한다. 이 프로젝트는 명령 실행기나 외부 AI를 추가하지 않는다. 모든 대화를 자동 수집하거나 기록의 진위를 독립 검증하지 않는다. 로컬 기록은 수정 가능한 파일이며 변조 방지 감사 시스템도 아니다.

## 시험 반입과 확인 범위

시험 전 공개 배포본을 고정하고 당일은 다운로드한다. 생성된 task spec·로그·구현·결과물은 외부로 전송/Git push하지 않는다. 제공 AI·Computer Use·후속 서술형 등 실제 시험 안내를 따른다.

MCP 2025-11-25 tools-only stdio 구현이다. 연결이 안 되면 CLI 또는 정상 파일 편집으로 같은 정리 방식을 사용할 수 있다. 자동 전체 수집·실제 Cofa 연결·시험 성과는 보장하지 않는다. 실제 확인 결과는 [VALIDATION.json](VALIDATION.json), 설계 출처는 [SOURCES.md](SOURCES.md)에 남긴다.

```text
python -B -X utf8 -m unittest discover -s agent-workflow/tests -v
```
