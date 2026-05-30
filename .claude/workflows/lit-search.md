# 문헌 검색 워크플로우

## 1단계: 스킬 선택

| 목적 | 사용 스킬 |
|------|---------|
| arXiv 최신 논문 빠른 검색 | `bgpt-paper-search` |
| DOI/제목으로 메타데이터 | `paper-lookup` |
| 체계적 리뷰 (여러 DB) | `literature-review` |
| 심층 웹 리서치 | `deep-research` |
| 검색 결과 부족 시 반복 | `iterative-retrieval` |

기본값: `bgpt-paper-search` 우선 → 부족하면 `literature-review`.

## 2단계: 검색 키워드 전략

### OHE 핵심 키워드
```
"orbital Hall effect"
"orbital Hall conductivity" / "OHC"
"orbital current" / "orbital angular momentum transport"
"orbital torque" / "orbital-to-spin conversion"
"orbitronics"
```

### SiC 관련
```
"silicon carbide spintronics" / "SiC spin transport"
"wide bandgap semiconductor spintronics"
"SiC orbital" / "3C-SiC" / "4H-SiC"
```

### 실험 기법
```
"inverse orbital Hall effect" / "IOHE"
"orbital Hall magnetoresistance"
"spin pumping FMR" / "ferromagnetic resonance"
"harmonic Hall measurement" / "second harmonic"
"spin Seebeck effect"
```

### 검색 순서
1. 좁은 키워드 (SiC + OHE 조합) → 직접 관련 논문
2. 넓은 키워드 (OHE general) → 배경/방법론
3. 실험 기법 키워드 → 차용할 수 있는 방법

## 3단계: 우선 검색 데이터베이스

1. **arXiv** — `cond-mat.mes-hall`, `cond-mat.mtrl-sci` (최신 프리프린트)
2. **Physical Review Letters / PRB** — 핵심 실험/이론
3. **Nature Materials / Nature Physics** — 고임팩트 리뷰
4. **Google Scholar** — 포괄 검색

## 4단계: 출력 형식

```markdown
## 문헌 검색: [주제]
검색일: YYYY-MM-DD

### 핵심 논문

| # | 제목 | 저자 | 저널 | 연도 | 관련도 | 핵심 내용 |
|---|------|------|------|------|--------|---------|
| 1 | ... | ... | ... | 20XX | ★★★ | ... |

### 연구 흐름 요약
[이 분야 최근 트렌드 3~5문장]

### SiC OHE 연구 직접 연결 논문
[상위 3개, 활용 방법 구체적으로]

### 추가 검색 키워드 제안
[새로 발견된 용어/개념]

### Zotero 추가 추천
[즉시 Zotero에 추가할 만한 논문 목록]
```

## 관련도 기준
- ★★★: OHE in semiconductors 또는 SiC spintronics 직접 관련
- ★★: OHE 이론/실험 일반, 또는 SiC 물성
- ★: 방법론 또는 배경 지식

## 5단계: 저장

저장 경로: `.claude/lit-notes/{topic}-{YYYY-MM-DD}.md`

중복 방지: 검색 전에 `.claude/lit-notes/` 폴더 확인해 이전 검색 결과와 중복 논문 제외.
