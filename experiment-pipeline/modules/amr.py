"""
AMR (Anisotropic Magneto-Resistance) 측정 처리.

표준 4 함수 인터페이스 (modules/__init__.py 참조):
    load(raw_dir) -> dict
    fit(loaded) -> dict
    plot(loaded, fitted, out_dir) -> list[Path]
    export(loaded, fitted, out_dir) -> None

본 구현은 *골격* (skeleton). 기존 AMR.ipynb 의 핵심 함수를 추출해 채워야 함.

모델:
    V_xx(theta) = V_0 + V_AMR * cos²(theta - phi)
    또는
    V_xx(theta) = V_0 + V_AMR * cos(2*(theta - phi))
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from . import common


MODULE_VERSION = "0.1.0-skeleton"


# =============================================================================
# 1. load
# =============================================================================

def load(raw_dir: Path) -> dict:
    """00_raw/ 의 AMR 측정 raw 파일들을 로드.

    예상 raw 포맷:
        - 컬럼: angle [deg], V_xx [V] (또는 R [Ω]), 가능하면 V_xy
        - 헤더는 # 또는 % 로 시작하는 코멘트 가능
        - 파일이 여러 개면 *averaging* 또는 *iteration* 단위

    Returns:
        {
            'data': pd.DataFrame,    # columns: angle_deg, V_xx, (V_xy)
            'metadata': dict,        # raw 파일 헤더에서 추출 (옵션)
        }
    """
    raw_dir = Path(raw_dir)
    files = common.list_raw_files(raw_dir)
    if not files:
        raise FileNotFoundError(f"No raw files in {raw_dir}")

    dfs = []
    for f in files:
        df = common.load_csv_safe(f)
        # 컬럼명 정규화 (가능하면)
        df.columns = [str(c).strip() for c in df.columns]
        df['_source'] = f.name
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)

    # 표준 컬럼명 추정
    rename_map = {}
    for c in data.columns:
        lc = c.lower()
        if 'angle' in lc or 'theta' in lc or 'deg' in lc:
            rename_map[c] = 'angle_deg'
        elif 'v_xx' in lc or 'vxx' in lc or 'r_xx' in lc:
            rename_map[c] = 'V_xx'
        elif 'v_xy' in lc or 'vxy' in lc or 'r_xy' in lc:
            rename_map[c] = 'V_xy'
    data = data.rename(columns=rename_map)

    metadata = {
        'n_files': len(files),
        'n_points_total': len(data),
        'source_files': [f.name for f in files],
    }
    return {'data': data, 'metadata': metadata}


# =============================================================================
# 2. fit
# =============================================================================

def _amr_model(theta_deg: np.ndarray, V0: float, V_amr: float, phi_deg: float) -> np.ndarray:
    """V_xx = V0 + V_amr * cos²(θ - φ)"""
    theta_rad = np.deg2rad(theta_deg)
    phi_rad = np.deg2rad(phi_deg)
    return V0 + V_amr * np.cos(theta_rad - phi_rad) ** 2


def fit(loaded: dict) -> dict:
    """V_xx(θ) 에 cos² fit.

    Returns:
        {
            'fit_results': pd.DataFrame,
            'metrics': {'R2': ..., 'amplitude_uV': ..., 'phase_deg': ..., 'offset_uV': ...},
            'model': 'V_xx = V0 + V_amr * cos²(θ - φ)',
            'fit_curve': pd.DataFrame,   # θ vs fit 값 (플롯용)
        }
    """
    from scipy.optimize import curve_fit

    data = loaded['data'].copy()
    if 'angle_deg' not in data.columns or 'V_xx' not in data.columns:
        raise ValueError(f"Required columns missing. Got: {list(data.columns)}")

    # 평균 (averaging if duplicates)
    grouped = data.groupby('angle_deg', as_index=False)['V_xx'].mean()
    grouped = grouped.sort_values('angle_deg').reset_index(drop=True)

    theta = grouped['angle_deg'].to_numpy()
    V = grouped['V_xx'].to_numpy()

    # 초기 추정
    V0_init = float(np.mean(V))
    V_amr_init = float(np.ptp(V))   # peak-to-peak
    phi_init = float(theta[np.argmax(V)])

    try:
        popt, pcov = curve_fit(
            _amr_model, theta, V,
            p0=[V0_init, V_amr_init, phi_init],
            maxfev=10000,
        )
        V0_fit, V_amr_fit, phi_fit = popt
        perr = np.sqrt(np.diag(pcov))
    except Exception as e:
        # 실패 시: 단순 추정값으로 반환
        V0_fit, V_amr_fit, phi_fit = V0_init, V_amr_init, phi_init
        perr = np.array([np.nan, np.nan, np.nan])
        print(f"[amr.fit] curve_fit failed: {e}. Using initial estimates.")

    # R²
    V_pred = _amr_model(theta, V0_fit, V_amr_fit, phi_fit)
    ss_res = float(np.sum((V - V_pred) ** 2))
    ss_tot = float(np.sum((V - np.mean(V)) ** 2))
    R2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')

    # 결과 패키지
    fit_results = pd.DataFrame({
        'parameter': ['V0', 'V_amr', 'phi'],
        'value': [V0_fit, V_amr_fit, phi_fit],
        'std_err': perr,
        'unit': ['V', 'V', 'deg'],
    })

    # μV 변환 (raw 가 V 일 때)
    amplitude_uV = float(V_amr_fit * 1e6)
    offset_uV = float(V0_fit * 1e6)

    metrics = {
        'R2': float(R2),
        'amplitude_uV': amplitude_uV,
        'phase_deg': float(phi_fit % 180.0),
        'offset_uV': offset_uV,
        'n_points': int(len(theta)),
    }

    # 플롯용 fit curve (smooth)
    theta_smooth = np.linspace(theta.min(), theta.max(), 360)
    V_smooth = _amr_model(theta_smooth, V0_fit, V_amr_fit, phi_fit)
    fit_curve = pd.DataFrame({'angle_deg': theta_smooth, 'V_xx_fit': V_smooth})

    return {
        'fit_results': fit_results,
        'metrics': metrics,
        'model': 'V_xx = V0 + V_amr * cos²(θ - φ)',
        'fit_curve': fit_curve,
        'data_averaged': grouped,
    }


# =============================================================================
# 3. plot
# =============================================================================

def plot(loaded: dict, fitted: dict, out_dir: Path) -> list[Path]:
    """표준 4 플롯 저장."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("matplotlib not installed — install via `pip install matplotlib`")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    common.apply_plot_style()

    data = loaded['data']
    avg = fitted['data_averaged']
    curve = fitted['fit_curve']
    metrics = fitted['metrics']

    saved = []

    # (1) raw overlay
    fig, ax = plt.subplots()
    for src, df_sub in data.groupby('_source'):
        ax.plot(df_sub['angle_deg'], df_sub['V_xx'] * 1e6, '.', alpha=0.5, label=src, markersize=3)
    ax.set_xlabel('Angle θ (deg)')
    ax.set_ylabel('V_xx (μV)')
    ax.set_title('Raw data overlay')
    ax.legend(fontsize=8, loc='best')
    path1 = out_dir / 'raw_overlay.png'
    fig.savefig(path1)
    plt.close(fig)
    saved.append(path1)

    # (2) fit
    fig, ax = plt.subplots()
    ax.plot(avg['angle_deg'], avg['V_xx'] * 1e6, 'o', color=common.COLOR_DATA, label='data (averaged)')
    ax.plot(curve['angle_deg'], curve['V_xx_fit'] * 1e6, '-', color=common.COLOR_FIT, label='cos² fit')
    ax.set_xlabel('Angle θ (deg)')
    ax.set_ylabel('V_xx (μV)')
    ax.set_title(f"AMR fit — R² = {metrics['R2']:.4f}, A = {metrics['amplitude_uV']:.2f} μV")
    ax.legend()
    path2 = out_dir / 'fit.png'
    fig.savefig(path2)
    plt.close(fig)
    saved.append(path2)

    # (3) residuals
    V_pred = np.interp(avg['angle_deg'], curve['angle_deg'], curve['V_xx_fit'])
    residuals_uV = (avg['V_xx'].to_numpy() - V_pred) * 1e6
    fig, ax = plt.subplots()
    ax.plot(avg['angle_deg'], residuals_uV, 'o-', color=common.COLOR_RESIDUAL)
    ax.axhline(0, color='k', lw=0.5)
    ax.set_xlabel('Angle θ (deg)')
    ax.set_ylabel('Residuals (μV)')
    ax.set_title('Fit residuals')
    path3 = out_dir / 'residuals.png'
    fig.savefig(path3)
    plt.close(fig)
    saved.append(path3)

    # (4) summary
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    # 2x2 grid: raw / fit / residuals / metrics text
    axes[0, 0].plot(data['angle_deg'], data['V_xx'] * 1e6, '.', color=common.COLOR_DATA, markersize=2)
    axes[0, 0].set_title('Raw'); axes[0, 0].set_xlabel('θ (deg)'); axes[0, 0].set_ylabel('V_xx (μV)')
    axes[0, 1].plot(avg['angle_deg'], avg['V_xx'] * 1e6, 'o', color=common.COLOR_DATA, label='data')
    axes[0, 1].plot(curve['angle_deg'], curve['V_xx_fit'] * 1e6, '-', color=common.COLOR_FIT, label='fit')
    axes[0, 1].set_title('Fit'); axes[0, 1].legend(); axes[0, 1].set_xlabel('θ (deg)'); axes[0, 1].set_ylabel('V_xx (μV)')
    axes[1, 0].plot(avg['angle_deg'], residuals_uV, 'o-', color=common.COLOR_RESIDUAL)
    axes[1, 0].axhline(0, color='k', lw=0.5)
    axes[1, 0].set_title('Residuals'); axes[1, 0].set_xlabel('θ (deg)'); axes[1, 0].set_ylabel('μV')
    axes[1, 1].axis('off')
    summary_text = (
        f"AMR fit metrics\n"
        f"───────────────\n"
        f"R²        = {metrics['R2']:.4f}\n"
        f"Amplitude = {metrics['amplitude_uV']:.2f} μV\n"
        f"Phase     = {metrics['phase_deg']:.2f}°\n"
        f"Offset    = {metrics['offset_uV']:.2f} μV\n"
        f"N points  = {metrics['n_points']}\n"
        f"\n"
        f"Model:\n  V_xx = V0 + V_amr · cos²(θ − φ)"
    )
    axes[1, 1].text(0.05, 0.95, summary_text, transform=axes[1, 1].transAxes,
                    verticalalignment='top', family='monospace', fontsize=10)
    fig.tight_layout()
    path4 = out_dir / 'summary.png'
    fig.savefig(path4)
    plt.close(fig)
    saved.append(path4)

    return saved


# =============================================================================
# 4. export
# =============================================================================

def export(loaded: dict, fitted: dict, out_dir: Path) -> None:
    """01_processed/ 에 fit_results.csv + metrics.json + processing_log.json."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fitted['fit_results'].to_csv(out_dir / 'fit_results.csv', index=False)
    fitted['data_averaged'].to_csv(out_dir / 'data_averaged.csv', index=False)
    fitted['fit_curve'].to_csv(out_dir / 'fit_curve.csv', index=False)

    metrics_full = {
        **fitted['metrics'],
        'model': fitted['model'],
        'metadata': loaded.get('metadata', {}),
    }
    (out_dir / 'metrics.json').write_text(
        json.dumps(metrics_full, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    common.write_processing_log(
        out_dir, module_name='amr', module_version=MODULE_VERSION,
        extra={'n_input_files': loaded.get('metadata', {}).get('n_files')},
    )
