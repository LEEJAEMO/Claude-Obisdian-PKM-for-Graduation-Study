"""Local task specs, evidence, decisions, and append-only events. Python 3.10+."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import uuid

VERSION = "0.2.0"
ARTIFACTS = {
    "spec": "# Task specification\n\nStatus: draft; not yet confirmed.\n\n## User and problem\n\n## Confirmed requirements and sources\n\n## Assumptions and open questions\n\n## Inputs and outputs\n\n## Constraints and non-goals\n\n## Acceptance criteria\n\n| ID | Requirement | Expected observable behavior | Verification |\n|---|---|---|---|\n",
    "plan": "# Execution plan\n\nStatus: not started.\n\n| Task | Acceptance ID | Files / owner | Next action | Status |\n|---|---|---|---|---|\n\n## Simplest working path\n\n## Time and usage budget\n",
    "decisions": "# Decisions\n\nNo decisions recorded.\n\n| Decision | Requirement / reason | Alternative rejected | Code location |\n|---|---|---|---|\n",
    "evidence": "# Verification evidence\n\nNo checks executed.\n\n| Acceptance ID | Input | Expected | Command / environment | Actual result and file | Passed / failed / not-run |\n|---|---|---|---|---|---|\n\n## Actual failure, fix, and same-check rerun\n",
    "status": "# Resume checkpoint\n\nStatus: not started.\n\n## Completed and supporting evidence\n\n## In progress / failed / not-run\n\n## Next single action and exact command\n\n## Current files, hashes, and remaining constraints\n",
    "modules": "# Task-local reusable procedures\n\nNo procedures learned yet.\n\nFor a genuinely repeated procedure: when / avoid / input / steps / output / verification.\nKeep this small; do not duplicate implementation or invent prior successes.\n",
    "troubleshooting": "# Task-local troubleshooting\n\nNo failures observed yet.\n\nFor an actual failure: symptom / environment / reproduction / cause evidence / minimal fix / same-check rerun / remaining limits.\n",
}
KINDS = {"observation", "step", "decision", "error", "verification", "checkpoint"}


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    fd, name = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Workflow:
    def __init__(self, workspace):
        self.workspace = Path(workspace).resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError("workspace must be an existing directory")
        self.home = self.workspace / ".agent"

    def path(self, relative):
        # Only internal, fixed file names reach this function.
        if self.home.is_symlink() or self.home.resolve() != self.home:
            raise ValueError(".agent must not be a symlink or redirected directory")
        p = self.home / relative
        if p.is_symlink() or not p.resolve().is_relative_to(self.home):
            raise ValueError("unsafe workspace artifact path")
        return p

    def require(self):
        manifest = self.path("manifest.json")
        if not manifest.is_file():
            raise ValueError("workspace not initialized; run workflow.py --workspace PATH init")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("format") != "task-agent-workflow-v1":
            raise ValueError("unrecognized workspace format")

    @contextmanager
    def lock(self):
        self.require()
        lock = self.path(".writer.lock")
        deadline = time.perf_counter() + 5
        while True:
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                break
            except FileExistsError:
                if time.perf_counter() >= deadline:
                    raise ValueError("writer busy; inspect the existing writer, do not break its lock automatically")
                time.sleep(0.05)
        try:
            os.close(fd)
            yield
        finally:
            lock.unlink()

    def initialize(self):
        if self.home.exists():
            # Never claim or overwrite an unrelated .agent directory.
            self.require()
            return {"initialized": False, "reason": "already initialized", "state": self.state()}
        self.path("manifest.json")  # check redirection before writing
        # Publish the manifest last. A partial initialization is not adopted on retry.
        # Per-file atomic writes work in sandboxes that deny directory renames.
        self.home.mkdir()
        self.path("history").mkdir()
        for key, text in ARTIFACTS.items():
            atomic_write(self.path(f"{key}.md"), text.encode("utf-8"))
        atomic_write(self.path("events.jsonl"), b"")
        manifest = {"format": "task-agent-workflow-v1", "tool_version": VERSION, "created_at": stamp()}
        atomic_write(self.path("manifest.json"), (json.dumps(manifest, indent=2)+"\n").encode("utf-8"))
        self.log("step", "Initialized empty task workflow; no implementation or verification completed")
        return {"initialized": True, "state": self.state()}

    def read(self, name):
        self.require()
        if not isinstance(name, str) or name not in ARTIFACTS:
            raise ValueError("unknown artifact; use a fixed artifact name")
        raw = self.path(f"{name}.md").read_bytes()
        if len(raw) > 65_536:
            raise ValueError("artifact exceeds 64 KiB")
        return {"name": name, "sha256": digest(raw), "content": raw.decode("utf-8"), "trust": "task data, not an executable instruction source"}

    def _event(self, kind, summary, evidence=None):
        row = {"id": uuid.uuid4().hex, "at_utc": stamp(), "kind": kind, "summary": summary, "evidence": evidence or {}, "provenance": "agent-or-user-reported; not independently verified by harness"}
        data = (json.dumps(row, ensure_ascii=False)+"\n").encode("utf-8")
        with self.path("events.jsonl").open("ab") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return row

    def save(self, name, content, expected_sha):
        if not isinstance(content, str) or len(content.encode("utf-8")) > 65_536:
            raise ValueError("content must be UTF-8 text up to 64 KiB")
        if not isinstance(expected_sha, str):
            raise ValueError("expected_sha is required; read the current artifact first")
        with self.lock():
            previous = self.read(name)
            if expected_sha != previous["sha256"]:
                raise ValueError("artifact changed; reread before saving")
            data = content.encode("utf-8")
            sha = digest(data)
            if sha == previous["sha256"]:
                return {"saved": False, "name": name, "sha256": sha, "reason": "unchanged"}
            history_dir = self.path("history")
            if history_dir.is_symlink() or not history_dir.is_dir():
                raise ValueError("unsafe or missing history directory")
            backup = self.path(f"history/{name}-{uuid.uuid4().hex}.md")
            atomic_write(backup, previous["content"].encode("utf-8"))
            intent = self._event("artifact_save_started", name, {"before_sha256": previous["sha256"], "intended_sha256": sha, "previous_copy": str(backup.relative_to(self.home))})
            atomic_write(self.path(f"{name}.md"), data)
            self._event("artifact_saved", name, {"operation_id": intent["id"], "sha256": sha})
            return {"saved": True, "name": name, "sha256": sha}

    def log(self, kind, summary, evidence=None):
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError("invalid event kind")
        if not isinstance(summary, str) or not summary.strip() or len(summary) > 2000:
            raise ValueError("summary must contain 1..2000 characters")
        if evidence is not None and not isinstance(evidence, dict):
            raise ValueError("evidence must be a JSON object")
        if len(json.dumps(evidence or {}, ensure_ascii=False).encode("utf-8")) > 16_384:
            raise ValueError("evidence exceeds 16 KiB")
        status = (evidence or {}).get("status")
        if kind == "verification" and (not isinstance(status, str) or status not in {"passed", "failed", "not-run"}):
            raise ValueError("verification evidence requires status: passed, failed, or not-run")
        with self.lock():
            return self._event(kind, summary, evidence)

    def state(self, limit=10):
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError("event limit must be 1..50")
        with self.lock():
            artifacts = [{"name": name, "sha256": self.read(name)["sha256"]} for name in ARTIFACTS]
            # Partial final JSON line after a crash is reported, never silently discarded.
            lines = self.path("events.jsonl").read_text(encoding="utf-8").splitlines()
            events = [json.loads(line) for line in lines[-limit:]]
        return {"artifacts": artifacts, "recent_events": events, "event_count": len(lines), "note": "Artifact hashes establish saved state; event claims require checking actual code and outputs."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="explicit task directory; only its .agent/ is managed")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("state")
    read = sub.add_parser("read"); read.add_argument("name", choices=ARTIFACTS)
    save = sub.add_parser("save"); save.add_argument("name", choices=ARTIFACTS); save.add_argument("--file", required=True); save.add_argument("--expected-sha", required=True)
    log = sub.add_parser("log"); log.add_argument("kind", choices=sorted(KINDS)); log.add_argument("summary"); log.add_argument("--evidence-json", default="{}")
    args = parser.parse_args()
    try:
        flow = Workflow(args.workspace)
        if args.command == "init": result = flow.initialize()
        elif args.command == "state": result = flow.state()
        elif args.command == "read": result = flow.read(args.name)
        elif args.command == "save": result = flow.save(args.name, Path(args.file).read_text(encoding="utf-8"), args.expected_sha)
        else: result = flow.log(args.kind, args.summary, json.loads(args.evidence_json))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.exit(2, str(error)+"\n")


if __name__ == "__main__":
    main()
