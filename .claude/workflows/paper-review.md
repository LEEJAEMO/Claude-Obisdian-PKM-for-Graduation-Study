# 논문 분석 워크플로우

## 1단계: 입력 처리

| 입력 형태 | 처리 방법 |
|----------|---------|
| PDF 파일 경로 | `pdf` 스킬로 읽기 → `Skill("pdf")` |
| arXiv ID (예: 2501.12345) | WebFetch `https://arxiv.org/abs/{id}` |
| Obsidian Zotero 노트 경로 | Read 도구로 직접 읽기 |
| 논문 제목만 | `bgpt-paper-search` 또는 `paper-lookup` 스킬로 먼저 검색 |

## 2단계: 분석 실행

`paper-reviewer` 서브에이전트를 호출해 분석.
복잡한 PDF는 `paperzilla` 스킬을 먼저 사용해 핵심 추출 후 에이전트에 전달.

## 3단계: 출력 형식 (Zotero 노트 호환)

분석 결과는 아래 형식으로 출력. Obsidian의 기존 Zotero 노트(`@저자연도.md`)에 붙여 넣을 수 있게 설계됨.

```markdown
> [!Synth]
> ### 핵심 주장
> [🔴 Red 하이라이트에 해당하는 논문의 핵심 주장 — 1~3문장]
>
> ### 이론적 근거
> [🟢 Green — 사용된 이론/모델. Berry curvature, Kubo formula, 궤도-격자 결합 등]
> 핵심 수식: $수식$
>
> ### 실험/방법
> [🟣 Purple — 실험 기법, 소자 구조, 측정량. Hall bar, ST-FMR, ISHE, Harmonic Hall 등]
>
> ### OHE in SiC 연구와의 연결
> 관련도: [높음 / 중간 / 낮음]
> [이 논문의 결과/방법을 우리 연구에 어떻게 활용할 수 있는가]
>
> ### 열린 질문
> [🔵 Blue — 논문의 한계, 대안적 해석, 미해결 질문]
>
> Related:: [[연관노트1]], [[연관노트2]]

> [!question] Q&A
> Q1: [논문에서 불명확한 점]
> A1: [Claude 답변]

> [!example] 모르는 단어
> - **[용어]**: [설명]
```

## 4단계: 사전 분석 + 메모 통합

> 읽기 전 사전 분석은 `/paper-scan` 워크플로우에서 담당한다.
> 이 워크플로우는 **읽은 후** Synth callout을 완성하는 단계다.

**Zotero 노트에 `## 📋 읽기 전 분석` 섹션이 있으면:**
- 해당 섹션(관련도 평가, 읽기 가이드의 질문들)을 Synth 작성 시 참조
- 사전 분석에서 제기한 질문에 Synth가 답했는지 확인

**`--memo` 인자가 있으면:**
- 메모가 텍스트이면 그대로 사용
- 메모가 파일 경로이면 Read 도구로 읽기
- 메모의 내용을 섹션별로 분류:
  - 핵심 주장/강조 → `### 핵심 주장`에 반영
  - 의문점/질문 → `[!question] Q&A`에 반영
  - 모르는 단어 → `[!example] 모르는 단어`에 반영
  - 실험/방법 관련 → `### 실험/방법`에 반영

## 5단계: Zotero 노트에 직접 반영

**우선순위: Zotero 노트 직접 업데이트**

**노트 위치 (2026-04-15 마이그레이션 이후)**:
`$VAULT\1. Project\대학원 공부\2. 연구 (Research)\6. Papers\@{citekey}*.md`

해당 노트가 존재하면:
1. frontmatter 업데이트: `status` (→ `read`), `importance`, `topic`, `relevance`, `key_claim`, `my_take`
2. **`# 📝 읽은 후 분석` 섹션이 없으면 새로 추가**, 있으면 `[!Synth]` 블록 교체
   - 삽입 위치: 기존 `# 📋 읽기 전 분석` 섹션 뒤(있을 경우) 또는 `# Annotations` 섹션 바로 위
   - 템플릿 정책(2026-05-06): 임포트 시점에는 빈 `# 📝 읽은 후 분석` placeholder가 자동 생성되지 않음 — 이 명령이 생성 책임
3. `[!md]`, `[!LINK]`, `[!Abstract]`, `# Annotations`, `# Notes` 섹션은 절대 수정하지 않음
4. `# 📎 SI` 섹션은 사용자가 수동으로 채우는 영역 — 명령이 만들지 않고 이미 있으면 건드리지 않는다

**Zotero 노트가 없는 경우에만** 별도 파일 저장:
```
.claude/paper-notes/YYYY-MM-DD_{@키}_{제목약칭}.md
```

## 6단계: 계산 논문 — pymatgen 연동 (선택)

논문이 **DFT / 제1원리 계산 / 결정 구조** 관련이면:

```python
# SiC 구조 확인 예시 (Materials Project API 필요 → MP_API_KEY)
from mp_api.client import MPRester

with MPRester() as mpr:
    # 3C-SiC: mp-7140, 4H-SiC: mp-8062, 6H-SiC: mp-1803
    struct = mpr.get_structure_by_material_id("mp-7140")
    bs = mpr.get_bandstructure_by_material_id("mp-7140")
```

활용 상황:
- 논문의 격자 상수 / 밴드갭 수치를 Materials Project 값과 비교
- 논문에서 제시한 SiC 구조 파일(CIF/POSCAR)을 재현해 symmetry 확인
- OHC (Orbital Hall Conductivity) 계산값의 맥락 파악

## 7단계: BibTeX 생성 (선택)

새 논문이거나 Zotero에 BibTeX가 없으면 `citation-management` 스킬로 생성:

```
Skill("citation-management", args="DOI:{doi}")
```

출력된 BibTeX는 Zotero에 직접 임포트하거나 `[!md]` 블록 아래에 추가.

## 관련 스킬
- `pdf` — PDF 논문 읽기 (1순위)
- `paperzilla` — 복잡한 PDF에서 핵심 추출
- `bgpt-paper-search` — arXiv/PubMed 논문 검색
- `paper-lookup` — DOI/제목으로 10개 DB 동시 검색
- `pymatgen` — DFT/계산 논문: SiC 결정 구조 재현, Materials Project 비교
- `citation-management` — BibTeX 생성 및 인용 검증

## 하이라이트 색상 범례 (참고)
- 🟡 Yellow = 섹션 전체 핵심
- 🔴 Red = 핵심 주장
- 🟢 Green = 이론 설명
- 🔵 Blue = 의문점
- 🟣 Purple = 실험/방법
- 🩷 Pink = 모르는 단어
- 🟠 Orange = 섹션 구분
