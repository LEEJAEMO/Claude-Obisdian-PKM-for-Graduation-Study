#!/usr/bin/env python3
"""
PreToolUse guard: lecture_transcribe.py 우회 방지

Whisper를 강의 전사 목적으로 직접 호출하려는 시도를 차단한다.
발동 조건:
  - whisper CLI + 미디어 파일 확장자 (.mp4/.m4a/.wav/.mp3/.mkv)
  - python -c "... whisper ..." 인라인 패턴
  단, lecture_transcribe.py 경유 호출은 허용.

왜 필요한가:
  2026-04-22 확인: 즉흥 Whisper 호출로 생성된 녹취록에 슬라이드 구분자·헤더가
  누락되는 사고 발생. lecture_transcribe.py에는 MAD 기반 슬라이드 감지가 포함되어
  있으나 직접 호출 시 이 코드가 실행되지 않는다.
  참고: T-002_whisper-improvised-script-no-slides.md
"""
import json, re, sys

data = json.loads(sys.stdin.read())
if data.get("tool_name") != "Bash":
    sys.exit(0)

cmd = data.get("tool_input", {}).get("command", "")

if "lecture_transcribe.py" in cmd:
    sys.exit(0)

is_raw_whisper = bool(
    re.search(r"(?<!\w)whisper\s", cmd) and
    re.search(r"\.(mp4|m4a|wav|mp3|mkv)\b", cmd, re.I)
)
is_inline_whisper = bool(re.search(r"python\S*\s.*-c.*whisper", cmd, re.S | re.I))

if is_raw_whisper or is_inline_whisper:
    print(
        "[GUARD] 즉흥 Whisper 호출 차단됨\n"
        "\n강의 전사는 반드시 lecture_transcribe.py를 경유해야 합니다:\n"
        "\n  python \".claude/scripts/lecture_transcribe.py\" \"<mp4_경로>\" \\\n"
        "    --model medium --lang ja --cooldown 30 --mad 5.0\n"
        "\n직접 whisper 호출 시 슬라이드 감지(MAD 알고리즘)가 실행되지 않아\n"
        "녹취록에 슬라이드 구분자가 누락됩니다.\n"
        "\n워크플로우: .claude/workflows/lecture-transcribe.md\n"
        "PKM 모듈: M-002_lecture-transcribe-routine.md\n"
        "에러 기록: T-002_whisper-improvised-script-no-slides.md",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
