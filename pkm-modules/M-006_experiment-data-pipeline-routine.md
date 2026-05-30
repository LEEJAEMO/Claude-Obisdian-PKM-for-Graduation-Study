---
type: pkm-module
id: M-006
title: 실험 데이터 자동화 파이프라인 루틴 (raw → processed → Obsidian)
domain: [experiment, research-data, automation, python, obsidian-sync]
task_type: workflow
input: "실험실 PC 의 raw 데이터 폴더 + 프로젝트명 + 측정 종류 + 샘플 ID"
output: "6. Experiment/4. Project/<project>/<date-meas>/<sample>/ 표준 구조 (00_raw + 01_processed + 02_notebooks) + Obsidian Vault 측정 노트 자동 생성 (frontmatter + plot 임베드)"
related_command: ""
related_spec: ""
related_agent: ""
related_system_root: "$EXPERIMENT_ROOT/"
related_vault_root: "Obsidian Vault/1. Project/대학원 공부/2. 연구 (Research)/2. Experiment/"
created: 2026-05-29
updated: 2026-05-29
---

# M-006 — 실험 데이터 자동화 파이프라인 루틴

> **재사용 목적**: 실험실 컴퓨터에서 받아온 raw 데이터를 (a) **무결성을 보존하며** (b) **표준 파이프라인으로 자동 처리** 하고 (c) **Obsidian 측정 노트로 자동 동기화** 하는 *반복 워크플로우* 의 단일 정본.

> **이 문서가 실험 데이터 워크플로우의 구조·인터페이스·동기화 정책의 정본** — 새 측정 추가 / 새 모듈 작성 / 새 프로젝트 시작 시 본 모듈을 명시적으로 참조.

---

## 트리거

- 실험실 PC 에서 측정 raw 를 받아온 직후 — *"이 측정 데이터 처리해줘"* / *"오늘 측정 자동화 돌려줘"*
- 새 측정 종류 모듈 추가 — *"AHE 모듈도 같은 인터페이스로 만들어줘"*
- 새 프로젝트 폴더 시작 — *"이 새 시리즈 실험 표준 구조로 잡아줘"*
- Obsidian 측 노트 갱신 — *"sync_to_obsidian 한 번 돌려줘"*

## 1차 소스 원칙

- **`00_raw/` 는 READ-ONLY** — 절대 수정·삭제 금지. 자동화 스크립트가 권한 강제 (`common.lock_raw_readonly()`).
- **처리 결과만 `01_processed/`** — *재실행 가능* (raw 만으로 복원 가능해야 함).
- **`README.md` frontmatter = single source of truth** — 측정 메타데이터·조건·fit 결과 모두 여기서 출발.
- **Obsidian 노트는 *처리 후* 생성** — 검색·인덱스 가치 있는 *결과 포함* 노트만.

## 단계 요약

| Step | 작업 |
|------|------|
| 0 | 사용자 입력 확인 — src 경로 / 프로젝트명 / 측정 종류 / 샘플 ID / 측정 날짜 |
| 1 | `import_raw.py` — 실험실 PC 의 raw 를 `4. Project/<project>/<YYYY-MM-DD>-<measurement>/<sample>/00_raw/` 로 복사 + 체크섬 + READ-ONLY + README.md 자동 생성 |
| 2 | 사용자가 README.md frontmatter 의 `conditions` 보강 (temperature, field, ...) — *선택* |
| 3 | `process_data.py` — README 의 `measurement_type` 으로 모듈 (`amr`, `ahe`, ...) 선택 → `load() → fit() → plot() → export()` 4 함수 순차 호출 |
| 4 | `sync_to_obsidian.py` — `01_processed/metrics.json` 읽어 Obsidian 측 측정 노트 자동 생성·갱신. PNG 를 `0. Inbox/Files/` 로 복사. 본문 수동 영역은 보존 |
| 5 | 사용자가 Obsidian 노트의 *실험 목적*, *고찰*, *다음 단계* 수동 기입 |
| 6 | (장기) 시스템 측 README 갱신 시 `sync_readmes_to_vault.py` 로 Vault 측 사본 동기화 |

## 시스템 폴더 구조 (정본)

### Vault 외부 — 실제 데이터·스크립트

```
6. Experiment/                                ← 시스템 측 루트
├── README.md                                 ← 시스템 설계서 (정본)
├── 0. inbox/                                  ← 임시 / 미분류
├── 1. AutoCad/
├── 2. VESTA-win64/  /  2.1. VESTA/
├── 3. Wafer Data/
├── 4. Project/                                ← ★ 실험 데이터 (raw + processed) ★
│   └── <장기 프로젝트명>/                       ← 예: "3. Cryo", "2026-05-20 SiC Dose-MillingRate"
│       └── <YYYY-MM-DD>-<측정종류>/             ← 예: "2026-05-25-AMR"
│           └── <샘플 ID>/                       ← 예: "sample-A"
│               ├── README.md                   ← frontmatter (메타)
│               ├── 00_raw/                     ← READ-ONLY raw
│               │   └── .checksums.json         ← 체크섬 (중복 import 방지)
│               ├── 01_processed/
│               │   ├── fit_results.csv
│               │   ├── data_averaged.csv
│               │   ├── fit_curve.csv
│               │   ├── metrics.json
│               │   ├── processing_log.json     ← 모듈 버전·환경
│               │   └── plots/
│               │       ├── raw_overlay.png
│               │       ├── fit.png
│               │       ├── residuals.png
│               │       └── summary.png
│               └── 02_notebooks/
│                   └── analysis.ipynb
├── 5. Experiment Manuals/
└── 6. Fitting Script/                         ← ★ 재사용 모듈·스크립트 ★
    ├── README.md
    ├── modules/                                ← 재사용 가능 (import 대상)
    │   ├── __init__.py                         ← 표준 인터페이스 명세
    │   ├── common.py                           ← raw loader, plot 스타일, frontmatter, lock
    │   ├── amr.py                              ← AMR 처리 (표준 4 함수)
    │   ├── ahe.py                              ← (예정)
    │   └── moke.py                             ← (예정)
    ├── templates/
    │   ├── notebook_template.ipynb
    │   └── obsidian_template.md
    └── scripts/                                ← CLI 진입점
        ├── import_raw.py                       ← 실험실 PC → 본 폴더
        ├── process_data.py                     ← 자동 처리
        ├── sync_to_obsidian.py                 ← Obsidian 노트 동기화
        └── sync_readmes_to_vault.py            ← README 사본 동기화
```

### Vault 내부 — 메타데이터·기록

```
Obsidian Vault/1. Project/대학원 공부/2. 연구 (Research)/2. Experiment/
├── !Experiment Index.md                       ← Dataview 자동 인덱스
├── 2.1 Samples/
├── 2.2 Experimental Manual/
├── 2.3 Experiment log/                        ← ★ 측정 노트 (sync_to_obsidian.py 대상) ★
│   ├── Hayashi 재현실험/
│   ├── SiC 기초물성 측정/
│   └── <project>/                              ← 자동 생성
│       └── YYYY-MM-DD <측정> <샘플>.md          ← 자동 생성
├── 2.4 Experiment Plan/
├── 2026-05-29 실험 데이터 자동화 시스템 안내.md  ← 사용자 운영 가이드
└── 시스템 문서/                                 ← README 사본 (sync_readmes_to_vault.py 대상)
    ├── !시스템 문서 인덱스.md
    ├── 6. Experiment — 시스템 설계 (사본).md
    └── 6. Fitting Script — 모듈 안내 (사본).md
```

## 표준 4 함수 인터페이스 (모든 측정 모듈 공통)

모든 `modules/<measurement>.py` (amr, ahe, moke, xrd 등) 는 **동일한 4 함수** 를 노출:

```python
def load(raw_dir: Path) -> dict:
    """raw_dir 의 모든 raw 파일 로드.
    Returns: {'data': pd.DataFrame, 'metadata': dict}
    """

def fit(loaded: dict) -> dict:
    """fit 실행.
    Returns: {
        'fit_results': pd.DataFrame,
        'metrics': {'R2': ..., 'amplitude_uV': ..., ...},
        'model': str,
        'fit_curve': pd.DataFrame,
        'data_averaged': pd.DataFrame,
    }
    """

def plot(loaded: dict, fitted: dict, out_dir: Path) -> list[Path]:
    """표준 4 플롯 저장 — raw_overlay / fit / residuals / summary.
    Returns: 저장된 파일 경로 리스트
    """

def export(loaded: dict, fitted: dict, out_dir: Path) -> None:
    """01_processed/ 에 fit_results.csv + metrics.json + processing_log.json 저장."""
```

→ `process_data.py` 가 README 의 `measurement_type` 으로 동적 import 후 4 함수 순차 호출.

**새 측정 종류 추가 시**: `modules/<name>.py` 만 작성. CLI 변경 불필요.

## CLI 사용 패턴

### 워크플로우 1 — 새 측정 (Phase 2 완전 자동화)

```bash
cd "$EXPERIMENT_ROOT/6. Fitting Script/scripts"

# 1. 실험실 PC → 본 폴더
python import_raw.py \
  --src "Z:/measurement_pc/2026-05-29/" \
  --project "3. Cryo" \
  --measurement "AMR" \
  --sample "sample-A" \
  --equipment "PPMS"

# 2. (선택) README.md 의 conditions 보강
# Obsidian 또는 텍스트 에디터로 frontmatter 수정

# 3. 자동 처리
python process_data.py \
  --project_path "../../4. Project/3. Cryo/2026-05-29-AMR/sample-A"

# 4. Obsidian 동기화
python sync_to_obsidian.py \
  --project_path "../../4. Project/3. Cryo/2026-05-29-AMR/sample-A"
```

### 워크플로우 2 — 기존 데이터 재처리 (모듈 업데이트 후 등)

```bash
# 처리 + 동기화만
python process_data.py --project_path <기존 project>
python sync_to_obsidian.py --project_path <기존 project>
```

### 워크플로우 3 — README 사본 동기화

```bash
# 시스템 측 README 가 갱신됐을 때
python sync_readmes_to_vault.py --dry-run    # 미리보기
python sync_readmes_to_vault.py              # 실제 동기화
```

## Obsidian 측정 노트 frontmatter 표준

```yaml
type: experiment-note
subtype: measurement
date: 2026-05-29
project: 3. Cryo
sample: sample-A
measurement_type: AMR
equipment: PPMS
conditions:
  temperature: 20K
  field_range: ±9 T
  excitation: 0 mA AC, 900 Oe DC
  averages: 3
data_root: "6. Experiment/4. Project/3. Cryo/2026-05-29-AMR/sample-A"
fit_results:
  R2: 0.998
  amplitude_uV: 12.4
  phase_deg: 87.2
  offset_uV: 0.5
status: processed
research_themes: [OHE, 3C-SiC]
related_papers: ["[[@HayashiEtAl2023CommunPhys...]]"]
tags: [experiment, AMR, "3. Cryo"]
last_synced: 2026-05-29T15:30:42
```

→ Dataview 가 `!Experiment Index.md` 에서 자동 인덱스.
→ `data_root` 필드로 6. Experiment 측 폴더 **왕복 추적** 가능.

## 자동 영역 vs 수동 영역 정책

`sync_to_obsidian.py` 의 *2 차 이상 실행* 시:

| 영역 | 자동 갱신 | 수동 보존 |
|------|---------|---------|
| frontmatter 의 `fit_results`, `last_synced`, `conditions`, `data_root` | ✅ | — |
| frontmatter 의 `research_themes`, `related_papers`, `tags` (사용자 추가분) | — | ✅ |
| 본문 의 자동 생성 영역 (조건 표, fit 결과 표, plot 임베드) | — (2차 실행 시 본문 전체 보존) | ✅ |
| 본문 의 `## 실험 목적`, `## 고찰`, `## 다음 단계` | — | ✅ |

`--force-overwrite` 플래그 사용 시에만 본문 전체 덮어쓰기.

## 깊이 가이드라인 (모듈 작성 시)

### 패턴 1 — 표준 4 함수 형태 엄수

모든 측정 모듈은 *반드시* `load → fit → plot → export` 4 함수만 노출. 보조 함수는 *private* (`_` prefix).

이유: `process_data.py` 의 *동적 import* 가 이 형태에만 작동. 일관성 깨면 CLI 가 측정마다 분기 처리 필요 → 유지보수 폭증.

### 패턴 2 — Type hint + docstring 필수

각 함수는 다음 골격 따름:

```python
def fit(loaded: dict) -> dict:
    """한 줄 설명.

    Args:
        loaded: load() 의 반환값. 'data' (DataFrame) + 'metadata' (dict) 키.

    Returns:
        dict with keys:
            - 'fit_results': DataFrame [parameter, value, std_err, unit]
            - 'metrics': dict with R2, amplitude_uV, phase_deg, offset_uV
            - 'model': str describing the fit model
            - 'fit_curve': DataFrame for plotting (angle_deg, V_xx_fit)
            - 'data_averaged': DataFrame (raw 가 multi-file 일 때 평균)
    """
```

이유: VS Code / Jupyter 의 *자동완성* 가 동작. 협업·인계 비용 감소.

### 패턴 3 — 표준 플롯 4 종 강제

`plot()` 은 반드시 `raw_overlay.png`, `fit.png`, `residuals.png`, `summary.png` 4 종 저장.

이유: `sync_to_obsidian.py` 가 *고정 파일명* 으로 PNG 를 Obsidian 으로 복사. 다른 파일명이면 임베드 깨짐.

### 패턴 4 — `processing_log.json` 항상 작성

`export()` 안에서 `common.write_processing_log()` 호출. 모듈 버전 + Python·numpy·pandas 버전 + 실행 시간 기록.

이유: *재현성*. 6 개월 후 동일 데이터를 재처리해도 같은 결과 보장 확인 가능.

### 패턴 5 — `common.py` 의존 강제

raw loader, plot 스타일, frontmatter 파서 등은 *반드시* `from . import common` 으로 임포트.

이유: 학술 출판 풍 *일관 스타일*. 측정 종류마다 색·폰트가 다르면 비교 어렵.

## 언어·표기 정책

- 모든 .py 파일의 *주석·docstring 은 한국어 + 영어 혼용 OK* (변수명·함수명은 영어)
- README.md 들의 본문은 한국어 우선, 영어 병기
- Obsidian 측 노트는 *한국어 본문*, 단 frontmatter 의 *키* 는 영어 (Dataview 친화)
- *인명* / *프로젝트명* 은 사용자 표기 그대로 (예: "3. Cryo")

## 위험·주의사항

| 위험 | 대응 |
|------|------|
| `00_raw/` 의 READ-ONLY 가 OneDrive 동기화 방해 | Python `chmod` 의 *읽기 전용 속성* 만 사용 (Windows ACL 무관) — OneDrive 정상 동작 확인 |
| 측정 종류 다양화 시 모듈 폭증 | 4 함수 인터페이스 강제 — 새 측정도 *추가만*, 기존 코드 변경 없음 |
| Obsidian 측 노트의 수동 입력 손실 | sync 스크립트는 *기본적으로* 본문 보존. `--force-overwrite` 명시해야 덮어쓰기 |
| 시스템 README 갱신 시 Vault 사본 누락 | `sync_readmes_to_vault.py` 주기적 실행 (월 1회 권장) 또는 hook 화 |
| 처리 결과 버전 불일치 | `processing_log.json` 에 모듈 버전 기록 → 비교 가능 |
| 실험실 PC ↔ 본인 PC 동기화 누락 | `import_raw.py` 의 *체크섬 로그* (`.checksums.json`) 매번 확인 |
| 같은 사람이 같은 raw 를 두 번 import | 체크섬으로 자동 skip (skip 카운트로 확인) |

## 단계별 셋업 일정 (개선·확장 시)

### Phase 0 — 인프라 (2026-05-29 완료) ✅

- 시스템 측 README + Vault 측 사본 + 인덱스
- 표준 4 함수 인터페이스 명세 (`modules/__init__.py`)
- `common.py` (raw loader, plot 스타일, frontmatter 파서, READ-ONLY lock)
- 4 개 CLI 스크립트 (`import_raw`, `process_data`, `sync_to_obsidian`, `sync_readmes_to_vault`)

### Phase 1 — 첫 모듈 (Skeleton) ✅

- `modules/amr.py` 골격 (cos² fit, 표준 4 플롯)
- `templates/notebook_template.ipynb`
- `templates/obsidian_template.md`

### Phase 2 — 실측 데이터 적용 (대기 중)

- 기존 `2026-05-25-AMR / sample-A` 데이터로 워크플로우 검증
- `modules/amr.py` 의 fit 로직을 기존 `AMR.ipynb` 기준으로 보강
- Obsidian 노트 1 건 자동 생성 확인

### Phase 3 — 측정 종류 확장 (가변)

- `modules/ahe.py` (Anomalous Hall Effect)
- `modules/moke.py` (Magneto-Optic Kerr Effect)
- `modules/xrd.py` (X-Ray Diffraction)

### Phase 4 — Skills / Hook 통합 (선택, 6 개월 후)

- M-005 처럼 *Skill* 형태로 변환 → 자연어 ("AMR 데이터 처리해줘") 로 자동 발동
- `PostToolUse(Write)` hook 에서 `00_raw/` 권한 자동 lock

### Phase 5 — MCP 서버 (장기, 1 년 후)

- `mcp-experiment-data` 서버로 자연어 조작 가능화
- 자세한 계획: `999. Claude guideline/2026-05-29 Claude PKM 개선 방안.md` § 3

## 토큰 예산

- 새 측정 1 건 처리 + Obsidian 동기화: ~2,000 tokens (대부분 CLI 호출 + 결과 확인)
- 새 측정 종류 모듈 추가 (예: `ahe.py` 작성): ~10,000~15,000 tokens
- 시스템 전체 재설계: ~30,000 tokens (본 모듈 작성과 비슷)

## 관련 스킬·에이전트·모듈

- `M-005 — 반도체 기업 리서치 노트 작성 루틴` (별개 도메인이지만 *PKM 모듈화 패턴* 공유)
- `M-001 — 강의노트 작성 루틴` (frontmatter 정책 공유)
- `999. Claude guideline/2026-05-29 Claude PKM 개선 방안.md` § 3 (MCP 통합 장기 계획)

## 좋은 시스템의 표준 예시 (정본)

### `6. Experiment/` (2026-05-29 셋업, Phase 0~1 완료)

본받을 부분:
- **표준 폴더 구조 강제** — 모든 실험 세션이 동일 4 단 구조 (`00_raw/`, `01_processed/`, `02_notebooks/`, `README.md`)
- **표준 4 함수 인터페이스** — `process_data.py` 가 동적 import 로 어떤 측정도 처리 가능
- **frontmatter single source of truth** — README ↔ Obsidian 양방향 추적
- **README 사본 + 자동 동기화 스크립트** — Vault 외부 파일을 Vault 내부에서 열람 가능
- **`.checksums.json` 으로 중복 import 방지** — raw 무결성 보장

새 시스템 셋업 시 본 시스템의 §1.2 (Project 내부 표준 구조), §2 (3 단계 워크플로우), §모듈 인터페이스 표준을 *그대로 복제*.

## 에이전트 호출 시 명시할 항목 (체크리스트)

기존 모듈 추가 또는 새 측정 종류 작성 시 본 모듈을 명시:

- [ ] 표준 4 함수 인터페이스 (load/fit/plot/export) 엄수
- [ ] 표준 4 플롯 파일명 (`raw_overlay`, `fit`, `residuals`, `summary`)
- [ ] `common.py` 의존 (raw loader, plot 스타일, frontmatter, log)
- [ ] frontmatter 스키마 일치 (`measurement_type` 키 필수)
- [ ] `processing_log.json` 항상 작성 (재현성)
- [ ] Obsidian 측 본문의 수동 영역 보존 정책 준수
- [ ] 작업 완료 후 보고 항목:
  - 처리된 데이터 수
  - Obsidian 노트 경로
  - fit 메트릭 (R², amplitude, phase 등)
  - 생성된 플롯 파일 목록
  - 모듈 버전 + 환경 (`processing_log.json` 참조)

## 참고 — 개선 아이디어 (후속)

- *Hook*: `PostToolUse(Write)` 에서 `00_raw/` 가 *수정* 되면 경고
- *Lint*: README.md frontmatter 의 `measurement_type` 이 `modules/` 에 *없는* 값이면 경고
- *Dashboard*: `!Experiment Index.md` 에 *주간 진행 통계* (Dataview)
- *Backup*: `00_raw/` 의 *별도 외장 디스크 백업* 자동화
- *Citation*: 측정 노트 → 논문 figure 자동 매핑 (figure caption 에 데이터 출처 표시)
- *MCP*: 자연어 조작 (`"어제 AMR 처리해줘"`) — Phase 5
