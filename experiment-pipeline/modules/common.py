"""
공통 유틸 — raw loader, plot 스타일, frontmatter 파서.

모든 측정 종류 모듈이 의존하는 *기반 유틸*.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


# =============================================================================
# Raw 데이터 로더
# =============================================================================

def list_raw_files(raw_dir: Path, exts: tuple[str, ...] = ('.csv', '.dat', '.txt', '.tsv')) -> list[Path]:
    """raw_dir 안의 데이터 파일 목록 (확장자 필터)."""
    raw_dir = Path(raw_dir)
    if not raw_dir.exists():
        raise FileNotFoundError(f"raw_dir not found: {raw_dir}")
    return sorted([p for p in raw_dir.iterdir() if p.suffix.lower() in exts])


def load_csv_safe(path: Path, **read_kwargs) -> pd.DataFrame:
    """다양한 구분자 / 헤더 옵션을 자동 시도하는 안전한 CSV 로더."""
    path = Path(path)
    # 시도 순서: 콤마 → 탭 → 공백 (whitespace)
    last_err = None
    for sep, comment_chars in [(',', '#%'), ('\t', '#%'), (r'\s+', '#%')]:
        try:
            df = pd.read_csv(path, sep=sep, comment=comment_chars[0], engine='python', **read_kwargs)
            if len(df.columns) >= 2:
                return df
        except Exception as e:
            last_err = e
            continue
    raise ValueError(f"Could not parse {path}. Last error: {last_err}")


# =============================================================================
# Plot 스타일 (학술 출판 풍)
# =============================================================================

PLOT_STYLE = {
    'figure.figsize': (6, 4),
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.family': 'Helvetica, Arial, sans-serif',
    'font.size': 11,
    'axes.linewidth': 1.0,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.labelsize': 12,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'legend.frameon': False,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
}

# 색상 — Sony Vault 의 학술 출판물 풍과 일관
COLOR_DATA = '#1976D2'      # 파랑 — 측정 데이터
COLOR_FIT = '#D32F2F'        # 빨강 — fit 곡선
COLOR_ACCENT = '#2E7D32'     # 녹색 — 결론·강조
COLOR_RESIDUAL = '#7A7A7A'   # 회색 — 잔차


def apply_plot_style():
    """학술 출판 풍 matplotlib 스타일 적용."""
    if plt is None:
        raise ImportError("matplotlib not installed")
    plt.rcParams.update(PLOT_STYLE)


# =============================================================================
# Frontmatter 파서 (README.md ↔ Obsidian 노트)
# =============================================================================

def parse_frontmatter(md_path: Path) -> dict:
    """Obsidian 풍 YAML frontmatter 파싱."""
    md_path = Path(md_path)
    if not md_path.exists():
        return {}
    text = md_path.read_text(encoding='utf-8')
    if not text.startswith('---'):
        return {}
    try:
        end = text.index('---', 3)
        yaml_text = text[3:end].strip()
    except ValueError:
        return {}
    try:
        import yaml
        return yaml.safe_load(yaml_text) or {}
    except ImportError:
        # 최소 파서 (1-depth 만)
        result = {}
        for line in yaml_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                result[k.strip()] = v.strip().strip('"\'')
        return result


def write_frontmatter(md_path: Path, frontmatter: dict, body: str = '') -> None:
    """frontmatter + body 를 .md 로 저장."""
    md_path = Path(md_path)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import yaml
        yaml_text = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    except ImportError:
        lines = []
        for k, v in frontmatter.items():
            if isinstance(v, (str, int, float, bool)):
                lines.append(f"{k}: {v}")
            else:
                lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
        yaml_text = '\n'.join(lines) + '\n'
    md_path.write_text(f"---\n{yaml_text}---\n\n{body}", encoding='utf-8')


# =============================================================================
# 처리 로그 (재현성)
# =============================================================================

def write_processing_log(out_dir: Path, module_name: str, module_version: str, extra: dict | None = None) -> None:
    """01_processed/processing_log.json — 재현성 확보용."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log = {
        'module': module_name,
        'module_version': module_version,
        'timestamp_iso': datetime.now().isoformat(),
        'python_executable': str(Path(os.sys.executable)),
        'python_version': os.sys.version.split()[0],
        'numpy_version': np.__version__,
        'pandas_version': pd.__version__,
        'extra': extra or {},
    }
    (out_dir / 'processing_log.json').write_text(
        json.dumps(log, indent=2, ensure_ascii=False), encoding='utf-8'
    )


# =============================================================================
# 표준 폴더 구조 보장
# =============================================================================

STANDARD_SUBDIRS = ['00_raw', '01_processed', '01_processed/plots', '02_notebooks']


def ensure_project_structure(project_path: Path) -> Path:
    """표준 4단 폴더 구조 생성·검증."""
    project_path = Path(project_path)
    for sub in STANDARD_SUBDIRS:
        (project_path / sub).mkdir(parents=True, exist_ok=True)
    return project_path


def lock_raw_readonly(raw_dir: Path) -> None:
    """Windows: 00_raw/ 의 모든 파일에 *읽기 전용* 속성 설정."""
    raw_dir = Path(raw_dir)
    if not raw_dir.exists():
        return
    for f in raw_dir.rglob('*'):
        if f.is_file():
            try:
                # Python 의 os.chmod 는 Windows 에서 *읽기 전용* 만 의미
                f.chmod(f.stat().st_mode & ~0o222)  # write 권한 제거
            except Exception:
                pass
