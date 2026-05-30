---
description: 논문 섹션 또는 연구 보고서 초안 작성. 인자: "섹션명 [참고 논문 @키 목록]". 예) "introduction @HayashiEtAl2023 @FukamiEtAl2025"
---

# 논문 초안 작성

`scientific-writing` 스킬을 사용해 IMRAD 형식의 물리학 논문 섹션을 작성한다.

## 연구 컨텍스트 (항상 유지)

- 연구: Orbital Hall Effect in SiC (Spintronics Lab, 교토대 석사)
- 타깃 저널: Physical Review Letters / Physical Review B (APS 형식)
- 언어: 영어 (한국어 초안 가능, 최종은 영어)
- 인용 형식: APS (Physical Review) — \[1\] 번호 방식

## 실행 순서

### Step 1: 참고 자료 로드

인자에 `@citekey`가 있으면 해당 Zotero 노트 Read:
- `$HOME\OneDrive\문서\Obsidian Vault\Zotero\@{citekey}.md`
- `[!Synth]` 블록과 `# Annotations` 섹션에서 핵심 내용 추출

### Step 2: 섹션별 작성 전략

`scientific-writing` 스킬의 2단계 접근법 적용:
1. **Stage 1**: 핵심 포인트 목록 (내부용 구조화)
2. **Stage 2**: 완성된 산문 단락으로 변환

**섹션별 기준:**

| 섹션 | 내용 | 길이 기준 |
|------|------|---------|
| Introduction | 배경 → gap → 우리 연구 → 논문 구성 | 3~5 단락 |
| Methods | 실험 장치·절차·측정법 (재현 가능하게) | 2~4 단락 |
| Results | 데이터 객관적 서술, 그림/표 참조 | 데이터 중심 |
| Discussion | 해석 → 기존 연구와 비교 → 한계 → 전망 | 3~5 단락 |
| Abstract | 전체 요약 (250단어 이내, 단일 단락) | 250단어 |
| Cover letter | 저널 편집장에게, 연구의 의의 강조 | 1페이지 |

### Step 3: 물리 표기 규칙

- 수식: LaTeX 인라인 `$\sigma_{xy}^{orb}$`, 블록 `$$...$$`
- 단위: SI (A, T, V, Ω·m 등)
- 벡터·텐서: 볼드체 또는 아래첨자 표기
- OHE 관련 기호: $\sigma_{OH}$, $\xi_{DL}$, $\tau_{OT}$, $\ell_{orb}$

### Step 4: 출력

**영어 초안 요청 시** — 완성된 산문 단락 (불릿 포인트 없음)

**한국어 → 영어 변환 요청 시** — 한국어 초안 먼저, 영어 번역 후

저장 경로 (선택):
```
$HOME\OneDrive\문서\Obsidian Vault\1. Project\대학원 공부\2. 연구 (Research)\drafts\YYYY-MM-DD_{섹션명}.md
```

## 관련 스킬
- `scientific-writing` — IMRAD 구조, 산문 작성 원칙
- `citation-management` — APS 인용 형식 검증
- `venue-templates` — Physical Review B/L 투고 양식
