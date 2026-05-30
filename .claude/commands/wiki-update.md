---
description: 현재 세션 내용을 Obsidian Research Log와 관련 노트에 반영. wiki-curator 에이전트가 노트 연결도 추천. 인자 없음.
---

# Wiki 업데이트

세션에서 만들어진 지식을 Obsidian LLM-wiki에 반영하고 노트 간 연결을 추천한다.

## 실행 순서

### Step 1: 워크플로우 매뉴얼 확인

`.claude/workflows/wiki-structure.md` 를 Read 도구로 읽어 저장 경로와 형식 확인.

### Step 2: Research Log 작성

경로: `$HOME\OneDrive\문서\Obsidian Vault\1. Project\대학원 공부\2. 연구 (Research)\Research Log\YYYY-MM-DD.md`

형식:
```markdown
---
type: research-log
date: YYYY-MM-DD
tags: [research-log, ohe, sic]
session_topics: [오늘 다룬 주제 키워드들]
---

### UP:: [[!Research MOC]]

# YYYY-MM-DD 연구 로그

## 오늘 한 작업
[세션 내용 요약]

## 분석한 논문
- [[@논문키]] — [핵심 결론 한 줄]

## 생성/수정한 노트
- [[노트명]] — [변경 내용]

## 새로 이해한 개념
- **[개념]**: [설명]

## 미해결 질문
- [ ] [질문]

## 내일 첫 번째 할 일
[구체적으로]
```

### Step 3: wiki-curator 에이전트 호출

에이전트에게 전달:
1. 오늘 생성/수정한 노트 경로 목록
2. 오늘 새로 이해한 개념들
3. "이 노트들과 연결할 수 있는 기존 노트를 찾아서 [[wikilink]] 추가를 추천해줘"

### Step 4: 업데이트 결과 보고

```
Wiki 업데이트 완료:
- Research Log: [경로]
- 연결 추천: [N]개 (wiki-curator 결과)
- 업데이트된 노트: [목록]
```
