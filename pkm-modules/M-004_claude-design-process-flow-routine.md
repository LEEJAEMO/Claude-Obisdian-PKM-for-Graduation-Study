---
type: pkm-module
id: M-004
title: Claude Design 기반 프로세스 플로우 도식화 루틴
domain: [claude-design, visualization, process-flow, fabrication, experiment]
task_type: workflow
input: "프로세스 단계 목록 (텍스트) + 재료/색상 매핑 + 스타일 선호도"
output: "claude.ai/design 에 통째로 붙여넣을 수 있는 prompt + Refinements + 출력 PDF/PPTX 저장 경로"
related_command: (수동 호출 — 사용자가 "프로세스 플로우 시각화" 요청 시)
related_spec: (없음 — 외부 도구 prompt 작성 루틴)
related_module: "[[M-001_lecture-note-routine]] (강의노트에 figure 삽입 시 연계)"
example_artifacts:
  - "[[2026-06-15 MF Report — Claude Design Prompts]] (P-1 SADP×SADP, P-2 MOS 게이트 적층)"
created: 2026-05-26
updated: 2026-05-26
---

# M-004 — Claude Design 기반 프로세스 플로우 도식화 루틴

> **재사용 목적**: 반도체 fabrication 공정, 실험 프로토콜, 디바이스 제작 단계 등 **선형·순차적 프로세스의 시각화** 를 [claude.ai/design](https://claude.ai/design) 으로 빠르게 만들기 위한 prompt 작성 + 정제 루틴의 단일 정본.
>
> **이 도구의 위치**: Claude Design 은 Anthropic Labs 가 2026-04-17 출시한 시각 생성 도구 (Pro/Max/Team/Enterprise 가입자 대상, research preview). 자연어 prompt → 프로토타입·슬라이드·one-pager 생성. **본 모듈은 그 prompt 작성의 모범을 정한다**.
>
> **선행 모듈**: 없음. **후행 모듈**: M-001 (강의노트의 figure 삽입), 추후 실험 매뉴얼 작성 시.

## 트리거

- 사용자가 자연어로:
  - "프로세스 플로우 그림 만들어줘"
  - "실험 단계 시각화"
  - "fabrication flow 그려줘"
  - "device 단면도"
  - "공정 흐름도"
- 또는 레포트·논문·강의자료 내 "Fig. X 자리에 들어갈 그림이 필요한 상황"

## 적용 영역 (재사용 사례)

| 영역 | 예시 | 필요 패널 수 |
|---|---|---|
| **반도체 fabrication** | MOSFET 적층, BEOL 배선, 3D-NAND | 10~20 |
| **MEMS 제작** | Bosch process, sacrificial layer 흐름 | 8~15 |
| **실험 프로토콜** | EBL dose ladder, spin coating, RIE 조건 | 5~12 |
| **디바이스 구조** | Hall bar, ST-FMR CPW, OHE 측정 구조 | 5~10 |
| **분석 워크플로우** | M-H 측정 + 분석, ST-FMR fitting flow | 5~10 |
| **공정 비교** | Wet vs Dry etching, 단일 vs 다중 패터닝 | 2~4 |

> [!info] 본 모듈의 적용 한계
> Claude Design 은 **개념·도식 수준** 의 그림 생성에 강함. **CAD 정밀 마스크 디자인** (예: 정확한 nm 단위 device layout) 은 KLayout/CleWin/L-Edit 가 본업. Design 으로 그린 그림은 보고서·발표용 그림. 실제 EBL 마스크 데이터 작성은 별도.

## 1차 소스 원칙

- **사용자가 단계 목록을 텍스트로 제공** 한 경우: 그 순서·내용 그대로 보존
- 단계 목록이 모호하거나 누락된 경우: **반드시 사용자에게 확인 후 진행** (임의로 단계를 추가하지 않음)
- **재료·색상 매핑** 은 일관성이 핵심 → 한번 정한 색상은 전체 figure 에서 유지

## 단계 요약

| Step | 작업 |
|------|------|
| 0 | 사용자 요청에서 정보 추출 — 단계 목록, 재료, 스케일, 출력 형식 (PDF/PPTX/PNG) |
| 1 | 누락 정보 확인 — 재료 두께, 컬러 선호도, 패널 수, 페이지 방향 |
| 2 | 본 M-004 의 **prompt 골격** 을 채워 1 차 prompt 생성 |
| 3 | 사용자에게 prompt 전달 — claude.ai/design 에 통째로 붙여넣기 안내 |
| 4 | 1 차 출력 확인 — 사용자가 결과 캡처/공유 |
| 5 | **Refinements** 단계 — 본 모듈의 패턴화된 후속 지시 중에서 선택 |
| 6 | 최종 결과물을 Obsidian Vault 의 적합한 위치에 저장 + 본문 노트에 wikilink |

## Prompt 골격 (재사용 가능)

### A. 단계별 단면도 (Cross-section) 시퀀스

```
Create a {N}-step semiconductor process-flow figure that illustrates
{프로세스 이름, 한 문장}.

== Layout ==
- One vertical figure ({A4 portrait | A3 landscape}) divided into {N}
  numbered panels in a {rows} × {cols} grid.
- Each panel shows a CROSS-SECTION view{, with a TOP-VIEW inset (top-right
  corner of the panel, 30 % size) if needed}.
- Each panel has a small caption (max 2 lines) below it.
- A common color legend at the top of the figure.

== Materials and colors (legend) ==
- {Material 1}           — {color name + hex}
- {Material 2}           — {color name + hex}
- ...

== The {N} panels (left-to-right, top-to-bottom) ==

Panel 1  "{Step 1 title}"
  {Description of cross-section appearance. Be specific about thickness
   and order of layers.}
  {Optional: Inset top view: ...}

Panel 2  "{Step 2 title}"
  ...

...

Panel {N}  "{Step N title}"
  ...

== Style ==
- Black 0.75-pt outlines around each material
- {Optional: Top-view insets enclosed in a thin black frame}
- Scale bar "{value}" in the bottom-right of every cross-section
- Title at top of figure:
  "{Figure title}"
- Bottom of figure: "{Footer — author + date + caveat}"

== Output ==
- PDF, {paper size and orientation}, 300 dpi
- Also export as PPTX so labels remain editable.
```

### B. Top view + 마스크 정렬

```
Create a single A4 portrait figure with 3 sub-figures showing:

Sub-figure A (top half): TOP VIEW of the final device.
  - {Layer 1 outline + position}
  - {Layer 2 outline + position}
  - ...
  - Wafer-corner global alignment marks (cross + chevron, black) at the
    four corners
  - Scale bar "{value}"

Sub-figure B (lower-left): Mask {M1} layout.
  - {Polarity: dark-field or bright-field}
  - {Opening shape and position}
  - Alignment marks at the four corners

Sub-figure C (lower-right): Mask {M2} layout.
  - {Polarity}
  - {Opening shape and position}
  - Alignment marks at the four corners
  - {Optional annotation: overlay tolerance}

== Common elements ==
- Title: "{Figure title}"
- Bottom: "{Author + date}"

== Output ==
- PDF, A4 portrait, 300 dpi
- Also export as PPTX
```

### C. 실험 프로토콜 / 워크플로우 (선형)

```
Create a horizontal flowchart figure ({A4 landscape | wide aspect})
showing the {N}-stage experimental protocol for {프로세스 이름}.

== Layout ==
- {N} stages arranged left-to-right, connected by arrows.
- Each stage is a rounded rectangle with:
    Top: stage number + title (1 line, bold)
    Middle: 1 photo/icon (optional)
    Bottom: key parameters (max 2 lines)
- Color-code stages by type (preparation/process/measurement/analysis).

== Stages ==

Stage 1: "{Title}"
  Parameters: {key params}
  Type: {prep | process | measurement | analysis}

...

Stage {N}: "{Title}"
  ...

== Style ==
- Arrows between stages: 1.5-pt black solid; if a stage feeds back to
  an earlier stage, use dashed arrow.
- Color scheme:
    Preparation  — light blue   (#B8DCFF)
    Process      — light orange (#F3B26B)
    Measurement  — light green  (#B8E0B8)
    Analysis     — light purple (#D8B8E0)
- Title at top: "{Figure title}"

== Output ==
- PDF, landscape A4, 300 dpi
- Also PPTX
```

## 시각 스타일 가이드 (공통 원칙)

| 항목 | 권장 값 |
|---|---|
| **배경** | 백색 (#FFFFFF) |
| **재료 색상** | 3~6 색까지. 학술 출판물 스타일 (절제된 채도, 명도 ↑) |
| **글꼴** | Inter, Helvetica, 또는 Arial. 9~11 pt 라벨, 14~16 pt 제목 |
| **선 굵기** | 외곽선 0.5~0.75 pt, 강조 라인 1.5 pt |
| **이온 충격·반응 화살표** | 빨강 (#D32F2F), 굵기 1.5 pt, 머리 폭 ~3 pt |
| **Scale bar** | 모든 단면도에 필수. 우측 하단, 검정 1 pt 굵기 + 길이값 라벨 |
| **결정학 방향 표기** | [100], [010], [001] 등 표준 표기 |
| **저작 표기** | 하단에 "Author + 날짜 + Generated with Claude Design (Anthropic)" |

## Refinements 패턴 (1 차 출력 후 추가 지시)

각 패턴은 1 차 결과의 흔한 부족함을 보완:

### R-1: 치수 라벨 누락

```
Make the {layer name} thickness exactly {value} and label it with a
dimension line at the {position} side.
```

### R-2: 이온 충격·화학 반응 표현

```
In panel {N}, add red arrows pointing {direction} labelled
"{phenomenon name}" onto the {surface/region}.
```

### R-3: 단위 셀 / 강조 영역

```
In panel {N}'s top view, highlight one {dimension} unit cell with a
dashed red square and label it "{label}".
```

### R-4: 결정학 표기

```
Replace the X/Y axis arrows with the conventional crystallographic
indices [100] / [010] / [001].
```

### R-5: 레이아웃 조정

```
Move the legend to the {right side | bottom} of the figure as a
{vertical | horizontal} bar.
```

### R-6: 비교·그룹화

```
Group panels {a}, {b}, {c} with a {color} dashed rectangle and label
them "{group name} — see {document § X}".
```

### R-7: 마스크 정렬 강조

```
Add an annotation arrow between mask M{X} and M{Y} stating:
"Overlay tolerance ≤ {value} nm 3σ on {tool name}".
```

### R-8: 파라미터 박스 추가

```
Add a small parameter table in the {position} corner showing:
- {param 1}: {value}
- {param 2}: {value}
- ...
```

## Design 접근 불가 시 대안 (백업)

| 도구 | 장점 | 단점 |
|---|---|---|
| **Inkscape** | 오픈소스, SVG 표준, 인쇄 품질 | 학습 곡선 |
| **TikZ in LaTeX** | 논문 임베드 최적, 재현 가능 | 코드 작성 시간 |
| **draw.io / diagrams.net** | 무료·웹·간편 | 학술 도식 스타일 한계 |
| **PowerPoint** | 즉시 사용, 단계별 슬라이드 가능 | 정밀도·스케일 부정확 |
| **Origin / Igor Pro** | 데이터 함께 plot 가능 | fab flow 같은 stepwise 그림에는 부적합 |

**권장 흐름**: claude.ai/design 으로 시작점 생성 → Inkscape 로 미세 조정 (라벨·정렬·치수). 또는 TikZ 로 처음부터.

## 결과물 저장 + 본문 통합

### 1. 저장 경로 (표준)

```
$VAULT\0. Inbox\Files\
```

파일명 규칙: `{프로젝트}_{Fig번호}_{내용}.{확장자}`

예시:
- `MF_Report_Fig1c_SADP_workflow.pdf`
- `MF_Report_Fig3a_process_flow.pdf`
- `OHE_Exp_Fig1_HallBar_fabrication.pdf`
- `SiC_RIE_dose_ladder_protocol.pdf`

### 2. 본문 노트에 wikilink

```markdown
![[MF_Report_Fig1c_SADP_workflow.pdf]]
*Fig. (1-c). SADP × SADP 12 단계 흐름 (Claude Design 생성, 2026-05-26).*
```

Obsidian 은 PDF embed 를 자동 인식. PNG 도 동일.

### 3. 메타데이터 보존

각 figure 의 prompt + refinements 는 별도 .md 로 저장 권장:
- 위치: 원본 노트와 동일 디렉토리, 파일명 `{원본}_Design_Prompts.md`
- 본 모듈의 frontmatter `example_artifacts` 에 추가

## 좋은 예시 (재사용 reference)

### 1) MF Report (2026-06-15) — Professor D 레포트 과제

- **위치**: `[[2026-06-15 MF Report — Claude Design Prompts]]`
- **P-1**: SADP × SADP 12 패널 단면도 — 패턴 A (단계별 단면도) 골격 적용
- **P-2**: MOS 게이트 적층 15 단계 + Top view + 마스크 — 패턴 A + 패턴 B 결합

### 2) (향후 추가 예정)

- 실험 프로토콜: OHE in SiC Hall bar 제작 단계 시각화
- 측정 워크플로우: ST-FMR + 2nd-harmonic Hall 분석 흐름
- 비교 도식: NEB22 단일 도포 vs 2 단계 spin coating

## 트러블슈팅

| 증상 | 원인 | 대응 |
|---|---|---|
| Design 결과의 색상이 prompt 와 다름 | 색상명만 적고 hex 누락 | hex code 명시 (예: `#D8D8D8`) |
| 패널 순서가 뒤바뀜 | "left-to-right, top-to-bottom" 명시 안 됨 | Layout 섹션에 grid 순서 명시 |
| Scale bar 누락 | 명시적 요구 없음 | Style 섹션에 "Scale bar `{value}` in bottom-right of every panel" 추가 |
| 라벨 글자 깨짐 | 해상도 부족 | "300 dpi" 명시 + PPTX 동시 export 로 라벨 재편집 |
| 단계가 너무 압축됨 | 패널 수가 grid 에 비해 적음 | rows × cols 명시 + 패널 크기 비율 명시 |
| PDF embed 시 Obsidian 인식 안 됨 | 파일명 공백 / 한글 | 영문·언더스코어 권장 |

## 인용·저작권 표기

생성된 figure 가 학술 보고서·논문에 포함될 때:

- **하단 캡션에 명기**: "Generated with Claude Design (Anthropic), {YYYY-MM-DD}."
- **본문 인용은 일반 reference 와 동일** — Design 자체는 1 차 출처가 아닌 도구
- **AI 사용 신고** 가 요구되는 경우: 본인 작업 vs AI 작업의 분리 명시 (예: [[2026-06-15 MF Report — Plasma Etching & Microfabrication [EN]]] 의 "Declaration of generative-AI usage" 섹션 참조)

## 모듈 갱신 정책

본 모듈은 **Claude Design 자체의 기능 변경**, 또는 **새로운 prompt 패턴이 유용함이 확인된 경우** 갱신:

- 신규 패턴 추가: § "Prompt 골격" 에 D, E, ... 로 확장
- Refinements 패턴 추가: § "Refinements 패턴" 에 R-9, R-10, ...
- 좋은 예시 추가: § "좋은 예시" 에 wikilink

갱신 시 `updated:` frontmatter 날짜 변경 + 본 § "모듈 갱신 정책" 하단에 변경 이력 1 줄 추가.

### 변경 이력

- 2026-05-26: 초판 작성 (MF Report 6/15 과제 작성 중 패턴 추출)
