---
description: 논문 읽기 전 빠른 사전 분석. abstract/conclusion/figure 스캔 → 관련도 평가 + 읽기 포인트 제시. 인자: PDF 경로 / arXiv ID / 논문 제목
---

**워크플로우 매뉴얼 먼저 읽기**: `.claude/workflows/paper-scan.md`

논문 사전 분석 요청: $ARGUMENTS

순서:
1. 워크플로우 매뉴얼을 Read 도구로 읽어 출력 형식 확인
2. 입력 형태에 따라:
   - PDF 파일 → `pdf` 스킬 호출: `Skill("pdf", args="$ARGUMENTS")`
   - arXiv ID → WebFetch `https://arxiv.org/abs/{id}`
   - 제목만 → `bgpt-paper-search` 스킬로 먼저 찾기
3. Abstract + Introduction + Conclusion + Figure 캡션만 읽음 (전체 본문 X)
4. 워크플로우 형식대로 사전 분석 출력
5. Zotero 노트(`@citekey.md`)가 있으면 `## 📋 읽기 전 분석` 섹션에 저장
