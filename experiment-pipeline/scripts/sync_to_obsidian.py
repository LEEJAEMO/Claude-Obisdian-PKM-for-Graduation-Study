#!/usr/bin/env python
"""
sync_to_obsidian.py — 처리 결과를 Obsidian 측정 노트로 자동 생성·갱신.

사용:
    python sync_to_obsidian.py --project_path "../../4. Project/3. Cryo/2026-05-25-AMR/sample-A"

작동:
    1. project_path/README.md + metrics.json 읽기
    2. Obsidian Vault 의 측정 노트 경로 결정:
       2.3 Experiment log/<project_name>/<YYYY-MM-DD <measurement> <sample>.md
    3. 노트가 *없으면* 템플릿에서 생성
    4. 노트가 *있으면* frontmatter 의 자동 영역만 갱신 (수동 영역 보존)
    5. plots/ 의 PNG 를 0. Inbox/Files/ 로 복사
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

from modules import common  # noqa: E402

# Obsidian Vault 경로 (상수)
VAULT_ROOT = Path(r"$VAULT")
EXPERIMENT_LOG = VAULT_ROOT / "1. Project" / "대학원 공부" / "2. 연구 (Research)" / "2. Experiment" / "2.3 Experiment log"
INBOX_FILES = VAULT_ROOT / "0. Inbox" / "Files"

TEMPLATE_PATH = SCRIPT_DIR.parent / "templates" / "obsidian_template.md"


def main():
    parser = argparse.ArgumentParser(description="처리 결과 → Obsidian 노트 동기화")
    parser.add_argument('--project_path', required=True, type=Path)
    parser.add_argument('--force-overwrite', action='store_true',
                        help='기존 노트의 본문도 덮어쓰기 (기본: 자동 영역만)')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    project = args.project_path.resolve()
    readme = project / 'README.md'
    metrics_path = project / '01_processed' / 'metrics.json'
    plots_dir = project / '01_processed' / 'plots'

    if not readme.exists():
        print(f"[ERROR] README.md not found: {readme}")
        sys.exit(1)

    fm = common.parse_frontmatter(readme)
    metrics = {}
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding='utf-8'))

    # frontmatter 필수 필드
    project_name = fm.get('project', 'Unknown')
    sample = fm.get('sample', 'Unknown')
    measurement = fm.get('measurement_type', 'Unknown')
    date_str = fm.get('date', datetime.now().strftime('%Y-%m-%d'))

    # 노트 경로
    safe_project = str(project_name).replace('/', '_')
    note_dir = EXPERIMENT_LOG / safe_project
    note_dir.mkdir(parents=True, exist_ok=True)
    note_filename = f"{date_str} {measurement} {sample}.md"
    note_path = note_dir / note_filename

    print(f"=== sync_to_obsidian.py ===")
    print(f"  project_path : {project}")
    print(f"  note_path    : {note_path}")
    print(f"  exists       : {note_path.exists()}")
    print(f"  metrics      : {bool(metrics)}")

    # plot PNG 복사 (sample-aware 파일명)
    INBOX_FILES.mkdir(parents=True, exist_ok=True)
    copied = []
    if plots_dir.exists():
        for png in plots_dir.glob('*.png'):
            target_name = f"{date_str}_{measurement}_{sample}_{png.stem}.png"
            target = INBOX_FILES / target_name
            if not args.dry_run:
                shutil.copy2(png, target)
            copied.append(target_name)
    print(f"  copied plots : {len(copied)}")

    if args.dry_run:
        print("[dry-run] 노트 생성 생략. 종료.")
        return

    # 노트 생성·갱신
    note_frontmatter = {
        'type': 'experiment-note',
        'subtype': 'measurement',
        'date': date_str,
        'project': project_name,
        'sample': sample,
        'measurement_type': measurement,
        'equipment': fm.get('equipment'),
        'conditions': fm.get('conditions', {}),
        'data_root': str(project).replace('\\', '/'),
        'fit_results': {
            'R2': metrics.get('R2'),
            'amplitude_uV': metrics.get('amplitude_uV'),
            'phase_deg': metrics.get('phase_deg'),
            'offset_uV': metrics.get('offset_uV'),
        },
        'status': fm.get('status', 'processed'),
        'related_papers': fm.get('related_papers', []),
        'research_themes': fm.get('research_themes', []),
        'tags': fm.get('tags', ['experiment', measurement, project_name]),
        'last_synced': datetime.now().isoformat(timespec='seconds'),
    }

    # 본문 (간단)
    plot_embeds = '\n'.join(
        f"![[{name}|500]]" for name in copied if 'summary' not in name
    )
    summary_embed = next(
        (f"![[{name}|700]]" for name in copied if 'summary' in name),
        ''
    )

    body = f"""### UP:: [[!Experiment Index]]

# {date_str} {measurement} — {sample}

> **데이터 위치**: `{project}`
> **처리 노트북**: `02_notebooks/analysis.ipynb`
> **자동 동기화**: sync_to_obsidian.py, 마지막 {note_frontmatter['last_synced']}

## 실험 목적

<!-- 수동 기입 -->

## 측정 조건

| 항목 | 값 |
|------|-----|
| 장비 | {fm.get('equipment', '?')} |
| 샘플 | {sample} |
| 측정법 | {measurement} |
| 날짜 | {date_str} |
"""
    conds = fm.get('conditions') or {}
    if isinstance(conds, dict):
        for k, v in conds.items():
            body += f"| {k} | {v} |\n"

    body += f"""
## Fit 결과

| 지표 | 값 |
|------|-----|
| R² | {metrics.get('R2', '?')} |
| Amplitude (μV) | {metrics.get('amplitude_uV', '?')} |
| Phase (°) | {metrics.get('phase_deg', '?')} |
| Offset (μV) | {metrics.get('offset_uV', '?')} |
| Model | `{metrics.get('model', '?')}` |

## 결과 플롯

{summary_embed}

### 개별 플롯

{plot_embeds}

## 고찰

<!-- 수동 기입 -->

## 다음 단계 / 미해결

<!-- 수동 기입 -->

## 관련 노트

- [[Samples#{sample}]]
- [[!Experiment Index]]
"""

    if note_path.exists() and not args.force_overwrite:
        # 기존 본문 중 *수동 영역* 보존
        existing = note_path.read_text(encoding='utf-8')
        # 간단 전략: 기존 frontmatter 만 교체. 본문 전체 보존.
        if existing.startswith('---'):
            try:
                end = existing.index('---', 3) + 3
                old_body = existing[end:].lstrip('\n')
                # frontmatter 갱신, body 보존
                common.write_frontmatter(note_path, note_frontmatter, old_body)
                print(f"[update] frontmatter 갱신, 본문 보존: {note_path}")
            except ValueError:
                common.write_frontmatter(note_path, note_frontmatter, body)
                print(f"[recreate] 기존 frontmatter 파싱 실패, 재생성: {note_path}")
        else:
            common.write_frontmatter(note_path, note_frontmatter, body)
            print(f"[recreate] 기존 frontmatter 없음, 재생성: {note_path}")
    else:
        common.write_frontmatter(note_path, note_frontmatter, body)
        action = 'overwrite' if args.force_overwrite else 'create'
        print(f"[{action}] {note_path}")

    print(f"\n[DONE] Obsidian 동기화 완료.")


if __name__ == '__main__':
    main()
