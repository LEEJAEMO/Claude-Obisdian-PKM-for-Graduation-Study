# Portable PKM workbench — 0.1.0

Modules, Troubleshooting, Specs를 작은 과제에 필요한 만큼만 가져오는 한국어 작업 보조 묶음이다. 읽기 전용 MCP, 같은 기능의 CLI, Markdown을 제공한다. 12개 카드는 개인 PKM의 범용 절차를 새로 작성한 것이며 완성된 과제나 정답은 포함하지 않는다.

먼저 [START_HERE.md](START_HERE.md)를 읽는다. Python 3.10 이상, 표준 라이브러리만 필요하다. 패키지 설치·API 키·외부 AI 연결이 없다.

## 시험 전 배포와 당일 다운로드

이 배포본은 시험 전에 고정한다. 시험 중 Git push, 문제·파일·결과물 외부 전송, 외부 AI·모델, Claude Code, Computer Use를 사용하지 않는다. 제공된 Codex와 허용된 공개 도구 다운로드만 사용한다. 운영 지시가 우선한다. 이 문서는 보안 설정·차단·업로드 제한을 우회하는 방법을 제공하지 않는다.

```text
git clone --depth 1 --single-branch --branch hackathon-kit-20261030 https://github.com/LEEJAEMO/Claude-Obisdian-PKM-for-Graduation-Study.git portable-pkm
cd portable-pkm
git rev-parse HEAD
python -B -X utf8 kit.py check
python -B -X utf8 -m unittest discover -s tests -v
```

위 다운로드는 실제 응시 환경에서 허용·제공되는 방식일 때 사용한다. 배포 계획에 기록된 고정 commit SHA와 `git rev-parse HEAD`를 대조한다. 불일치하면 임의로 실행하지 말고 공개된 고정 commit의 코드만 사용한다. Git을 사용할 수 없으면 공개 저장소의 고정 commit ZIP 다운로드를 사용한다. 시험 파일을 배포본에 복사하거나 원격에 업로드하지 않는다.

## CLI

```text
python -B -X utf8 kit.py search "요구 stakeholder" --kind module --limit 3
python -B -X utf8 kit.py read M-REQ
python -B -X utf8 kit.py search "CSV Excel" --kind troubleshooting
```

검색은 lexical 방식이며 관련성 정확도를 보장하지 않는다. metadata에 ID·적용 조건·비대상·출처·검증 수준을 반환한다. 선택 ID의 본문만 읽는다. 카드 hash가 달라지거나 경로가 knowledge/ 밖이면 거부한다. 고정 commit은 배포 출처 확인용이며 hash만으로 공급망 신뢰가 생기는 것은 아니다.

## 선택: MCP 연결

이 서버는 MCP `2025-11-25`, tools-only, stdio를 구현한 작은 어댑터다. `pkm_search`, `pkm_read`만 제공하며 네트워크·쓰기·셸 도구는 없다. 공식 SDK가 아니며 모든 MCP 기능을 구현하지 않는다.

시험 환경에서 문서화된 등록 경로가 제공될 때만 사용한다. 일반 Codex CLI 공식 예시를 적용하면 다음 형태다. 실제 Python 실행 파일과 server.py의 절대 경로로 바꾼다.

```text
codex mcp add portable-pkm -- /absolute/path/to/python -B -X utf8 /absolute/path/to/portable-pkm/server.py
```

이 명령은 호스트 설정을 변경한다. 이 저장소는 자동 실행하지 않는다. 공식 설정 파일을 사용하는 환경이라면 아래 항목을 호스트가 허용하는 위치에 추가할 수 있다. 기존 설정을 덮어쓰지 않는다.

```toml
[mcp_servers.portable-pkm]
command = "/absolute/path/to/python"
args = ["-B", "-X", "utf8", "/absolute/path/to/portable-pkm/server.py"]
```

연결 후 `pkm_search(query="요구", kind="module", limit=3)`와 `pkm_read(id="M-REQ")`를 확인한다. 시험 제공 Codex의 등록·프로토콜 지원이 다르면 CLI/Markdown으로 전환한다. 차단 기능을 바꾸거나 우회하지 않는다. 서버를 터미널에서 단독 실행하면 JSON-RPC 입력을 기다리므로 화면 출력이 없는 것이 정상이다.

## 검증 범위

`docs/VALIDATION.json`에 실제 검사 결과를 기록한다. 로컬 Python CLI·JSON-RPC stdio subprocess 시험과 새 경로 복원은 시험 Cofa/Codex 호스트에 연결한 통합 검증과 구분한다. 시험 환경과의 연결은 사전 체험에서 확인해야 한다. 사전 체험의 내용·산출물도 외부로 보내지 않는다.

후속 서술형은 AI·복사/붙여넣기 없이 직접 답한다. [설명 연습](docs/COGNITION-PRACTICE.md)은 시험 전 연습용이다. [설계 출처](docs/SOURCES.md)와 카드의 적용 조건을 함께 확인한다.
