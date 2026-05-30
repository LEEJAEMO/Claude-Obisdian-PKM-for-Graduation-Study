---
description: Vault 정합성 검증 (고아 노트, 스키마 위반, 메타데이터 완성도)
---

# /lint — Vault 정합성 검사

볼트 전체 frontmatter 스키마, 고아 노트, controlled vocabulary 위반 여부를 검사하고 리포트한다.

## 실행

```bash
python scripts/vault_lint.py
```

결과는 `scripts/lint_report.txt`에 저장되고 터미널에도 출력된다.

## 검사 항목

1. **고아 노트**: 어느 곳에서도 wikilink로 참조되지 않는 파일
   - 단, Index/MOC 노트(`!`로 시작)는 제외
   - 논문(`@`로 시작)은 Paper Index에서 Dataview로 관리되므로 제외
   - 강의노트·세미나·실험 노트는 Dataview 기반 MOC에 등록되면 "의사 고아"로 허용 (linter는 경고만)

2. **Frontmatter 스키마 위반**:
   - `type: zotero` — `my_context`, `my_take`, `topic` 필드 존재
   - `type: assignment` — `due_date` 존재
   - `type: experiment-note` — status enum 준수 (planning/in-progress/completed/troubleshooting)
   - `type: knowledge-note` — status enum 준수 (active/draft/archived/processed/pending/reviewed)
   - 구 버전 type 탐지 (`type: 과제` 등)

3. **Controlled Vocabulary 위반**:
   - 논문 `topic` 필드의 모든 항목이 `!Paper Index.md`의 vocab 목록 내에 있는지

4. **논문 메타데이터 완성도**:
   - `my_context` 빈 값 카운트
   - `key_claim` 빈 값 카운트
   - `my_take` 빈 값 카운트

## 출력 후 조치

리포트에서 발견된 이슈를 다음 순서로 처리:
1. **스키마 위반** → 즉시 수정 (자동화 가능)
2. **vocab 위반** → `!Paper Index.md` vocab에 추가 or topic 수정
3. **고아 노트** → 사용자 검토 (의사 고아 vs 실질 고아 구분)
4. **my_context 빈 값** → 사용자 수동 입력 (주간 점검 시 몰아서)

## 주기

- 주간 점검 때 반드시 실행 (매뉴얼 §5 참조)
- 대규모 마이그레이션 직후 실행
- `/save-session` 전 실행 권장
