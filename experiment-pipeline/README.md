# 6. Fitting Script — 실험 데이터 처리 모듈

본 폴더는 `6. Experiment/` 시스템의 *데이터 처리 측* 모듈·스크립트 모음.
상위 시스템 설명: `6. Experiment/README.md`.

작성: 2026-05-29

---

## 구조

```
6. Fitting Script/
├── README.md                         ← 본 파일
├── AMR.ipynb                         ← 기존 노트북 (참고, 마이그레이션 예정)
├── result_plot.png                   ← 기존 산출물 (참고)
├── modules/                          ← 재사용 모듈 (import 가능)
│   ├── __init__.py
│   ├── common.py                     ← raw loader, plot 스타일, util
│   ├── amr.py                        ← AMR 측정 처리
│   ├── ahe.py                        ← AHE 측정 처리 (예정)
│   └── moke.py                       ← MOKE 측정 처리 (예정)
├── templates/
│   ├── notebook_template.ipynb       ← 새 측정 노트북 시작점
│   └── obsidian_template.md          ← Obsidian 측정 노트 템플릿
└── scripts/                          ← CLI 스크립트
    ├── import_raw.py                 ← 실험실 PC → 본 폴더로 raw 복사 + frontmatter
    ├── process_data.py               ← 자동 처리 실행
    └── sync_to_obsidian.py           ← Obsidian 노트 자동 생성·갱신
```

---

## 모듈 인터페이스 표준

모든 측정 종류의 모듈 (`modules/amr.py`, `modules/ahe.py` 등) 은 **공통 4 함수** 를 노출:

```python
# modules/amr.py 예시

def load(raw_dir: Path) -> dict:
    """00_raw/ 의 모든 파일을 로드해서 dict 반환.
    Returns:
        {
            'data': pd.DataFrame,         # columns: ['angle', 'V_xx', 'V_xy', ...]
            'metadata': {                 # 측정 조건
                'temperature_K': 20,
                'field_Oe': 900,
                'excitation_mA': 0,
                'averages': 3,
            }
        }
    """
    ...

def fit(loaded: dict) -> dict:
    """fit 실행, 결과 dict 반환.
    Returns:
        {
            'fit_results': pd.DataFrame,  # 컬럼별 fit 파라미터
            'metrics': {
                'R2': 0.998,
                'amplitude_uV': 12.4,
                'phase_deg': 87.2,
            },
            'model': '...',                # 사용한 모델 명세
        }
    """
    ...

def plot(loaded: dict, fitted: dict, out_dir: Path) -> list[Path]:
    """표준 플롯 4 종을 out_dir 에 저장. 저장된 파일 경로 리스트 반환.
    표준 플롯:
        - raw_overlay.png: 원본 데이터 overlay
        - fit.png: fit 결과 (data + curve)
        - residuals.png: 잔차
        - summary.png: 종합 (4 in 1)
    """
    ...

def export(loaded: dict, fitted: dict, out_dir: Path) -> None:
    """01_processed/ 에 표준 export.
    저장:
        - fit_results.csv
        - metrics.json
        - processing_log.json (modules 버전, 실행 시간, 환경)
    """
    ...
```

→ `scripts/process_data.py` 는 README.md frontmatter 의 `measurement_type` 으로 모듈 선택 후 위 4 함수 순차 호출.

---

## 사용 예 (수동, Phase 1)

```python
from pathlib import Path
import sys
sys.path.insert(0, r'$EXPERIMENT_ROOT\6. Fitting Script')

from modules import amr, common

project_path = Path(r'$EXPERIMENT_ROOT\4. Project\3. Cryo\2026-05-25-AMR\sample-A')

# 1. 로드
loaded = amr.load(project_path / '00_raw')

# 2. fit
fitted = amr.fit(loaded)

# 3. 플롯
amr.plot(loaded, fitted, project_path / '01_processed' / 'plots')

# 4. export
amr.export(loaded, fitted, project_path / '01_processed')

print(f"R² = {fitted['metrics']['R2']:.4f}")
print(f"Amplitude = {fitted['metrics']['amplitude_uV']:.2f} μV")
```

---

## CLI 사용 예 (Phase 2)

```bash
# 1. 실험실 PC → 본 폴더
python scripts/import_raw.py \
  --src "Z:/measurement_pc/2026-05-29/" \
  --project "3. Cryo" \
  --measurement "AMR" \
  --sample "sample-A"

# 2. 자동 처리
python scripts/process_data.py \
  --project_path "../4. Project/3. Cryo/2026-05-29-AMR/sample-A"

# 3. Obsidian 동기화
python scripts/sync_to_obsidian.py \
  --project_path "../4. Project/3. Cryo/2026-05-29-AMR/sample-A"
```

---

## 개발 우선순위

1. **`modules/common.py`** — 모든 모듈이 의존, 가장 먼저
2. **`modules/amr.py`** — 기존 AMR.ipynb 의 핵심 함수 추출
3. **`templates/notebook_template.ipynb`** — 새 분석 시작점
4. **`templates/obsidian_template.md`** — sync 스크립트가 사용
5. **`scripts/process_data.py`** — modules 호출 CLI
6. **`scripts/sync_to_obsidian.py`** — Obsidian 동기화
7. **`scripts/import_raw.py`** — 실험실 PC 연결 (네트워크 환경 확인 필요)

---

## 참고

- 상위 시스템: `../README.md`
- 기존 노트북: `AMR.ipynb` — 핵심 fit 로직 추출 대상
- PKM 통합 계획: `999. Claude guideline/2026-05-29 Claude PKM 개선 방안.md` § 3 (MCP 통합은 Phase 4)
