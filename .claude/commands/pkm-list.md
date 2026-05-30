---
description: PKM 특정 폴더의 llms.md 인덱스 조회
argument-hint: "[Modules|Research|Troubleshooting|Specs]"
---

# /pkm-list — PKM 폴더 인덱스 조회

사용자가 PKM 폴더의 현재 인덱스를 빠르게 보고 싶을 때 사용.

## 동작

인자 `$1`에 따라 해당 폴더의 `llms.md`를 읽어 채팅에 표시한다:
- `Modules` → `999. Claude guideline/1. Claude PKM/11. Modules/llms.md`
- `Research` → `.../12. Research/llms.md`
- `Troubleshooting` → `.../13. Troubleshooting/llms.md`
- `Specs` → `.../14. Specs/llms.md`
- 인자 없음 → 마스터 `.../1. Claude PKM/llms.md`

## 구현 지시 (AI에게)

1. 인자 파싱 후 대상 파일 경로 결정
2. Read 도구로 해당 `llms.md` 읽기
3. `## 항목 테이블` 섹션 중심으로 응답 (전체가 짧으면 전체)
4. 비어 있으면 "현재 등록된 항목 없음" + 폴더 용도 안내
