---
description: OHE/Spintronics 문헌 검색. 인자: 검색 주제 (예: "orbital Hall effect in semiconductors")
---

**워크플로우 매뉴얼 먼저 읽기**: `.claude/workflows/lit-search.md`

문헌 검색 요청: $ARGUMENTS

순서:
1. 워크플로우 매뉴얼을 Read 도구로 읽어 키워드 전략 확인
2. 이전 검색 결과 확인: `.claude/lit-notes/` 폴더 목록 조회 (중복 방지)
3. 스킬 호출 순서:
   - 기본: `bgpt-paper-search` 스킬 → `Skill("bgpt-paper-search", args="$ARGUMENTS")`
   - 결과 부족 시: `paper-lookup` 스킬 추가
   - 체계적 리뷰 필요 시: `literature-review` 스킬
   - 심층 분석 필요 시: `deep-research` 스킬
4. `literature-searcher` 서브에이전트를 호출해 결과 정리
5. 매뉴얼의 출력 형식으로 정리 후 `.claude/lit-notes/{topic}-{date}.md` 저장
6. Zotero에 즉시 추가 추천 논문 목록 별도 제시

중복 검색 금지 — 첫 검색에 충분한 키워드 변형 사용.
