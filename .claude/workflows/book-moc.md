# 교재 MOC 작성 워크플로우

## 저장 경로
- MOC 인덱스: `$HOME\OneDrive\문서\Obsidian Vault\3. Resource\학부학습\물리학\!{교재명} MOC.md`
- 챕터 노트: `...\물리학\{교재명}\CH{번호} {제목}.md`

## 1단계: 교재 정보 확인

기존 교재 현황:
| 교재 | 약칭 | MOC | 상태 |
|------|------|-----|------|
| Kittel 고체물리학 8판 | `SS` | `!고체물리학 MOC` | ✅ 완성 |
| 자기학총서 제3판 | `MT` | `!자기학총서 MOC` | 진행중 (7~11장 우선) |

## 2단계: PDF 목차 추출 (필요 시)

> ⚠ **PyMuPDF(fitz) 사용 금지** — Windows DLL 오류로 환경에 따라 import 자체가 실패함.
> 텍스트 / TOC: `pypdf`, 이미지 렌더링: `pypdfium2` 사용.

```python
import sys
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')

reader = PdfReader(r"교재명_ocr.pdf")

# TOC (outline). pypdf는 중첩 리스트로 반환
def walk_outline(items, level=1):
    for item in items:
        if isinstance(item, list):
            walk_outline(item, level + 1)
        else:
            try:
                page_idx = reader.get_destination_page_number(item) + 1
            except Exception:
                page_idx = "?"
            print("  " * (level - 1) + f"[{level}] {item.title} (p.{page_idx})")

if reader.outline:
    walk_outline(reader.outline)
else:
    # outline 없으면 앞 30페이지 텍스트 스캔
    for i in range(min(30, len(reader.pages))):
        text = reader.pages[i].extract_text() or ""
        for line in text.splitlines():
            if line.strip():
                print(repr(line[:120]))
```

## 3단계: Frontmatter 규칙

### MOC 인덱스 파일
```yaml
---
type: MOC
tags: [물리학, MOC]
created: YYYY-MM-DD
source: "[저자], 『교재명』, 판수 (연도)"
---
```

### 챕터 노트
```yaml
---
type: {교재약칭}-챕터        # 예: 자기학총서-챕터
chapter_label: "7"           # 표시용 (소절은 "11.2")
chapter_num: 7               # 정렬용 숫자
title: [한국어 제목]
title_en: [영어 제목]
subject: [교재명]            # MOC 파일명과 정확히 일치
page_start: [시작 쪽]
page_end: [끝 쪽]
research_relevance: "⭐⭐⭐"  # OHE/SiC 관련도 1~5개 별
tags: []
created: YYYY-MM-DD
---
```

**research_relevance 기준**
| 별 | 기준 |
|----|------|
| ⭐⭐⭐⭐⭐ | OHE in SiC 연구에서 직접 사용 |
| ⭐⭐⭐⭐ | 배경 이론, 비교 대상 |
| ⭐⭐⭐ | 간접 관련 지식 |
| ⭐⭐ | 참고 목적 |
| ⭐ | 교양 |

## 4단계: 챕터 노트 내부 구조

```markdown
### UP:: [[!교재명 MOC]]

# CH{번호} {제목}

---

## 핵심 개념
- **[개념]**: 한 문장 정의 (3~10개)

## 주요 공식
### [소제목]
$$수식$$
- 변수 의미

## 세부 노트
### [소절]
내용

> [!figure] 그림 N — [제목]
> - **id**: {약칭}_CH{번호}-f{번호}_p{쪽수}
> - **fig_type**: graph / schematic / diagram / photo / plot
> - **topic**: [설명]
> - **key_value**: [핵심 수치]
> - **tags**: #태그1 #태그2
> - **source**: {교재명} 제{판}판, p.{쪽수}

![[{약칭}_CH{번호}-f{번호}_p{쪽수}.png|560]]
*그림 N. [설명]. ({교재명}, p.{쪽수})*

## 연구 연결 (OHE in SiC)
[⭐⭐ 이상 챕터에만. 없으면 섹션 전체 생략]
```

## 5단계: 이미지 추출

> ⚠ **PyMuPDF(fitz) 사용 금지** — `pypdfium2`로 페이지 렌더링한다.

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(
    r"$GRAD_ROOT/2. 교재 텍스트/{파일명}.pdf"
)
out_dir = (
    r"$GRAD_ROOT/0. Main Vault"
    r"/Obsidian Vault/0. Inbox/Files"
)

# 단일 페이지 (scale=2 → fitz.Matrix(2,2)와 동일한 해상도)
page_num = 395
pil_image = pdf[page_num - 1].render(scale=2).to_pil()
pil_image.save(f"{out_dir}/{약칭}_CH{번호}-f{번호}_p{page_num:03d}.png")
```

이미지 파일명: `{약칭}_CH{번호}-f{그림번호}_p{쪽수:3자리}.png`
예: `MT_CH09-f03_p401.png`

## 6단계: 작업 순서 (토큰 절약)

1. MOC 인덱스 생성 (전체 챕터 목록 확정)
2. ⭐⭐⭐⭐⭐ → ⭐ 순서로 챕터 작성
3. 한 세션에 3~5개 챕터 제한

## Dataview 쿼리 (MOC 인덱스 내)

```dataview
TABLE WITHOUT ID
    file.link AS "챕터",
    chapter_label AS "No.",
    page_start AS "시작 p.",
    research_relevance AS "관련도"
FROM "3. Resource/학부학습/물리학/{교재명}"
WHERE type = "{약칭}-챕터"
SORT chapter_num ASC
```
