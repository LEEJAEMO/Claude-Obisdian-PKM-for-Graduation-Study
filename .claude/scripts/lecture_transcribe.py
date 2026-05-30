#!/usr/bin/env python3
"""
강의 녹취록 자동 생성 스크립트 (Zoom/録画形式)
======================================================
사용법:
  python lecture_transcribe.py <video_path> [옵션]

옵션:
  --model    Whisper 모델 (tiny/base/small/medium/large) [기본: medium]
  --lang     언어 코드 (ja/ko/en 등)                   [기본: ja]
  --cooldown 슬라이드 간 최소 간격(초)                  [기본: 30]
  --mad      슬라이드 변경 MAD 임계값                   [기본: 5.0]
  --out      출력 TXT 경로 (미지정 시 비디오 옆에 저장)

출력:
  - 녹취록 TXT: 타임스탬프 + 슬라이드 번호 삽입
  - 요약 출력: Claude가 읽을 3줄 요약 (segment수, slide수, 경로)

NOTE: 중간 이미지/프레임은 일절 출력하지 않음 — Claude context 절약
"""

import argparse, json, os, subprocess, sys, tempfile, io
import cv2
import numpy as np
import whisper

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ──────────────────────────────────────────────
# 슬라이드 변경 감지
# ──────────────────────────────────────────────
def detect_slides(video_path: str, mad_threshold: float, cooldown: int) -> list[tuple[int, int]]:
    """
    MAD(평균 절대 차이) 기반 슬라이드 변경 감지.
    Returns: [(timestamp_sec, slide_num), ...]
    """
    cap = cv2.VideoCapture(video_path)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1)

    slides = []
    prev_gray = None
    slide_num = 0
    last_change_t = -(cooldown + 1)
    t = 0

    print(f"[1/3] 슬라이드 감지 중... (MAD>{mad_threshold}, cooldown={cooldown}s)", flush=True)

    while t <= duration:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        crop = frame[int(h * 0.05):int(h * 0.95), int(w * 0.05):int(w * 0.95)]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(float)

        if prev_gray is not None:
            mad = np.mean(np.abs(gray - prev_gray))
            if mad > mad_threshold and (t - last_change_t) > cooldown:
                slide_num += 1
                slides.append((t, slide_num))
                last_change_t = t
        else:
            slide_num = 1
            slides.append((0, 1))

        prev_gray = gray
        t += 1  # 1초 간격 샘플링

    cap.release()
    print(f"      → {slide_num}개 슬라이드 감지", flush=True)
    return slides


# ──────────────────────────────────────────────
# 오디오 추출
# ──────────────────────────────────────────────
def extract_audio(video_path: str, tmp_dir: str) -> str:
    audio_path = os.path.join(tmp_dir, "lecture_audio.wav")
    print(f"[2/3] 오디오 추출 중...", flush=True)
    subprocess.run(
        ["ffmpeg", "-i", video_path,
         "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
         audio_path, "-y", "-loglevel", "error"],
        check=True
    )
    print(f"      → {audio_path}", flush=True)
    return audio_path


# ──────────────────────────────────────────────
# Whisper 전사
# ──────────────────────────────────────────────
def transcribe(audio_path: str, model_name: str, language: str) -> list[dict]:
    print(f"[3/3] Whisper({model_name}) 전사 중... 언어={language}", flush=True)
    model = whisper.load_model(model_name)
    result = model.transcribe(
        audio_path,
        language=language,
        verbose=False,
        condition_on_previous_text=True,
        task="transcribe"
    )
    print(f"      → {len(result['segments'])} 세그먼트", flush=True)
    return result["segments"]


# ──────────────────────────────────────────────
# 녹취록 결합
# ──────────────────────────────────────────────
def get_slide_at(t_sec: float, slides: list[tuple[int, int]]) -> int:
    current = 1
    for ts, sn in slides:
        if ts <= t_sec:
            current = sn
        else:
            break
    return current


def fmt_time(t_sec: float) -> str:
    t = int(t_sec)
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"


def build_transcript(segments: list[dict], slides: list[tuple[int, int]],
                     video_name: str) -> str:
    lines = [
        "=" * 60,
        f"강의 녹취록: {video_name}",
        f"자동 생성: Whisper + 슬라이드 감지 (slide={len(slides)})",
        "=" * 60,
        "",
    ]
    prev_slide = 0

    for seg in segments:
        start = seg["start"]
        text = seg["text"].strip()
        if not text:
            continue

        current_slide = get_slide_at(start, slides)
        if current_slide != prev_slide:
            slide_ts = next((ts for ts, sn in slides if sn == current_slide), start)
            lines += ["", f"━━━ 【スライド {current_slide}】 {fmt_time(slide_ts)} ━━━", ""]
            prev_slide = current_slide

        lines.append(f"[{fmt_time(start)}] {text}")

    lines += ["", f"[{fmt_time(segments[-1]['end'])}] ─── 終了 ───"]
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="강의 녹취록 자동 생성")
    parser.add_argument("video", help="MP4/M4A 파일 경로")
    parser.add_argument("--model",    default="medium", help="Whisper 모델")
    parser.add_argument("--lang",     default="ja",     help="언어 코드")
    parser.add_argument("--cooldown", type=int,   default=30,  help="슬라이드 쿨다운(초)")
    parser.add_argument("--mad",      type=float, default=5.0, help="MAD 임계값")
    parser.add_argument("--out",      default=None,     help="출력 TXT 경로")
    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"ERROR: 파일 없음 — {args.video}", file=sys.stderr)
        sys.exit(1)

    video_name = os.path.splitext(os.path.basename(args.video))[0]
    out_path = args.out or os.path.join(
        os.path.dirname(args.video), "녹취록", f"{video_name} 녹취록.txt"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        slides = detect_slides(args.video, args.mad, args.cooldown)
        audio_path = extract_audio(args.video, tmp_dir)
        segments = transcribe(audio_path, args.model, args.lang)

    transcript = build_transcript(segments, slides, video_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    # Claude가 읽을 3줄 요약만 출력
    print("\n" + "=" * 40)
    print(f"DONE  세그먼트={len(segments)} | 슬라이드={len(slides)}")
    print(f"OUT   {out_path}")
    print("=" * 40)


if __name__ == "__main__":
    main()
