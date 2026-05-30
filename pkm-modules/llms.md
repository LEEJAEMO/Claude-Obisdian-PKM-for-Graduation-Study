# 11. Modules — Index

purpose: 반복되는 연구·학습 task의 절차/템플릿 모듈화
scope: 강의노트 작성, 논문 리뷰, 세미나 요약, 문헌 조사, 교재 MOC, 기업 리서치, 실험 데이터 자동화 파이프라인 등
non_scope: 측정 모델별 fit 알고리즘 자체는 modules/<measurement>.py 에 분리 (본 인덱스 외 — M-006 § 표준 4 함수 인터페이스 참조)
last_updated: 2026-05-29

## 사용법

- 작업 시작 전 아래 테이블 조회 → 재사용 가능한 모듈이 있으면 참조
- **작업 완료 후 재사용 가치가 있으면 사용자 승인받고 신규 항목으로 추가**

## 파일명 규칙

`M-<3자리번호>_<slug>.md` (예: `M-001_paper-review-routine.md`)

## Frontmatter 스키마

```yaml
---
type: pkm-module
id: M-001
title: 논문 리뷰 기본 절차
domain: [paper-review, research]     # 도메인 태그
task_type: workflow                  # workflow | template | checklist
input: "논문 PDF 또는 arXiv ID"
output: "Zotero Synth callout + Vault 노트"
related_command: /paper-review
related_spec: 14. Specs/commands/paper-review.md
created: 2026-04-19
updated: 2026-04-19
---
```

## 항목 테이블

| ID | 제목 | 도메인 | task_type | 입력 | 출력 | 경로 |
|----|------|--------|-----------|------|------|------|
| M-001 | 강의노트 작성 루틴 | [lecture-note, teaching, obsidian] | workflow | 녹취록 TXT (필수) + 강의 PDF (선택, 복수 가능) + 사용자 메모 (선택) | Obsidian 강의노트 .md 파일 + 슬라이드 이미지 PNG | M-001_lecture-note-routine.md |
| M-002 | 강의 녹취록 생성 루틴 | [lecture-note, whisper, transcription] | workflow | 강의 녹화 MP4 또는 M4A 파일 경로 | 슬라이드 분절 녹취록 TXT (`<mp4_dir>/녹취록/<파일명> 녹취록.txt`) | M-002_lecture-transcribe-routine.md |
| M-003 | 강의 영상 슬라이드 PNG 추출 루틴 | [lecture-note, video-frame, obsidian] | workflow | 강의 MP4 + lecture_transcribe.py 가 만든 녹취록 TXT + 추출할 슬라이드 번호 목록 (선택) | Obsidian Vault/0. Inbox/Files/<prefix>_pXX.png (1280×720 등 원본 해상도) | M-003_slide-png-extract-routine.md |
| M-004 | Claude Design 기반 프로세스 플로우 도식화 루틴 | [claude-design, visualization, process-flow, fabrication, experiment] | workflow | 프로세스 단계 목록 (텍스트) + 재료/색상 매핑 + 스타일 선호도 | claude.ai/design 에 통째로 붙여넣을 수 있는 prompt + Refinements + 출력 PDF/PPTX 저장 경로 | M-004_claude-design-process-flow-routine.md |
| M-005 | 반도체 기업 리서치 노트 작성 루틴 | [career, company-research, semiconductor, market-analysis] | workflow | 기업명 (필수) + 사용자 관심 분야 (선택) + 지원 직무 (선택) + 기존 회사 노트 참조 (선택) | Obsidian Vault/2. Area/2.2 Career/Semiconductor MOC/3. Company/<기업명>.md (600~900줄 표준 분량) | M-005_semiconductor-company-research-routine.md |
| M-006 | 실험 데이터 자동화 파이프라인 루틴 (raw → processed → Obsidian) | [experiment, research-data, automation, python, obsidian-sync] | workflow | 실험실 PC 의 raw 데이터 폴더 + 프로젝트명 + 측정 종류 + 샘플 ID | 6. Experiment/4. Project/<project>/<date-meas>/<sample>/ 표준 구조 (00_raw + 01_processed + 02_notebooks) + Obsidian Vault 측정 노트 자동 생성 (frontmatter + plot 임베드) | M-006_experiment-data-pipeline-routine.md |
