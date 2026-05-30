# 강의 녹취록 생성 워크플로우 (Zoom/录画 MP4)

> **즉흥 스크립트 금지**: `whisper` CLI나 임시 Python 스크립트로 직접 전사하면
> 슬라이드 구분자·헤더가 누락된다 (T-002 참조). 반드시 `lecture_transcribe.py`만 사용.
> PreToolUse hook(`guard_whisper_improvise.py`)이 우회 시도를 차단한다.

## 발동 조건

`/lecture-transcribe [MP4 경로]` 또는 자연어로 "이 강의 녹취록 만들어줘 → [경로]"

강의노트 작성 전 선행 단계로 실행. 출력 TXT를 `/notes-digest` 또는 `lecture-note` 워크플로우에 넘긴다.

---

## Claude가 할 일 (총 3단계, ~4 tool calls)

### Step 1: 경로 확인

```
MP4 존재 여부 확인 (Bash: ls "<경로>")
출력 경로 자동 결정: <mp4_dir>/녹취록/<파일명> 녹취록.txt
```

### Step 2: 스크립트 백그라운드 실행

```bash
python "$PROJECT_ROOT/.claude/scripts/lecture_transcribe.py" \
  "<mp4_경로>" \
  --model medium \
  --lang ja \
  --cooldown 30 \
  --mad 5.0
```

- `run_in_background: true` — Whisper 처리는 40~60분 소요
- 완료 알림이 오면 Step 3로 진행

### Step 3: 결과 확인 후 보고

스크립트 stdout의 마지막 4줄(DONE/OUT 요약)만 읽는다.
중간 로그나 프레임 이미지는 **읽지 않는다** — context 낭비.

```
녹취록 생성 완료:
- 세그먼트: N개 | 슬라이드: M개
- 저장: <out_path>
→ 강의노트 작성 준비 완료. /notes-digest 또는 lecture-note 워크플로우로 이어가세요.
```

---

## 파라미터 (사전 교정값 — 변경 불필요)

| 파라미터 | 값 | 근거 |
|---------|-----|------|
| `--model` | `medium` | small은 일본어 정확도 불충분 |
| `--lang` | `ja` | 전기전도 등 일본어 강의 기본값 |
| `--cooldown` | `30` | 슬라이드 내 필기 annotation을 페이지 전환으로 오인 방지 |
| `--mad` | `5.0` | 연속 프레임 MAD≈0, 다른 슬라이드 MAD=14~23 기준으로 교정 |

한국어 강의 또는 영어 강의이면 `--lang ko` / `--lang en` 으로 변경.

---

## 출력 형식

```
============================================================
강의 녹취록: 2026-04-15 1030 전기전도2
자동 생성: Whisper + 슬라이드 감지 (slide=59)
============================================================

━━━ 【スライド 1】 00:00 ━━━

[00:05] はい、じゃあ始めましょう...

━━━ 【スライド 2】 00:36 ━━━

[00:38] 今日のテーマは...
```

슬라이드 번호는 절대 페이지가 아닌 **변경 순서 기준** (1부터 순차).
슬라이드 PDF와 대조 시: 타임스탬프로 해당 슬라이드 특정.

---

## 스크립트 경로

```
.claude/scripts/lecture_transcribe.py
```

의존성: `opencv-python`, `numpy`, `openai-whisper`, `ffmpeg` (PATH에 있어야 함)

---

## 다음 단계 연결

```
/notes-digest <녹취록_경로>       ← 텍스트 입력 형태
또는
/lecture-note 워크플로우의 "TXT 녹취록" 입력 경로 전달
```

---

## 토큰 예산

| 단계 | tool calls | 비용 |
|------|-----------|------|
| Step 1 경로 확인 | 1 | 최소 |
| Step 2 백그라운드 실행 | 1 | 0 (대기 중) |
| Step 3 결과 읽기 | 1~2 | 4줄만 읽음 |
| **합계** | **3~4** | **~1K tokens** |

중간 프레임 이미지 읽기, 진행 폴링, 캘리브레이션 반복 — **금지**.
