#!/usr/bin/env python
"""
Stop hook: Claude Code 응답 종료마다 실행.

두 가지 역할:
  1. 자동 스냅샷 (autosave) — 서버 크래시 복구용 최소 상태를 기록
  2. 컨텍스트 압축 제안 — 도구 호출 50회 이상일 때 /compact·/save-session 안내

autosave는 /save-session 과 별개. autosave는 '크래시 있었음'만 표시,
정식 세션 복원은 여전히 사용자의 /save-session 실행에 의존.
"""
import sys
import json
from datetime import datetime
from pathlib import Path


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    now = datetime.now()
    tool_count = data.get("tool_use_count", 0)
    stop_reason = data.get("stop_reason", "")

    session_dir = Path.home() / ".claude" / "session-data"
    session_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. autosave: 매 응답 종료마다 스냅샷 갱신 ──
    autosave_path = session_dir / f"{now.strftime('%Y-%m-%d')}-autosave.tmp"
    snapshot = {
        "last_updated": now.isoformat(timespec="seconds"),
        "tool_use_count": tool_count,
        "stop_reason": stop_reason,
        "note": (
            "서버 크래시 복구용 최소 스냅샷. "
            "정식 저장은 /save-session, 복원은 /resume-session 사용."
        ),
    }
    try:
        autosave_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass  # 스냅샷 실패해도 세션 자체는 막지 않음

    # ── 2. compact 제안: 도구 호출 50회 이상 ──
    if tool_count >= 50:
        print(
            f"\n[자동 알림] 이번 세션에서 도구를 {tool_count}회 호출했습니다.\n"
            "컨텍스트가 길어졌습니다. 다음 중 하나를 고려하세요:\n"
            "  • /compact — 컨텍스트 압축 (작업 계속)\n"
            "  • /save-session — 세션 저장 후 새 세션 시작\n",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
