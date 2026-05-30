---
description: 녹취록 TXT + 강의 PDF + 메모 3가지를 합쳐 Obsidian 강의노트 작성. 인자 형식: --transcript <path> --pdf <path> [--pdf2 <path>] [--memo <텍스트 또는 파일경로>]
---

**워크플로우 매뉴얼 먼저 읽기**: `.claude/workflows/lecture-note.md`
**깊이·언어 정책 정본 같이 읽기**: PKM 모듈 `M-001_lecture-note-routine.md` ( `<Vault>/999. Claude guideline/1. Claude PKM/11. Modules/` )

> 두 문서는 단일 정본 (M-001) ↔ 운영 절차 (workflow) 의 관계. M-001 § 깊이 가이드라인 / § 언어·표기 정책이 노트 품질을 결정.

강의노트 작성 요청: $ARGUMENTS

---

## 실행 순서

### Step 0: 입력 파싱

인자에서 다음을 추출:
- `--transcript <path>` — 녹취록 TXT (lecture-transcribe 출력물)
- `--pdf <path>` — 강의 PDF (슬라이드 원본, 1회차)
- `--pdf2 <path>` — 두 번째 PDF (선택, 2회차 등 강의가 복수 PDF에 걸쳐 있을 때)
- `--memo <텍스트 또는 경로>` — 사용자 메모/필기 (생략 가능)

> [!warning] 경로 주의
> 출력 경로는 항상 `문서`(한국어) 폴더 사용. `文書`(일본어)에 저장하면 Obsidian에서 보이지 않음.

**인자 없이 경로만 넘어온 경우**: 확장자로 자동 판별 (.txt → transcript, .pdf → pdf)

**누락된 입력이 있으면**: 작업을 시작하기 전에 사용자에게 확인 요청.
단, `--memo`는 없어도 진행 가능.

**한 강의가 복수 PDF에 걸쳐 있는 경우**:
- 예: 1주차 중반(제1회 PDF p.18~) + 2주차 중반(제2회 PDF p.~21)
- `--pdf`와 `--pdf2` 각각의 페이지 범위를 녹취록 타임스탬프로 추정
- 이미지 접두어를 구별: `{과목}_W{주차}_1R_p{##}`, `{과목}_W{주차}_2R_p{##}`
- 각 PDF에서 해당 범위 페이지만 추출 (전체 추출 후 불필요 파일 삭제보다, 범위 지정 추출 선호)

### Step 1: 워크플로우 매뉴얼 확인

`.claude/workflows/lecture-note.md`를 Read로 읽어:
- 과목 목록 + subject 필드값 확인
- 이미지 접두어 규칙 확인
- 출력 경로 확인

### Step 2: 과목 정보 파악

파일명 또는 녹취록 첫 줄에서:
- 날짜 (YYYY-MM-DD)
- 과목명 → subject 필드값
- 주차 번호
- 교수명

불명확하면 사용자에게 확인.

### Step 2.5: 이전 주차 강의노트 참조 (2주차 이상일 때)

**2주차 이상인 경우 반드시 실행**:

1. 같은 subject의 이전 주차 강의노트를 Glob/Read로 찾기:
   ```
   강의노트 (Lecture Note)/*{subject}*{이전주차}*.md
   ```
2. 이전 주차 노트의 **마지막 섹션** (어디까지 다뤘는지)을 확인
3. **이전 주차에서 이미 다룬 내용이라도, 교수가 실제로 설명했으면 기록한다**
   - 단, 해당 섹션/항목에 `[복습]` 표시를 붙여 이전 주차 내용과 구분
   - 교수가 **새롭게 보충한 코멘트**는 `[신규]` 표시 또는 별도 표시 없이 본문으로
   - **"이전 주차니까 생략"이라는 임의 판단을 하지 않는다** — 55분짜리 복습도 해당 주차 강의의 일부
4. 녹취록에서 **신규 내용이 시작되는 지점**을 파악하고, 그 이후는 `[복습]` 표시 없이 상세 기술
5. 새 노트의 `prev_lecture` 필드에 이전 주차 노트 링크 설정
6. **이전 주차 노트의 `next_lecture` 필드도 반드시 갱신** (빈 문자열 → 새 노트 링크)

> [!important] 핵심 원칙
> **녹취록이 1차 소스, PDF는 보조.** PDF 교재는 여러 주차에 걸쳐 사용되므로, 이전 주차에서 다룬 PDF 범위는 제외하고 **이번 주차에 새로 다룬 범위만** 강의노트에 포함한다.

### Step 3: PDF 이미지 추출 (PDF가 있으면 항상 실행)

**PDF가 있으면 무조건 이미지 추출한다. 생략하지 않는다.**

**단일 PDF인 경우** — 아래 코드를 Bash로 실행:

```python
import pypdfium2 as pdfium, os, sys

pdf_path = r"[PDF 경로]"
out_dir  = r"$VAULT/0. Inbox/Files"
prefix   = "[이미지 접두어]"  # 예: EC_W2_p

pdf = pdfium.PdfDocument(pdf_path)
for i, page in enumerate(pdf):
    bitmap   = page.render(scale=2)
    pil_img  = bitmap.to_pil()
    out_path = f"{out_dir}/{prefix}{i+1:02d}.png"
    pil_img.save(out_path)
    print(f"saved: {out_path}")
print(f"DONE: {len(pdf)} pages")
```

**복수 PDF인 경우** (한 강의가 두 파일에 걸쳐 있을 때):
- 녹취록 타임스탬프를 기준으로 각 PDF의 관련 페이지 범위를 먼저 파악
- 각 파일에서 해당 범위 페이지만 추출 (0-index: `start_page`~`end_page` 포함)
- 이미지 접두어를 구별: `{과목}_W{주차}_1R_p{##}` / `{과목}_W{주차}_2R_p{##}`

```python
import pypdfium2 as pdfium, os

# ── 제1회 PDF (예: p.18~43 → 0-index 17~42) ──
pdf1_path   = r"[제1회 PDF 경로]"
pdf1_start  = 17   # 0-index 시작 페이지
pdf1_end    = 42   # 0-index 끝 페이지 (포함)
prefix1     = "EC_W2_1R_p"
out_dir     = r"$VAULT/0. Inbox/Files"

pdf1 = pdfium.PdfDocument(pdf1_path)
for i in range(pdf1_start, pdf1_end + 1):
    bitmap  = pdf1[i].render(scale=2)
    pil_img = bitmap.to_pil()
    page_num = i + 1  # 1-index 표시용
    pil_img.save(f"{out_dir}/{prefix1}{page_num:02d}.png")
    print(f"saved: {prefix1}{page_num:02d}.png")

# ── 제2회 PDF (예: p.01~21 → 0-index 0~20) ──
pdf2_path   = r"[제2회 PDF 경로]"
pdf2_start  = 0
pdf2_end    = 20
prefix2     = "EC_W2_2R_p"

pdf2 = pdfium.PdfDocument(pdf2_path)
for i in range(pdf2_start, pdf2_end + 1):
    bitmap  = pdf2[i].render(scale=2)
    pil_img = bitmap.to_pil()
    page_num = i + 1
    pil_img.save(f"{out_dir}/{prefix2}{page_num:02d}.png")
    print(f"saved: {prefix2}{page_num:02d}.png")
```

- 명령어: `python` (Windows 환경, `python3` 아님)
- 패키지가 없으면: `pip install pypdfium2` 후 재실행
- 추출 후 총 페이지 수와 저장 경로 확인

### Step 4: 녹취록 + PDF + 메모 내용 파악

- **녹취록 TXT**: `【スライド N】` 헤더 기준으로 슬라이드별 발화 내용 분리. 타임스탬프 [MM:SS]는 참고용이며 노트에 포함하지 않음.
- **PDF 페이지**: 슬라이드 N ↔ PDF 페이지 N 대응. 중요 다이어그램/그래프 슬라이드를 파악.
- **메모**: 사용자가 특별히 표시한 내용, 질문, 강조점 반영.

**Depth 원칙** (transcript 시간 비중 → 노트 depth):
- 각 슬라이드/섹션의 발화 세그먼트 수 또는 타임스탬프 구간 길이를 확인
- 교수가 오래 설명한 섹션(긴 타임스탬프 구간, 많은 세그먼트)은 노트 depth를 높임:
  - 유도 과정 단계별 명시 (결론만 쓰지 않기)
  - 물리적 직관/해석 추가
  - 필요 시 수식 중간 단계 포함
- 빠르게 지나간 슬라이드는 1~2문장 요약으로 충분

**Q&A 캡처**:
- 강의 중 학생 질문 또는 교수 자체 질문이 있으면 반드시 노트에 포함
- 녹취록에서 질문-답변 패턴 또는 `학생:` / `先生:` 형식을 탐지
- 노트의 `## Q&A` 섹션에 질문(들여쓰기 없이) + 답변(> 인용 블록)으로 작성

### Step 5: note-organizer 에이전트 호출

> [!important] 깊이·언어 정책의 명시적 전달 필수
> 에이전트는 본 명령의 instruction 만 받음. M-001 의 § 깊이 가이드라인 / § 언어·표기 정책을 **prompt 에 직접 풀어 적거나 M-001 파일 경로를 명시적으로 Read 지시**할 것. 그렇지 않으면 5/7 노트 같은 깊이가 안 나옴.

아래를 에이전트에 전달:

1. **입력 자료 절대 경로**:
   - 녹취록 TXT 경로 (필수)
   - PDF 경로 (있을 때) + 페이지 범위
   - 사용자 메모 (있을 때)

2. **과목 메타**: 과목명, 날짜, 주차, 교수명, subject 필드값, 이미지 접두어

3. **참조 문서 Read 지시**:
   - `<Vault>/999. Claude guideline/1. Claude PKM/11. Modules/M-001_lecture-note-routine.md` § 깊이 가이드라인 / § 언어·표기 정책 / § 좋은 노트의 표준 예시
   - 좋은 노트 예시: `2026-04-30 ID 4주차 (Professor A).md` §III-3-A (b)(c)(g), `2026-05-07 ID 5주차 (Professor A).md` §(b)(f)(g) 와 §III-3-B (d) — 이 두 노트의 핵심 섹션을 깊이 표준으로 삼아 새 노트의 깊이를 맞춤

4. **깊이 패턴 7종 명시** (M-001 에서 발췌):
   - 패턴 1: n단계 분해 유도 (수식·알고리즘이 있는 섹션)
   - 패턴 2: "왜 이 형태인가" 동기 설명
   - 패턴 3: 비교 표 + 콜아웃
   - 패턴 4: 콜아웃 4종 용법 (info / important / warning / note)
   - 패턴 5: 강의 인용 형식 (한국어 의역 + 정확한 타임스탬프)
   - 패턴 6: 다음 섹션 연결 인용
   - 패턴 7: 시각적 anchor (슬라이드 이미지 위치)

5. **언어 정책**:
   - **한자 학술 용어 사용 금지** (M-001 매핑 표 참조). 본문 한자 0건 목표.
   - 한자 보존 영역: frontmatter 의 `lecture_material` / `prev_lecture` wikilink (실제 파일명) — display alias 로 한국어 표시.
   - 인용문은 한국어 의역. 일본어 직역체 ("~입니다", "~하지요") 다듬기.
   - 인명 한국어 음역 (Professor A → Professor A).

6. **분량 가이드**:
   - 60분 → 600~900줄, 90분 → 1100~1500줄, 120분 → 1500~2000줄
   - 핵심 섹션 1개당 80~150줄

7. **이미지·삽입 규칙**:
   - 주요 다이어그램: `![[접두어_p##.png|560]]` + 한국어 캡션
   - 텍스트 전용 슬라이드 (표지/목차/참고문헌): 생략
   - 삽입 위치: 해당 섹션 설명 텍스트 **앞**

8. **frontmatter 스키마**: workflow `lecture-note.md` § 3단계 참조

9. **사용자 메모 처리**: 강조점은 `> [!note]` 또는 `## 미해결` 섹션에 반영

10. **Q&A 캡처**: 강의 중 학생 질문이나 교수 자체 질문이 있으면 `## Q&A` 섹션 (질문 + `>` 답변 블록) 필수

11. **저장 경로**: `$VAULT/1. Project/대학원 공부/1. 과목 (subject)/강의노트 (Lecture Note)/` (다른 경로 절대 금지 — `OneDrive/문서/` 또는 `文書` 사용 금지)

12. **완료 후 보고 형식 (필수)**:
    - 최종 줄 수
    - 한자 본문 잔존 개수 (목표 0)
    - 핵심 섹션별 분량 (예: §(b) 100줄, §(f) 130줄)
    - 추가된 콜아웃 / 강의 인용 개수
    - 사용한 깊이 패턴 (7종 중 어느 것을 어디에)

### Step 6: 저장 확인

파일이 올바른 경로에 저장되었는지 확인:
```
$VAULT\1. Project\대학원 공부\1. 과목 (subject)\강의노트 (Lecture Note)\YYYY-MM-DD {약칭} {주차}주차 ({교수성}).md
```

완료 후 보고:
```
강의노트 저장 완료:
- 파일: [경로]
- 슬라이드: N개 | 이미지 삽입: M장
- 메모 반영: [있음/없음]
- 이전 주차: [참조한 노트명 또는 "없음(1주차)"]
- prev/next 링크: [설정 완료 / 해당 없음]
```

### Step 7: prev/next 링크 갱신

새 노트 생성 후:
1. 이전 주차 노트의 `next_lecture` 필드를 새 노트 링크로 갱신
2. 이전 주차 노트 본문의 네비게이션 영역에 `다음 주차 →` 링크 추가 (없었으면)
3. 새 노트의 `prev_lecture` 필드와 본문 네비게이션 `← 이전 주차` 확인

---

## 호출 예시

```
/notes-digest --transcript "C:/경로/2026-04-15 전기전도2 녹취록.txt" --pdf "C:/경로/전기전도2_lecture.pdf" --memo "슬라이드 12의 산란 진폭 공식 이해 안 됨"
```

PDF 없이 녹취록만:
```
/notes-digest --transcript "C:/경로/녹취록.txt"
```
→ 이미지 없이 텍스트 노트만 작성 (Step 3 건너뜀)
