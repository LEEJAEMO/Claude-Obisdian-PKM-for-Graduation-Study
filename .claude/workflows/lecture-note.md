# 강의노트 작성 워크플로우

> [!important] 깊이·언어 정책의 정본
> 본 워크플로우의 **깊이 가이드라인 / 언어·표기 정책 / 좋은 노트 예시**는 PKM 모듈 **M-001** 가 정본:
> `<Vault>/999. Claude guideline/1. Claude PKM/11. Modules/M-001_lecture-note-routine.md`
>
> 본 워크플로우는 운영 절차(경로, PDF 추출 코드, 과목 표) 만 다루고, 노트 내용의 깊이·표기는 M-001 § 깊이 가이드라인 / § 언어·표기 정책을 따른다.

## 저장 경로

> [!warning] 경로 주의
> Vault는 OneDrive 내 `문서`(한국어) 폴더가 아니라 **Desktop** 아래에 있음.
> 올바른 경로: `$VAULT/`

완성 노트: `$VAULT/1. Project/대학원 공부/1. 과목 (subject)/강의노트 (Lecture Note)/`
이미지: `$VAULT/0. Inbox/Files/`

코드에서 경로 지정 시 반드시 아래 형식 사용 (슬래시 방향 포함):
```python
out_dir = r'$VAULT/0. Inbox/Files'
note_dir = r'$VAULT/1. Project/대학원 공부/1. 과목 (subject)/강의노트 (Lecture Note)'
```

## 1단계: 입력 처리

| 입력 형태 | 처리 방법 |
|----------|---------|
| PDF 강의자료 | `pdf` 스킬로 읽기 → `Skill("pdf")` |
| 이미지 파일 (PNG/JPG 슬라이드) | Read 도구로 시각적 읽기 |
| 직접 붙여넣은 텍스트 필기 | 그대로 처리 |
| **TXT 녹취록** (Zoom/録画 MP4에서 생성) | Read 도구로 읽기 → `lecture-transcribe` 워크플로우 출력물 |

PDF 처리 시 `pdf` 스킬 우선 사용. 스킬 없으면 pypdfium2 코드로 PNG 변환 후 Read.

### TXT 녹취록 입력 시 추가 처리

`lecture-transcribe` 워크플로우로 생성된 녹취록 TXT를 입력받을 경우:
- `【スライド N】` 헤더를 섹션 구분으로 활용
- 타임스탬프 `[MM:SS]`는 인용 정확성용 — 본문 텍스트엔 노출 안 하되 **교수 인용에는 반드시 병기** (M-001 § 패턴 5)
- 슬라이드 번호와 PDF 슬라이드를 대조해 내용 보완 (PDF가 있으면 이미지 삽입)
- 녹취록만 있고 PDF 없으면 텍스트 노트만 작성 (이미지 생략)

**Depth 원칙**: M-001 § 깊이 가이드라인 참조. 핵심 요점:
- 핵심 수식/알고리즘 유도가 있는 섹션은 **n단계 분해 패턴** 적용 (결론 박스만 던지지 말 것)
- 결론 식 후에 **식의 의미 분해** (각 항이 뭘 의미하는지) 별도 추가
- 콜아웃 4종 (info/important/warning/note) 적극 활용
- "왜 이 형태인가" 동기를 결론 직전에 1~2문장
- 강의 인용은 자연스러운 한국어 의역 + 정확한 타임스탬프

**분량 기준** (M-001 § 분량 기준):
- 60분 강의: 600~900줄
- 90분 강의: 1100~1500줄
- 120분 강의: 1500~2000줄
- 핵심 섹션 1개당 80~150줄

**Q&A 캡처**: 강의 중 학생 질문이나 교수 자체 Q&A가 있으면 `## Q&A` 섹션에 반드시 포함. (생략 금지)

**복수 PDF 강의**: 한 강의가 여러 회차 PDF에 걸쳐 있을 수 있음.
- 이미지 접두어로 회차 구별: `{과목}_W{주차}_1R_p{##}`, `{과목}_W{주차}_2R_p{##}`
- 각 PDF에서 해당 강의에 속하는 페이지 범위만 추출 (녹취록 타임스탬프로 범위 추정)

## 2단계: 과목 정보 확인

작업 전 반드시 확인:
- 과목명 (subject 필드에 정확히 일치해야 Dataview 동작)
- 주차 번호
- 담당교수

### 현재 수강 과목 (2026 봄학기)
| subject 값 (정확히) | 과목명 | 약칭 | 교수 | 이미지 접두어 |
|--------------------|--------|------|------|-------------|
| `반도체공학특론` | 반도체공학특론 | SC | Professor B / Professor F | `SC_W{주차}_p{##}` |
| `전기전도` | 전기전도 | EC | Professor C 계열 | `EC_W{주차}_p{##}` |
| `MicroFabrication` | MicroFabrication | MF26 | Professor C / Professor D | `MF26_p{##}` |
| `양자론전자공학` | 양자론전자공학 | QE | — | `QE_W{주차}_p{##}` |
| `지능적디자인공학` | 지능적디자인공학 | ID | Professor A 타카시 | `ID_W{주차}_p{##}` |
| `융합광,전자과학의전망` | 융합광전자과학의전망 | OP | — | `OP_W{주차}_p{##}` |
| `광양자정보과학의 기초` | 광양자정보과학의 기초 | QO | Professor E 미츠루 | `QO_W{주차}_p{##}` |

(인명은 한국어 음역. 본문에서는 한국어 표기 사용. frontmatter 의 `prev_lecture` wikilink 만 실제 파일명 한자 보존)

## 3단계: 출력 형식 (Obsidian Frontmatter + 구조)

파일명: `YYYY-MM-DD {과목약칭} {주차}주차 ({교수성_원래표기}).md`
예: `2026-04-30 ID 4주차 (Professor A).md` (파일명의 인명 한자는 검색 호환을 위해 일관 유지)

```markdown
---
type: lecture-note
subject: [subject 값 — 위 표에서 정확히]
date: YYYY-MM-DD
week: [주차 번호]
note_method: claude
lecture_material: "<강의자료 파일명> (pp.X~Y)"
recording: "<녹화 파일명> (~분)"
reviewed: false
notices: false
aliases:
  - <한국어 약식 별칭>
tags:
  - lecture-note
  - <과목 태그>
  - <도메인 태그 한국어로>
prev_lecture: "[[이전 주차 노트 링크]]"
next_lecture: ""
---

> [!info] 참고 교재
> - [PDF 페이지 범위] 등 메타 정보

### UP:: [[과목별 강의노트 목록]]

# [과목 한국어명] — [주차]주차 (YYYY-MM-DD)

> [[이전 주차 노트|← 이전 주차 (교수 한국어)]]  |  [[다음 주차 노트|다음 주차 →]]

> [!info] 강의 정보
> - 과목 / 담당 / 강의 자료 / 범위 / 녹취록 / 레포트 마감 등

---

## TL;DR
[2~3문단 핵심 정리]

> [!important] 핵심 결론
> [한 줄 결론 2~4개]

---

## 목차
[섹션별 링크]

---

## [본문 — n단계 분해 + 의미 분해 + 콜아웃 + 인용]

## Q&A
[학생 질문 + 교수 답변]

## 미해결 / 추가 조사 필요
- [ ] [질문]

## Tasks
- [ ] [후속 작업]

## 공지사항
- [공지]

## 관련 노트
- [[이전 주차]] — [한 줄 메모]
- 교재 PDF / 녹취록 경로
```

### prev/next 필드 규칙

- **`prev_lecture`**: 같은 subject의 이전 주차 노트 Obsidian 링크. 1주차이면 `""`
- **`next_lecture`**: 같은 subject의 다음 주차 노트 Obsidian 링크. 마지막이면 `""`
- 새 노트 생성 시 **이전 주차 노트의 `next_lecture`도 반드시 갱신**
- 본문 상단에 `← 이전 주차 (교수 한국어) | 다음 주차 →` 네비게이션 표시
- wikilink display alias 로 한자 인명을 한국어로 표시: `[[2026-04-23 ID 3주차 (Professor A)|3주차 (Professor A)]]`

## 4단계: 이미지 추출 (PDF가 있으면 항상 실행)

PDF 강의자료가 있을 경우 **별도 지시 없이 자동으로** 전체 페이지를 PNG로 추출하고 노트에 삽입한다.

### 추출 코드 (pypdfium2 사용 — pymupdf는 DLL 오류로 사용 불가)

```python
import pypdfium2 as pdfium

pdf_path = r"강의자료.pdf"
out_dir = r"$VAULT/0. Inbox/Files"
prefix = "{접두어}"  # 예: ID_W5_p

pdf = pdfium.PdfDocument(pdf_path)
for i, page in enumerate(pdf):
    bitmap = page.render(scale=2)
    pil_image = bitmap.to_pil()
    pil_image.save(f"{out_dir}/{prefix}{i+1:02d}.png")
```
- `python` 명령 사용 (Windows, `python3` 아님)
- 패키지: `pip install pypdfium2`

### 노트 내 삽입 규칙
- 주요 다이어그램/그래프 슬라이드: `![[파일명.png|560]]` + 캡션 (한국어)
- 보조 슬라이드: `![[파일명.png|400]]` + 캡션
- 텍스트만 있는 슬라이드(표지, 목차, 참고문헌 등): 삽입 생략

### 삽입 위치
각 섹션의 **설명 텍스트 앞**에 해당 슬라이드 이미지를 배치 (시각적 anchor).

### 강의 영상에서만 보이는 라이브 마크업 추가 추출
강사가 강의 중 펜으로 슬라이드에 표시한 내용·구두 보충 등이 노트의 anchor 로 필요하면 **M-003 (`extract_slide_pngs.py`)** 를 사용해 mp4 에서 직접 추출. 자세한 절차는 M-003 module 참조.

## 5단계: note-organizer 에이전트 호출

`note-organizer` 에이전트에게 전달할 때 **다음을 모두 명시** (M-001 § 에이전트 호출 시 명시할 항목 체크리스트와 동일):

1. 추출한 텍스트/이미지 내용
2. 과목명, 주차, 교수명
3. 입력 자료 절대 경로 (녹취록 / PDF / 사용자 메모)
4. **M-001 § 깊이 가이드라인 명시** — n단계 분해 패턴, 식의 의미 분해, 콜아웃 4종 용법, "왜 이 형태인가" 동기, 다음 섹션 연결 인용
5. **M-001 § 언어·표기 정책** — 한자 0건, 인용 한국어 의역, 인명 한국어 음역
6. **분량 가이드** — 강의 시간 → 줄 수 목표 (예: 90분 → 1100~1500줄)
7. **좋은 노트 예시 reading 지시** — `2026-04-30 ID 4주차 (Professor A).md` §III-3-A(b)/(c)/(g) 와 `2026-05-07 ID 5주차 (Professor A).md` §(b)/(f)/(g)/III-3-B(d) 를 참조해 깊이 감각 보정
8. frontmatter 스키마 (위 §3단계)
9. 이미지 placeholder 규칙
10. **완료 후 보고 형식**: 줄 수, 한자 본문 잔존 개수, 핵심 섹션별 분량, 추가된 콜아웃·인용 개수

복잡한 물리 해석이 필요하면 → `paper-reviewer` 에이전트에 따로 요청.

## 관련 스킬·모듈
- `pdf` 스킬 — PDF 강의자료 읽기
- `markitdown` 스킬 — 파일 형식 변환 (PPT, DOCX → MD)
- **M-001** (정본) — 깊이·언어 정책
- **M-002** — 녹취록 TXT 생성 (선행 단계)
- **M-003** — 강의 영상 슬라이드 PNG 추출 (라이브 마크업 필요 시)
