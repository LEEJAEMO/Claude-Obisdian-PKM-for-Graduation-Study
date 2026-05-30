---
description: 논문을 읽은 후 Synth callout 완성. 인자: PDF 경로 / arXiv ID / 논문 제목 [--memo <메모 텍스트 또는 파일경로>]
---

**워크플로우 매뉴얼 먼저 읽기**: `.claude/workflows/paper-review.md`

논문 분석 요청: $ARGUMENTS

> **읽기 전 사전 분석은 `/paper-scan`을 사용하세요.**
> 이 명령어는 논문을 읽은 후 Synth callout을 완성하는 단계입니다.

인자 파싱:
- 논문 식별자 (PDF 경로 / arXiv ID / 제목) — 필수
- `--memo <텍스트 또는 파일경로>` — 읽으면서 적은 하이라이트·질문·메모 (선택)

순서:
1. 워크플로우 매뉴얼을 Read 도구로 읽어 출력 형식 확인
2. 입력 형태에 따라:
   - PDF 파일 → `pdf` 스킬 호출: `Skill("pdf", args="...")`
   - arXiv ID → WebFetch `https://arxiv.org/abs/{id}`
   - 제목만 → `bgpt-paper-search` 스킬로 먼저 찾기
3. Zotero 노트에 `## 📋 읽기 전 분석` 섹션이 있으면 Read로 불러와 컨텍스트에 포함
4. `--memo`가 있으면 메모 내용을 Synth 작성 시 반영
5. `paper-reviewer` 서브에이전트를 호출해 전체 Synth callout 작성
6. 워크플로우 매뉴얼의 Zotero 노트 업데이트 절차에 따라 저장
