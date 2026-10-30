# Task Agent Workflow 0.2.0

과제 수행 중 **spec을 직접 만들고 개정하며, 계획·결정·실행 근거·오류·재개 상태를 로컬에 남기는** AI Agent 운영 하네스다. 배포하는 것은 작업 구조와 도구다. 분야별 지식 카드·개인 자료·완성 과제는 포함하지 않는다.

이전 0.1 지식 조회 배포본을 이 구조로 교체했다. 기존 main 브랜치는 유지하고 `hackathon-kit-20261030` 브랜치에서 배포한다.

## 먼저 읽기

[AGENT_GUIDE.md](AGENT_GUIDE.md)를 제공된 Codex에 명시적으로 읽게 한다. 자동 인식·강제 실행되는 hook이 아니다. 기존 과제 AGENTS.md/설정은 보존한다.

Python 3.10 이상, 표준 라이브러리만 필요하다. API 키·pip 설치·외부 AI·웹 서버·DB가 필요 없다. 런타임은 네트워크나 셸을 실행하지 않는다.

```text
git clone --depth 1 --single-branch --branch hackathon-kit-20261030 https://github.com/LEEJAEMO/Claude-Obisdian-PKM-for-Graduation-Study.git agent-workflow
python -B -X utf8 agent-workflow/workflow.py --workspace /absolute/path/to/task init
python -B -X utf8 agent-workflow/workflow.py --workspace /absolute/path/to/task state
```

과제 폴더는 이미 존재해야 한다. Windows도 해당 환경의 실제 절대 경로를 사용한다. 내려받는 도구 폴더와 과제 폴더를 구분한다. Git이 없으면 공개 고정 commit ZIP을 제공되는 방식으로 내려받는다. 고정 SHA는 함께 제공하는 Vault 당일 지침에서 확인한다.

## 과제별로 생성되는 것

```text
task/
  기존 과제 파일과 구현 코드
  .agent/
    manifest.json
    spec.md                 요구·입출력·제약·수용 기준
    plan.md                 수용 기준별 작업과 상태
    decisions.md            선택·대안·이유·코드 위치
    evidence.md             검사 명령·예상·실제·실패/미실행
    troubleshooting.md      실제 실패의 재현·원인·수정·재검증
    modules.md              과제 안에서 반복된 절차만
    status.md               재개 지점과 다음 행동
    events.jsonl            append-only 사건 로그
    history/                문서 변경 전 본문
```

spec은 Agent가 실제 요구를 읽고 작성한다. 사용자가 새 요구를 알려 주면 spec을 개정하고 영향받는 계획·검사도 갱신한다. 처음 생성되는 파일은 빈 구조이며 완료된 작업이나 검증 통과를 뜻하지 않는다.

## CLI로 spec 갱신하기

```text
python -B -X utf8 agent-workflow/workflow.py --workspace TASK read spec
python -B -X utf8 agent-workflow/workflow.py --workspace TASK save spec --file SPEC_DRAFT.md --expected-sha HASH_FROM_READ
python -B -X utf8 agent-workflow/workflow.py --workspace TASK log decision "필수 조회 흐름을 먼저 구현하기로 결정"
python -B -X utf8 agent-workflow/workflow.py --workspace TASK state
```

`TASK`, `SPEC_DRAFT.md`, `HASH_FROM_READ`는 실제 경로·값으로 바꾼다. 초안 파일은 과제 내부에 둔다. save는 현재 hash가 달라지면 거부하며 이전 본문과 변경 로그를 보존한다. 다른 artifact도 같은 방식이다. 같은 내용 저장은 새 변경 이력을 만들지 않는다.

검증 로그는 `log verification SUMMARY --evidence-json JSON` 형태다. evidence의 `status`는 `passed`, `failed`, `not-run` 중 하나여야 한다. command, expected, actual, output_file을 함께 적을 수 있다. 셸별 JSON 인용이 불편하면 MCP를 사용하거나 과제 내부 evidence 문서를 편집·저장한다.

로그는 호출자가 보고한 근거다. 도구가 테스트를 대신 실행하거나 합격을 보증하지 않는다. 수동 편집을 허용하는 로컬 파일이므로 로그도 변조 방지 감사 시스템이 아니다. save가 도중에 실패하면 `artifact_save_started`만 남을 수 있다. 다음 실행에서 실제 hash와 history를 대조하고 자동 성공으로 처리하지 않는다.

## 선택: MCP

초기화한 과제 디렉터리 하나에 서버를 바인딩한다. MCP 도구는 그 디렉터리 `.agent/`만 관리하며 일반 파일 쓰기·명령 실행 도구가 없다.

제공되는 정상 등록 경로가 있을 때만 다음 일반 Codex CLI 형태를 적용한다. 실제 환경에서 등록이 막히면 CLI를 사용하고 제한을 우회하지 않는다.

```text
codex mcp add task-workflow -- /absolute/path/to/python -B -X utf8 /absolute/path/to/agent-workflow/server.py --workspace /absolute/path/to/task
```

| 도구 | 역할 |
|---|---|
| agent_state(limit=10) | 문서 hash와 최근 사건·로그 개수 조회 |
| agent_read(name) | spec/plan/status 등 현재 본문과 hash 조회 |
| agent_save(name, content, expected_sha) | 문서 개정·이전 본문 보존·변경 사건 기록 |
| agent_log(kind, summary, evidence) | 실제 단계·결정·오류·검증·재개 사건 추가 |

MCP `2025-11-25` tools-only stdio 어댑터이며 공식 SDK나 전체 MCP 구현은 아니다. 로컬 프로토콜 시험과 실제 Cofa 호스트 연결은 구분한다. 쓰기 도구 호출이 성공했는지 애매하면 state를 읽고 확인한다. append 호출을 무조건 재시도하면 중복 로그가 생길 수 있다. 기존 writer의 lock을 자동 제거하지 않는다.

## 시험에서의 사용

시험 전에 공개 배포를 고정하고 당일은 다운로드만 한다. 제공된 Codex 안에서만 사용한다. Git push·문제/파일/결과물 외부 전송·별도 AI·Claude Code·Computer Use와 차단 우회는 하지 않는다. 후속 서술형에서는 AI와 복사/붙여넣기 없이 직접 답한다. 사전 체험에서 CLI/MCP 지원을 확인한다.

## 확인

```text
python -B -X utf8 -m unittest discover -s agent-workflow/tests -v
```

현재 실제 검증 결과는 [VALIDATION.json](VALIDATION.json), 도구 사용 예시는 [EXAMPLE.md](EXAMPLE.md), 출처 범위는 [SOURCES.md](SOURCES.md)에 기록한다. 예시는 창작 입력이며 실제 시험 과제·모범답안이 아니다.
