#!/usr/bin/env python
"""
sync_readmes_to_vault.py — 6. Experiment 측 README.md 들을 Obsidian Vault 의 사본으로 동기화.

Obsidian 은 Vault 폴더 *외부* 의 .md 를 직접 인식하지 못함. 따라서 본 스크립트는:
1. 6. Experiment/ 측의 README.md 들의 *본문* 을
2. Vault 측 사본의 frontmatter 는 유지하고 *본문만* 갱신
3. mirror_status 의 날짜를 *오늘* 로 갱신

사용:
    python sync_readmes_to_vault.py            # 동기화 실행
    python sync_readmes_to_vault.py --dry-run  # 변경 사항만 표시
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from datetime import date
from pathlib import Path

# Windows cp949 회피 — stdout 을 utf-8 로 강제
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 원본 (시스템 측) ↔ 사본 (Vault 측) 매핑
SRC_DST_PAIRS = [
    (
        r"$EXPERIMENT_ROOT\README.md",
        r"$VAULT\1. Project\대학원 공부\2. 연구 (Research)\2. Experiment\시스템 문서\6. Experiment — 시스템 설계 (사본).md",
    ),
    (
        r"$EXPERIMENT_ROOT\6. Fitting Script\README.md",
        r"$VAULT\1. Project\대학원 공부\2. 연구 (Research)\2. Experiment\시스템 문서\6. Fitting Script — 모듈 안내 (사본).md",
    ),
]


def split_frontmatter(text: str) -> tuple[str, str]:
    """text 를 (frontmatter_block, body) 로 분리.
    frontmatter_block 은 '---\\n...\\n---\\n' 형태 (또는 빈 문자열).
    """
    if not text.startswith('---'):
        return '', text
    try:
        end = text.index('---', 3) + 3
        # 다음 줄까지 포함
        if end < len(text) and text[end] == '\n':
            end += 1
        return text[:end], text[end:]
    except ValueError:
        return '', text


def update_mirror_status(frontmatter_block: str, today: str) -> str:
    """frontmatter 의 mirror_status 와 date 를 today 로 갱신."""
    out = re.sub(
        r'mirror_status:\s*synced-\d{4}-\d{2}-\d{2}',
        f'mirror_status: synced-{today}',
        frontmatter_block,
    )
    out = re.sub(
        r'(?m)^date:\s*\d{4}-\d{2}-\d{2}',
        f'date: {today}',
        out,
    )
    return out


def update_body_mirror_date(body: str, today: str) -> str:
    """본문 의 '마지막 동기화: YYYY-MM-DD' 를 today 로 갱신."""
    return re.sub(
        r'\*\*마지막 동기화\*\*:\s*\d{4}-\d{2}-\d{2}',
        f'**마지막 동기화**: {today}',
        body,
    )


def main():
    parser = argparse.ArgumentParser(description="6. Experiment README ↔ Vault 사본 동기화")
    parser.add_argument('--dry-run', action='store_true', help='변경 사항만 표시')
    args = parser.parse_args()

    today = date.today().isoformat()
    print(f"=== sync_readmes_to_vault.py ===")
    print(f"  today : {today}")
    print(f"  pairs : {len(SRC_DST_PAIRS)}")
    print()

    n_updated = 0
    n_unchanged = 0
    n_error = 0

    for src_path, dst_path in SRC_DST_PAIRS:
        src = Path(src_path)
        dst = Path(dst_path)

        if not src.exists():
            print(f"[ERROR] src not found: {src}")
            n_error += 1
            continue

        if not dst.exists():
            print(f"[ERROR] dst not found: {dst}")
            n_error += 1
            continue

        src_content = src.read_text(encoding='utf-8')
        dst_content = dst.read_text(encoding='utf-8')

        dst_fm, dst_body_old = split_frontmatter(dst_content)

        # 본문 = src 전체 (src 는 frontmatter 없음 — 단순 .md)
        # 단, dst 의 frontmatter 직후 *경고 박스* + '---' 까지는 보존
        # 본 노트의 frontmatter 다음에 *경고박스 ~ 첫 '---' 줄까지* 가 사본의 "헤더 영역"

        # 사본의 body 에서 첫 '---' 까지가 헤더, 그 후가 src 의 본문 사본
        # 따라서 헤더만 보존하고 그 뒤를 src 전체로 교체

        # 첫 '\n---\n' 찾기 (헤더 끝)
        match = re.search(r'\n---\n', dst_body_old)
        if match:
            header_part = dst_body_old[: match.end()]  # 헤더 + '---'
        else:
            # 헤더 없으면 빈 헤더
            header_part = '\n'

        # 새 body = 갱신된 헤더 + src 본문
        header_part = update_body_mirror_date(header_part, today)
        new_body = header_part + '\n' + src_content
        new_fm = update_mirror_status(dst_fm, today)
        new_content = new_fm + new_body

        if new_content == dst_content:
            print(f"[unchanged] {dst.name}")
            n_unchanged += 1
            continue

        if args.dry_run:
            print(f"[would update] {dst.name}")
            print(f"  src bytes: {len(src_content)}")
            print(f"  dst bytes (old): {len(dst_content)}")
            print(f"  dst bytes (new): {len(new_content)}")
        else:
            dst.write_text(new_content, encoding='utf-8')
            print(f"[updated] {dst.name}")
        n_updated += 1

    print()
    print(f"  updated   : {n_updated}")
    print(f"  unchanged : {n_unchanged}")
    print(f"  errors    : {n_error}")

    if args.dry_run:
        print(f"\n[dry-run] 실제 변경 없음.")


if __name__ == '__main__':
    main()
