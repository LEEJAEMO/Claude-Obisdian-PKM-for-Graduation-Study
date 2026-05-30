---
description: DOI / arXiv ID / 논문 제목으로 Zotero 라이브러리에 자동 추가하고 Obsidian 논문 노트를 생성. my_context 입력 필수. 인자: DOI, arXiv ID, 또는 제목.
---

# Zotero 논문 추가

새 논문을 Zotero 라이브러리에 추가하고 `6. Papers/` 폴더에 Vault 유지보수 매뉴얼 §1.1 스키마를 따르는 노트를 생성한다.

> **단일 진실의 원천**: 논문 frontmatter 스키마는 항상 `Obsidian Vault/999. Claude guideline/Vault 유지보수 매뉴얼.md` §1.1을 따른다. 이 명령은 그 스키마를 강제한다.

## Zotero 스크립트 세트 — 언제 뭘 쓰는가

| 도구 | 범위 | 언제 |
|------|------|------|
| **`/zotero-add`** (이 명령) | 신규 1건 등록 | 새 논문을 처음 추가할 때 |
| **`zotero_pin_latest.py`** (프로젝트 루트) | 최근 1건 citekey pin | `/zotero-add` 직후 또는 Zotero 데스크톱으로 수동 추가 직후 |
| **`update_all_citekeys.py`** (프로젝트 루트) | 전체 일괄 재명명 | BBT 설정 변경·대규모 라이브러리 재구성 후 (매뉴얼 §7 "파일명 수동 변경 금지") |

⚠️ **세 도구 모두 실행 전 Zotero 데스크톱을 닫을 것** — SQLite 충돌 방지.

---

## 사전 조건

- `ZOTERO_LIBRARY_ID`와 `ZOTERO_API_KEY`가 `.claude/settings.json`에 설정되어 있어야 함
- 설정되지 않았으면 즉시 알리고 중단
- Zotero 데스크톱이 닫혀 있어야 함 (pin 단계에서 SQLite 직접 접근)

---

## 실행 순서

### Step 0: my_context 확인 (생략 불가)

Vault 유지보수 매뉴얼 §2 "진입 의례"는 논문 임포트 시 **`my_context` 한 줄 작성을 필수**로 규정한다. 이 명령은 그 규칙을 강제한다.

**사용자 입력값에 `--context` 플래그가 포함되어 있는지 확인:**

```
/zotero-add 10.1038/... --context "Advisor가 세미나에서 언급한 논문"
/zotero-add 2501.12345 --context "Fukami 2025와 비교군"
/zotero-add "title" --context "기억 안 남"
```

**플래그가 없으면 작업 중단하고 사용자에게 한 줄을 요청:**

> "이 논문을 왜 저장하나요? 짧게 한 줄 주세요 (예: '세미나 언급', '리뷰에서 인용됨', '비교군'). 정말 기억 안 나면 '기억 안 남'이라고 쓰면 됩니다 — 그 자체가 신호입니다."

**빈 값은 허용하지 않는다.** `"기억 안 남"`, `"미상"` 같은 명시적 표식이라도 받는다.

### Step 1: 메타데이터 수집

`paper-lookup` 스킬로 입력값(DOI / arXiv ID / 제목)에서 메타데이터 수집:
- 제목, 저자(성·이름 분리), 저널, 연도, 권호, 페이지, DOI, abstract

arXiv ID면 `https://arxiv.org/abs/{id}` WebFetch 병행.

### Step 2: 중복 확인

`pyzotero` 스킬로 기존 라이브러리 검색:

```python
from pyzotero import Zotero
import os

zot = Zotero(os.environ['ZOTERO_LIBRARY_ID'], 'user', os.environ['ZOTERO_API_KEY'])
results = zot.items(q=doi_or_title, limit=5)
```

이미 존재하면 → 기존 citekey 확인 후 Obsidian 노트 없으면 Step 4로 건너뜀. (기존 노트에는 my_context를 덮어쓰지 않음; 사용자가 채울 수 있도록 안내만)

### Step 3: Zotero에 추가

```python
template = zot.item_template('journalArticle')
template['title'] = title
template['DOI'] = doi
template['abstractNote'] = abstract
template['publicationTitle'] = journal
template['volume'] = volume
template['issue'] = issue
template['pages'] = pages
template['date'] = year
template['creators'] = [
    {'creatorType': 'author', 'firstName': fn, 'lastName': ln}
    for fn, ln in authors
]
zot.create_items([template])
```

### Step 3.5: citekey pin (BBT 형식 확정)

API로 추가한 직후 citekey는 BBT 형식으로 pin되지 않은 상태일 수 있다. 프로젝트 루트의 `zotero_pin_latest.py`를 실행해 최신 항목의 citekey를 `AuthorEtAlYearJournalAbbrev` 형식으로 pin:

```bash
python "$PROJECT_ROOT/zotero_pin_latest.py"
```

실행 후 pin된 citekey를 확인해 Step 4의 파일명·frontmatter `citekey` 필드에 사용.

> **citekey 형식**: `{Author}EtAl{Year}{JournalAbbrev}` (예: `UrazhdinEtAl2026NatNano`).
> 단독 저자: `{Author}{Year}{JournalAbbrev}` (예: `Ando2025JPSJ`).
> JournalAbbrev는 `zotero_pin_latest.py`의 `JOURNAL_MAP`을 참조.

### Step 4: Obsidian 노트 생성

**경로** (매뉴얼 §1.1 준수):
```
$HOME\OneDrive\문서\Obsidian Vault\1. Project\대학원 공부\2. 연구 (Research)\6. Papers\@{citekey}_{First six words of title}.md
```

이미 존재하면 건너뜀 (덮어쓰지 않음).

**frontmatter는 반드시 Vault 매뉴얼 §1.1 스키마 전부 포함**:

```markdown
---
aliases:
  - "{논문 제목}"
type: zotero
tags:
  - zotero
citekey: "{citekey}"
created: "YYYY-MM-DD"
status: unread
importance: 3
relevance: indirect
topic: []
key_claim: "{AI 자동 — abstract 기반 1~2문장}"
my_context: "{Step 0에서 사용자가 입력한 한 줄 — 절대 빈 값 금지}"
my_take: ""
---

%%
## 색상 범례
🟡 Yellow  — Entire Key (전반적으로 중요한 내용)
🔴 Red     — 핵심 주장 / 결론
🟢 Green   — 이론적 설명
🔵 Blue    — 의문점 / 아직 밝혀지지 않은 점
🟣 Purple  — 실험 / 방법 / 재료
🩷 Pink    — 모르는 영단어 (Magenta)
🟠 Orange  — 섹션 구분 (접속사)
⬛ Gray    — 섹션 제목 → heading으로 자동 변환

## relevance 선택
direct      — 내 연구(OHE in SiC)와 직접 연관
indirect    — 간접적으로 연관 (배경지식, 인접 분야)
background  — 기초 개념 / 리뷰 논문

## status 선택
unread / reading / read

## Claude 요청 방법
- 읽기 전: /paper-scan @{citekey}
- 읽은 후: /paper-review @{citekey}
%%

---

# Overview

> [!Cite]

{authors_formatted}, "{title}", _{journal}_, {year}. doi: [{doi}](https://doi.org/{doi}).

> [!md]
> **Title**:: {title}
> **Year**:: {year}
> **Citekey**:: @{citekey}
> **Journal**:: _{journal}_
> **DOI**:: {doi}

> [!Abstract]
>
> {abstract}

---

# 📋 읽기 전 분석

%% begin pre-reading %%
(비어있음 — `/paper-scan`으로 채움)
%% end pre-reading %%

---

# 📝 읽은 후 분석

%% begin post-reading %%
(비어있음 — `/paper-review`로 채움)
%% end post-reading %%

---

# Notes

%% begin notes %%

%% end notes %%

---

# Annotations

%% begin annotations %%
(Zotero Integration 플러그인이 재임포트 시 채움)
%% end annotations %%
```

**필드 초기값**:
- `importance: 3` (기본값, 사용자 재조정)
- `relevance: indirect` (기본값, `/paper-scan` 또는 사용자 재조정)
- `topic: []` (빈 배열, `/paper-scan`으로 제안→사용자 승인)
- `key_claim`: AI가 abstract 기반 1~2문장으로 자동 채움
- `my_context`: **Step 0에서 받은 값 그대로** (매뉴얼 §1.1 필수)
- `my_take: ""` (읽은 후 사용자가 채움)

### Step 5: 결과 보고

```
Zotero 추가 완료:
- 논문: {title}
- Citekey: @{citekey}
- 경로: 6. Papers/@{citekey}_{title stem}.md
- my_context: "{사용자 입력값}"
- Zotero: [추가됨 / 이미 존재]
- Obsidian 노트: [생성됨 / 이미 존재]

다음 단계:
  /paper-scan @{citekey}             — 읽기 전 사전 분석
  Zotero 데스크톱 재실행 + Integration 재임포트  — PDF 하이라이트 연동
  /paper-review @{citekey}           — 읽은 후 Synth callout 완성
```

---

## 관련 스킬·도구

- `paper-lookup` — DOI/제목으로 메타데이터 수집
- `pyzotero` — Zotero Web API 연동
- `citation-management` — BibTeX 생성 (필요 시)
- `zotero_pin_latest.py` — 단건 citekey pin (Step 3.5에서 호출)
- `update_all_citekeys.py` — 전체 재명명 (별도, 라이브러리 재구성 시에만)

## 금기 사항

- **`my_context` 빈 값 금지** (매뉴얼 §1.1 필수 필드)
- **`Obsidian Vault\Zotero\` 경로에 저장 금지** — 실제 경로는 `6. Papers/`
- **파일명 수동 편집 금지** — `update_all_citekeys.py`만 사용 (매뉴얼 §7)
