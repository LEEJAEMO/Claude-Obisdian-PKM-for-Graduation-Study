---
type: pkm-module
id: M-002
title: 강의 녹취록 생성 루틴
domain: [lecture-note, whisper, transcription]
task_type: workflow
input: "강의 녹화 MP4 또는 M4A 파일 경로"
output: "슬라이드 분절 녹취록 TXT (`<mp4_dir>/녹취록/<파일명> 녹취록.txt`)"
related_command: /lecture-transcribe
related_spec: 14. Specs/workflows/lecture-transcribe.md
related_agent: ""
created: 2026-04-19
updated: 2026-05-01
---

# M-002 — 강의 녹취록 생성 루틴

> **재사용 목적**: MP4 강의 녹화 → 슬라이드 분절 녹취록 TXT 생성. M-001 강의노트 루틴의 선행 단계.

## 트리거

- `/lecture-transcribe <MP4 경로>` 호출
- 또는 자연어로 "이 강의 녹취록 만들어줘" + 경로 첨부

## 단계 요약

| Step | 작업 |
|------|------|
| 1 | 경로 확인 (`ls "<mp4>"`) + 출력 경로 결정 (`<mp4_dir>/녹취록/<파일명> 녹취록.txt`) |
| 2 | `lecture_transcribe.py` 백그라운드 실행 (`run_in_background: true`) — 40~60분 소요 |
| 3 | 완료 알림 수신 후 stdout 마지막 4줄만 읽어 요약 보고 |

## 스크립트 실행 명령

```bash
python "$PROJECT_ROOT/.claude/scripts/lecture_transcribe.py" \
  "<mp4_또는_m4a_경로>" \
  --model large-v3-turbo \
  --lang ja \
  --cooldown 30 \
  --mad 5.0
```

## 파라미터 기본값 (교정 완료 — 변경 불필요)

| 파라미터 | 값 | 근거 |
|---------|-----|------|
| `--model` | `large-v3-turbo` | 일본어 전문 강의 정확도 최우선. **large-v3 사용 금지** (다운로드 미완료). medium은 불충분 |
| `--lang` | `ja` | 일본어 강의 기본값 (한국어: `ko`, 영어: `en`) |
| `--cooldown` | `30` | 슬라이드 내 필기 annotation을 페이지 전환으로 오인 방지 |
| `--mad` | `5.0` | 연속 프레임 MAD≈0, 슬라이드 전환 MAD=14~23 기준으로 교정 |

## M4A 파일 입력 시 주의사항

- m4a(오디오 전용)는 비디오 프레임이 없으므로 슬라이드 감지 결과가 `slide=0`으로 출력된다 → **정상 동작**
- 출력 녹취록은 슬라이드 분절 없이 타임스탬프 세그먼트만 나열됨
- 후속 `notes-digest` 에서 PDF 슬라이드를 기준으로 내용을 수동 대응해야 함

## 출력 형식

```
============================================================
강의 녹취록: 2026-04-15 1030 전기전도2
자동 생성: Whisper + 슬라이드 감지 (slide=59)
============================================================

━━━ 【スライド 1】 00:00 ━━━

[00:05] はい、じゃあ始めましょう...
```

- 슬라이드 번호: 변경 순서 기준 (절대 페이지 아님)
- PDF 대조 시: 타임스탬프로 해당 슬라이드 특정

## 주의사항

- 중간 프레임 이미지 읽기·진행 폴링·캘리브레이션 반복 **금지** (context 낭비)
- 완료 알림 전까지 다른 작업 진행 가능

## 토큰 예산

| 단계 | tool calls | 비용 |
|------|-----------|------|
| Step 1 경로 확인 | 1 | 최소 |
| Step 2 백그라운드 실행 | 1 | 0 (대기 중) |
| Step 3 결과 읽기 | 1~2 | 4줄만 읽음 |
| **합계** | **3~4** | **~1K tokens** |

## 다음 단계

완료 후 M-001(강의노트 작성 루틴) 또는 `/notes-digest <녹취록_경로>` 로 이어간다.
