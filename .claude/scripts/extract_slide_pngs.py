#!/usr/bin/env python3
"""
extract_slide_pngs.py — mp4 강의 영상에서 슬라이드 PNG 추출
============================================================
사용:
  python extract_slide_pngs.py <video> --transcript <txt> --out <dir> --prefix ID_W5
  python extract_slide_pngs.py <video> --transcript <txt> --out <dir> --prefix ID_W5 --slides 4,7,10
  python extract_slide_pngs.py <video> --transcript <txt> --out <dir> --prefix ID_W5 --slides all

옵션:
  --transcript  lecture_transcribe.py 가 만든 녹취록 TXT (슬라이드 시작 시각 파싱용, 필수)
  --out         출력 디렉토리 (보통 Obsidian Vault/0. Inbox/Files)
  --prefix      파일명 prefix (예: ID_W5 → ID_W5_p04.png 형식)
  --slides      추출할 슬라이드 번호 ("4,7,10" 형식 또는 "all")  [기본: all]
  --offset      슬라이드 시작 시각 + offset 초 시점에서 캡처     [기본: 2.0]

용도:
  강의 녹화에서만 보이는 강사 라이브 마크업·필기·구두 보충이 필요할 때 사용.
  PDF 강의자료만으로 충분한 경우는 굳이 추출하지 않아도 된다.

기술 노트:
  - cv2.imwrite는 Windows + 한글 경로에서 조용히 실패하므로
    cv2.imencode + open('wb') 우회 사용.
  - 슬라이드 시작 직후는 전환 애니메이션 가능성이 있어 +2초 offset 권장.
  - 녹취록 형식: "━━━ 【スライド N】 (HH:)MM:SS ━━━" 라인을 파싱.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
from pathlib import Path

import cv2

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def parse_slide_times(transcript_path: Path) -> dict[int, int]:
    """
    녹취록에서 슬라이드 번호 → 시작 시각(초) 매핑 추출.
    포맷 예: "━━━ 【スライド 12】 10:28 ━━━" 또는 "━━━ 【スライド 60】 01:10:39 ━━━"
    """
    pattern = re.compile(r"スライド\s*(\d+)】\s*(?:(\d+):)?(\d+):(\d+)")
    times: dict[int, int] = {}
    with transcript_path.open(encoding="utf-8") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                slide = int(m.group(1))
                h = int(m.group(2)) if m.group(2) else 0
                mm = int(m.group(3))
                ss = int(m.group(4))
                times[slide] = h * 3600 + mm * 60 + ss
    return times


def parse_slide_list(arg: str, all_slides: list[int]) -> list[int]:
    if arg.lower() == "all":
        return all_slides
    return [int(x.strip()) for x in arg.split(",") if x.strip()]


def capture_frame_to_png(cap: cv2.VideoCapture, t_sec: float, out_path: Path) -> int:
    """t_sec 시점의 프레임을 PNG로 저장. 한글 경로 우회. 반환: 파일 크기(bytes)."""
    cap.set(cv2.CAP_PROP_POS_MSEC, t_sec * 1000)
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError(f"frame read failed at t={t_sec:.2f}s")
    ok, buf = cv2.imencode(".png", frame)
    if not ok:
        raise RuntimeError("PNG encode failed")
    out_path.write_bytes(buf.tobytes())
    return out_path.stat().st_size


def main() -> int:
    p = argparse.ArgumentParser(description="강의 mp4 → 슬라이드 PNG 추출")
    p.add_argument("video", help="MP4 강의 영상 경로")
    p.add_argument("--transcript", required=True, help="녹취록 TXT 경로 (lecture_transcribe.py 출력)")
    p.add_argument("--out", required=True, help="출력 디렉토리")
    p.add_argument("--prefix", required=True, help="파일명 prefix (예: ID_W5)")
    p.add_argument("--slides", default="all", help='추출할 슬라이드 번호 ("4,7,10" 또는 "all")')
    p.add_argument("--offset", type=float, default=2.0, help="슬라이드 시작 + offset 초 시점에서 캡처")
    args = p.parse_args()

    video = Path(args.video)
    transcript = Path(args.transcript)
    out_dir = Path(args.out)

    if not video.exists():
        print(f"[error] video not found: {video}", file=sys.stderr)
        return 1
    if not transcript.exists():
        print(f"[error] transcript not found: {transcript}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)

    times = parse_slide_times(transcript)
    if not times:
        print(f"[error] no slide markers in {transcript}", file=sys.stderr)
        return 1

    targets = parse_slide_list(args.slides, sorted(times.keys()))

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        print(f"[error] cv2.VideoCapture failed: {video}", file=sys.stderr)
        return 1
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1)
    print(f"[info] video {duration:.1f}s, slides in transcript: {len(times)}, targets: {len(targets)}")

    saved = 0
    skipped = 0
    for s in targets:
        t = times.get(s)
        if t is None:
            print(f"[skip] slide {s}: no timestamp in transcript")
            skipped += 1
            continue
        capture_t = min(t + args.offset, duration - 0.5)
        out_path = out_dir / f"{args.prefix}_p{s:02d}.png"
        try:
            sz = capture_frame_to_png(cap, capture_t, out_path)
            print(f"[ok] slide {s:>2} (t={t}s, capture={capture_t:.1f}s): {out_path.name} ({sz // 1024} KB)")
            saved += 1
        except Exception as e:  # noqa: BLE001
            print(f"[fail] slide {s}: {e}")
            skipped += 1

    cap.release()
    print(f"\n[done] saved={saved}, skipped={skipped}, out_dir={out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
