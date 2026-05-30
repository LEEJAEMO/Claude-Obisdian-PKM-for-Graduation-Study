# 논문 사전 분석 워크플로우 (읽기 전)

## 목적

논문을 본격적으로 읽기 전에 빠르게 핵심 구조를 파악하고 읽기 방향을 설정한다.
읽은 후에는 `/paper-review --memo <메모>` 로 이어진다.

---

## 1단계: 입력 처리

| 입력 형태 | 처리 방법 |
|----------|---------|
| PDF 파일 경로 | `pdf` 스킬로 읽기 → `Skill("pdf")` |
| arXiv ID (예: 2501.12345) | WebFetch `https://arxiv.org/abs/{id}` |
| 논문 제목만 | `bgpt-paper-search` 스킬로 먼저 검색 |

**읽는 범위**: Abstract + Introduction (첫 2단락) + Conclusion + Figure/Table 캡션만.
본문 전체는 읽지 않는다 — 유저가 직접 읽을 것이므로 context 절약.

---

## 2단계: 사전 분석 출력

아래 형식으로 출력:

```markdown
## 📋 읽기 전 분석

**논문**: [제목]
**저자**: [저자] ([연도]) [저널]
**arXiv / DOI**: [링크]

### 핵심 주장 (Abstract 기반)
[논문이 무엇을 주장하는지 1~3문장. 결론의 핵심만.]

### 논문 구조 한눈에
| 섹션 | 내용 요약 |
|------|---------|
| Introduction | [무엇을 동기로 하는가] |
| Methods / Theory | [어떤 방법/이론을 쓰는가] |
| Results | [어떤 결과를 얻었는가] |
| Discussion | [어떻게 해석하는가] |
| Conclusion | [결론 핵심] |

### 주목할 Figure / Equation
- **Fig. N**: [이 그림이 왜 중요한지]
- **Eq. N**: [이 수식이 무엇을 말하는지]
(3~5개 선별)

### OHE in SiC 연관도
관련도: [높음 / 중간 / 낮음]
이유: [왜 이 관련도인가 — 구체적으로]
활용 포인트: [우리 연구에서 어떻게 쓸 수 있는가]

### 읽기 가이드
읽을 때 이 질문들을 염두에 두세요:
- [ ] [이 논문을 읽으며 답해야 할 핵심 질문 1]
- [ ] [핵심 질문 2]
- [ ] [핵심 질문 3]
(최대 5개)

**추천 읽기 방식**: [전체 정독 / Introduction+Results 위주 / Conclusion+Figures만 / Skip]
**이유**: [왜 그 방식을 추천하는지]
```

---

## 3단계: Zotero 노트에 저장

**노트 위치 (2026-04-15 마이그레이션 이후)**:
`$VAULT\1. Project\대학원 공부\2. 연구 (Research)\6. Papers\@{citekey}*.md`

(파일명은 `@{citekey}_{title-slug}.md` 패턴 — citekey로 prefix 매칭)

해당 노트가 존재하면:
1. **`# 📋 읽기 전 분석` 섹션이 노트에 없으면 새로 추가**, 있으면 내용 갱신
   - 삽입 위치: `# Annotations` 섹션 바로 위 (`---` 구분선 뒤)
   - 템플릿 정책(2026-05-06): 임포트 시점에는 분석 섹션이 비어있는 채로 자동 생성되지 않음 — 이 명령이 첫 생성 책임
2. frontmatter의 `status`를 `unread` → `pre-read`로 업데이트
3. `topic`(controlled vocab), `relevance`, `key_claim` 필드도 분석 결과로 채움

**Obsidian/Zotero 노트가 아예 없으면**:
- 분석 결과를 대화창에만 출력 (별도 파일 저장 안 함)
- 사용자가 Zotero Integration 플러그인으로 임포트하도록 안내 (`/zotero-add` 명령은 Zotero Web API로 직접 추가하는 별도 경로)

---

## 4단계: 다음 단계 안내

출력 끝에 반드시 아래를 덧붙인다:

```
─────────────────────────────────────
논문을 읽은 후:
  /paper-review --memo "메모 내용"
  또는
  /paper-review --memo "C:/경로/메모파일.txt"
─────────────────────────────────────
```

---

## 관련 명령어

- `/paper-review --memo <메모>` — 읽은 후 Synth callout 완성
- `/zotero-add` — Zotero에 먼저 논문 임포트
