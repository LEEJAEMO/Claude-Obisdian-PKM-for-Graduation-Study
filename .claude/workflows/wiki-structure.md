# Obsidian LLM-wiki 구조 정의

## 전체 흐름

```
세션 시작 → /resume-session → 어제 상태 로드
     ↓
작업 중   → /paper-review / /notes-digest / /lit-search
     ↓
세션 종료 → /save-session → 세션 파일 저장 + /wiki-update 자동 호출
                             ↓
                      Research Log 생성 + wiki-curator 연결 추천
```

## Obsidian Vault 구조 (LLM-wiki 관점)

```
Obsidian Vault/
├── 0. Inbox/Files/               ← 이미지·PDF 첨부 (자동 저장 대상)
├── 0. Template/
│   ├── 1. 학습 템플릿/
│   └── 2. Research 템플릿/       ← Zotero 노트 템플릿
├── 1. Project/대학원 공부/
│   ├── 1. 과목 (subject)/
│   │   └── 강의노트 (Lecture Note)/  ← /notes-digest 출력
│   └── 2. 연구 (Research)/
│       ├── Research Log/         ← /wiki-update 출력 (NEW)
│       │   └── YYYY-MM-DD.md
│       └── Knowledge/            ← 개념 정리 노트
├── 2. Area/
│   └── 2.1 Planner/
│       ├── 2.1.1 Daily Notes/
│       └── 2.1.2 Weekly Notes/
├── 3. Resource/
│   ├── 학부학습/물리학/          ← 교재 MOC (/book-moc 출력)
│   └── Zotero/                  ← @논문키.md (/paper-review 출력)
└── 999. Claude guideline/        ← CLAUDE.md, 가이드라인
```

## Research Log 형식

저장: `1. Project/대학원 공부/2. 연구 (Research)/Research Log/YYYY-MM-DD.md`

```markdown
---
type: research-log
date: YYYY-MM-DD
tags: [research-log, ohe, sic]
session_topics: []
---

### UP:: [[!Research MOC]]

# YYYY-MM-DD 연구 로그

## 오늘 한 작업
## 분석한 논문
## 생성/수정한 노트
## 새로 이해한 개념
## 미해결 질문
## 내일 첫 번째 할 일
```

## !Research MOC 형식

저장: `1. Project/대학원 공부/2. 연구 (Research)/!Research MOC.md`

```markdown
---
type: MOC
tags: [MOC, research, ohe, sic]
---

# Research MOC — OHE in SiC

## 연구 로그

\`\`\`dataview
TABLE WITHOUT ID file.link AS "날짜", session_topics AS "주제"
FROM "1. Project/대학원 공부/2. 연구 (Research)/Research Log"
WHERE type = "research-log"
SORT date DESC
\`\`\`

## 분석한 논문
[[@논문키]] — [상태]

## 핵심 개념 노트
[[개념명]]

## 진행중인 질문
- [ ] 질문
```

## 세션 파일 저장소

경로: `~/.claude/session-data/`
형식: `YYYY-MM-DD-research-session.tmp`
보관: 최신 30개 (오래된 것은 수동 아카이브)

## 노트 연결 규칙 (wiki-curator 기준)

| 새 노트 유형 | 연결 후보 |
|------------|---------|
| 강의노트 | 과목 인덱스, 관련 교재 챕터, Zotero 논문 |
| Zotero 논문 | 관련 개념 노트, 다른 Zotero 논문, Research Log |
| 교재 챕터 | 교재 MOC, 관련 강의노트, Zotero 논문 |
| Research Log | 당일 분석 논문, 생성 노트 |

## 고아 노트 기준

아래 조건 모두 해당 시 고아:
1. 다른 노트에서 `[[이 파일명]]` 언급 없음
2. 이 파일에 `[[wikilink]]` 없음
3. 어떤 MOC의 Dataview 쿼리에도 걸리지 않음
