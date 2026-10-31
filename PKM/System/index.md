현재 파일 절대경로: {{ROOT}}/PKM/System/index.md
과제 루트 기준 상대경로: PKM/System/index.md
최초 작성 주체: ai
최초 작성 모델: gpt-6.1-sol
최초 작성 근거: Codex 실행 세션의 모델 정보
최근 수정 주체: ai
최근 수정 모델: gpt-6.1-sol
최근 수정 근거: Codex 실행 세션의 모델 정보

# System — 설치와 문서 관리 도구

이 폴더는 작업 도구·설치 정보·자동 사건·이전 본문을 보관한다. 실제 task 구현은 Project/에서 수행한다.
일반 사용에 MCP 등록이나 추가 로그인은 필요하지 않다. 현재 제공 Codex의 정상 실행 도구로 Python CLI를 사용하면 된다.

```text
python -B -X utf8 PKM/System/workspace.py --root . check
python -B -X utf8 PKM/System/workspace.py --root . brief
python -B -X utf8 PKM/System/workspace.py --root . new Spec feature-name --body-file Project/spec-draft.txt
python -B -X utf8 PKM/System/workspace.py --root . read PKM/Spec/S001-task.md
python -B -X utf8 PKM/System/workspace.py --root . update PKM/Spec/S001-task.md --body-file Project/spec-draft.txt --expected-sha HASH_FROM_READ
```

root 인자는 실제 루트로 바꾼다. new는 분류별 다음 ID·문서 첫 줄의 현재 절대경로·index 항목을 만든다. update는 읽었던 hash를 확인하고 이전 본문을 History의 .txt로 보존한 뒤 문서/인덱스를 갱신한다.
직접 작성한 새 문서는 첫 줄 경로와 해당 index의 목록을 함께 갱신한다. 각 index의 entries:start/end 사이 목록만 도구가 재생성하며 위 작성 가이드는 유지한다.
폴더 위치가 달라졌으면 `repair-paths`로 운영 Markdown의 경로와 분류 목록을 갱신할 수 있다. 이 명령은 경로 정보만 바꾸며 코드·요구·완료 상태를 추정하지 않는다.

공개 저장소의 Markdown은 설치용 템플릿이어서 경로 토큰을 가진다. install이 대상 환경의 절대경로로 치환하고 check로 미치환 0건을 확인한다.
기존 루트 AGENTS.md가 있으면 원문을 Backups의 .txt로 보존하고 원래 지침 뒤에 작업 공간 지침을 추가한다. 이미 설치된 작업 공간은 재설치로 덮어쓰지 않는다.
기존 제공 파일의 Project 작업 사본과 원본의 대응은 workspace.json에 기록한다. 원본 파일 자체는 삭제·이동하지 않는다. Python 환경·.git·의존성 캐시·도구 설정을 통째로 복사하지 않는다.

## 문서 상단의 경로와 작성 주체 (v1.1)

모든 작성·갱신 Markdown은 아래 8개 항목을 맨 위에 순서대로 적는다. YAML이나 Obsidian 플러그인 없이 읽는 일반 텍스트다.
1. 현재 파일 절대경로: 실제 파일의 절대경로
2. 과제 루트 기준 상대경로: 루트 AGENTS.md가 있는 과제 루트 기준, /로 구분 (예: PKM/Spec/S001-task.md)
3. 최초 작성 주체: ai / human / mixed / unknown
4. 최초 작성 모델: 실제 확인한 모델 ID, 인간이면 not-applicable, 확인 불가면 unknown
5. 최초 작성 근거: 실행 환경에 실제 노출된 모델 정보나 사용자 확인 등 짧은 출처
6. 최근 수정 주체: ai / human / mixed / unknown
7. 최근 수정 모델: 실제 확인한 모델 ID, 인간이면 not-applicable, 확인 불가면 unknown
8. 최근 수정 근거: 실제 확인한 출처

최초 작성 정보는 보존하고 내용 수정자는 최근 수정 항목에 기록한다. 모델명은 기본 설정·브랜드·기억으로 추정하지 않는다. 인간이 작성했음이 확인된 경우에만 human으로 쓴다. 인간과 AI의 공동 작성이 확인되면 mixed와 확인한 모델·기여 근거를 적는다. 기존 원문/복사본의 작성자가 불명확하면 unknown이며 설치한 Agent를 원저자로 기록하지 않는다. 경로만 복사·이동·수정할 때 작성자 정보를 새로 귀속하지 않는다.

도구 new/update의 실행 예: --root 실제루트 --actor ai --model 실제로확인한ID --identity-source 실행환경의모델표시 new Spec 주제 --body-file Project/draft.txt
인간 작성 확인 시 --actor human --identity-source 사용자확인. 미지정 모델은 unknown이다. 이 옵션은 하위 명령(new/update) 앞에 둔다. 직접 편집할 때도 같은 규칙을 지킨다. repair-paths는 주소·누락 헤더를 정리하되 최초/최근 작성자 정보는 보존하며, 없던 정보는 unknown으로 남긴다.
