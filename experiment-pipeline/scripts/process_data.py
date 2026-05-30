#!/usr/bin/env python
"""
process_data.py — 표준 프로젝트 폴더의 raw 데이터를 자동 처리.

사용:
    python process_data.py --project_path "../../4. Project/3. Cryo/2026-05-25-AMR/sample-A"
    python process_data.py --project_path <path> --module amr  # 명시적 모듈 선택

작동:
    1. project_path/README.md 에서 frontmatter 의 measurement_type 읽기
    2. 대응 모듈 로드 (amr, ahe, moke, ...)
    3. modules.<name>.load() → fit() → plot() → export()
    4. 01_processed/ + 01_processed/plots/ 자동 생성
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

# 모듈 경로 추가
SCRIPT_DIR = Path(__file__).parent
MODULES_PARENT = SCRIPT_DIR.parent
sys.path.insert(0, str(MODULES_PARENT))

from modules import common  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="실험 데이터 자동 처리")
    parser.add_argument('--project_path', required=True, type=Path,
                        help='프로젝트 폴더 (00_raw/ 가 있는 곳)')
    parser.add_argument('--module', default=None,
                        help='모듈명 (생략 시 README.md frontmatter 의 measurement_type 사용)')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 실행 없이 단계만 표시')
    args = parser.parse_args()

    project = args.project_path.resolve()
    if not project.exists():
        print(f"[ERROR] project_path not found: {project}")
        sys.exit(1)

    raw_dir = project / '00_raw'
    if not raw_dir.exists() or not any(raw_dir.iterdir()):
        print(f"[ERROR] No raw data in {raw_dir}")
        sys.exit(1)

    # 모듈 결정
    if args.module:
        module_name = args.module
    else:
        readme = project / 'README.md'
        if not readme.exists():
            print(f"[ERROR] README.md not found in {project} — specify --module")
            sys.exit(1)
        fm = common.parse_frontmatter(readme)
        module_name = fm.get('measurement_type', '').lower()
        if not module_name:
            print(f"[ERROR] measurement_type not in README.md frontmatter — specify --module")
            sys.exit(1)

    print(f"=== process_data.py ===")
    print(f"  project_path : {project}")
    print(f"  module       : {module_name}")
    print(f"  raw_dir      : {raw_dir}")

    if args.dry_run:
        print("[dry-run] 모듈 로드·처리 생략. 종료.")
        return

    # 모듈 동적 import
    try:
        module = importlib.import_module(f'modules.{module_name}')
    except ModuleNotFoundError:
        print(f"[ERROR] modules/{module_name}.py not found")
        sys.exit(1)

    # 4단계 처리
    print(f"\n[1/4] load() ...")
    loaded = module.load(raw_dir)
    print(f"      → {loaded.get('metadata', {})}")

    print(f"\n[2/4] fit() ...")
    fitted = module.fit(loaded)
    metrics = fitted.get('metrics', {})
    for k, v in metrics.items():
        print(f"      {k} = {v}")

    print(f"\n[3/4] plot() ...")
    plot_dir = project / '01_processed' / 'plots'
    saved_plots = module.plot(loaded, fitted, plot_dir)
    for p in saved_plots:
        print(f"      → {p.relative_to(project)}")

    print(f"\n[4/4] export() ...")
    module.export(loaded, fitted, project / '01_processed')
    print(f"      → 01_processed/fit_results.csv, metrics.json, processing_log.json")

    print(f"\n[DONE] {module_name} 처리 완료. Obsidian 동기화는 sync_to_obsidian.py 실행.")


if __name__ == '__main__':
    main()
