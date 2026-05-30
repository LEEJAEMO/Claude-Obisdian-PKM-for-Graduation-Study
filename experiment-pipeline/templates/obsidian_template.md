---
type: experiment-note
subtype: measurement
date: {{date}}
project: {{project}}
sample: {{sample}}
measurement_type: {{measurement_type}}
equipment: {{equipment}}
conditions:
  temperature: {{temperature}}
  field_range: {{field_range}}
  excitation: {{excitation}}
  averages: {{averages}}
data_root: {{data_root}}
fit_results:
  R2: {{R2}}
  amplitude_uV: {{amplitude_uV}}
  phase_deg: {{phase_deg}}
  offset_uV: {{offset_uV}}
status: processed
related_papers: []
research_themes: []
tags:
  - experiment
  - {{measurement_type}}
  - {{project}}
last_synced: {{last_synced}}
---

### UP:: [[!Experiment Index]]

# {{date}} {{measurement_type}} — {{sample}}

> **데이터 위치**: `{{data_root}}`
> **처리 노트북**: `02_notebooks/analysis.ipynb`
> **자동 동기화**: sync_to_obsidian.py, 마지막 {{last_synced}}

## 실험 목적

<!-- 수동 기입 -->

## 측정 조건

| 항목 | 값 |
|------|-----|
| 장비 | {{equipment}} |
| 샘플 | {{sample}} |
| 측정법 | {{measurement_type}} |
| 날짜 | {{date}} |
| 온도 | {{temperature}} |
| 자기장 | {{field_range}} |
| Excitation | {{excitation}} |
| Averages | {{averages}} |

## Fit 결과

| 지표 | 값 |
|------|-----|
| R² | {{R2}} |
| Amplitude (μV) | {{amplitude_uV}} |
| Phase (°) | {{phase_deg}} |
| Offset (μV) | {{offset_uV}} |

## 결과 플롯

![[{{date}}_{{measurement_type}}_{{sample}}_summary.png|700]]

### 개별 플롯

![[{{date}}_{{measurement_type}}_{{sample}}_raw_overlay.png|500]]
*Raw data overlay*

![[{{date}}_{{measurement_type}}_{{sample}}_fit.png|500]]
*Fit 결과*

![[{{date}}_{{measurement_type}}_{{sample}}_residuals.png|500]]
*Fit 잔차*

## 고찰

<!-- 수동 기입 -->

## 다음 단계 / 미해결

<!-- 수동 기입 -->

## 관련 노트

- [[Samples#{{sample}}]]
- [[!Experiment Index]]
