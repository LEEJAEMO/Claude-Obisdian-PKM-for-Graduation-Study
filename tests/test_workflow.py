from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import workflow
from workflow import Workflow, ARTIFACTS
from server import Session, TOOLS, PROTOCOL


def request(method, params=None, ident=1):
    return {"jsonrpc": "2.0", "id": ident, "method": method, "params": params or {}}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        # Keep sandboxed test writes inside this explicitly writable checkout.
        self.tmp = tempfile.TemporaryDirectory(prefix="workflow-test-", dir=ROOT)
        self.root = Path(self.tmp.name) / "작업 폴더 with spaces"
        self.root.mkdir()
        (self.root / "task.txt").write_bytes(b"original task input\n")
        self.flow = Workflow(self.root)
        self.flow.initialize()

    def tearDown(self):self.tmp.cleanup()

    def session(self):
        s = Session(self.flow)
        s.handle(request("initialize", {"protocolVersion": PROTOCOL, "clientInfo": {"name": "test", "version": "1"}, "capabilities": {}}))
        s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return s

    def test_init_is_empty_idempotent_and_preserves_task(self):
        self.assertEqual(set(a["name"] for a in self.flow.state()["artifacts"]), set(ARTIFACTS))
        self.assertIn("not yet confirmed", self.flow.read("spec")["content"])
        self.assertIn("No checks executed", self.flow.read("evidence")["content"])
        self.assertFalse(self.flow.initialize()["initialized"])
        self.assertEqual((self.root / "task.txt").read_bytes(), b"original task input\n")
        self.assertEqual(self.flow.state()["event_count"], 1)

    def test_unrelated_agent_directory_is_never_adopted(self):
        target = self.root / "other";target.mkdir();(target / ".agent").mkdir()
        original = target / ".agent" / "private.txt"; original.write_bytes(b"keep")
        with self.assertRaises(ValueError):Workflow(target).initialize()
        self.assertEqual(original.read_bytes(), b"keep")
        self.assertEqual(list((target / ".agent").iterdir()), [original])

    def test_spec_revision_history_and_event_log(self):
        old = self.flow.read("spec")
        self.flow.save("spec", "# Spec\nR-001: Show an empty state for zero items.\n", old["sha256"])
        current = self.flow.read("spec")
        self.flow.save("spec", current["content"]+"R-002: Reject unknown status labels.\n", current["sha256"])
        backups = list((self.root / ".agent/history").glob("spec-*.md"))
        self.assertEqual(len(backups), 2)
        self.assertIn(old["content"], [p.read_text(encoding="utf-8") for p in backups])
        events = self.flow.state()["recent_events"]
        self.assertEqual([e["kind"] for e in events].count("artifact_saved"), 2)
        self.assertEqual(events[-1]["evidence"]["sha256"], self.flow.read("spec")["sha256"])

    def test_stale_writer_cannot_overwrite(self):
        original = self.flow.read("plan")["sha256"]
        self.flow.save("plan", "first writer", original)
        with self.assertRaisesRegex(ValueError, "changed"):
            self.flow.save("plan", "stale writer", original)
        self.assertEqual(self.flow.read("plan")["content"], "first writer")

    def test_same_content_does_not_create_history(self):
        before = self.flow.state()["event_count"]
        old = self.flow.read("spec")
        self.assertFalse(self.flow.save("spec", old["content"], old["sha256"])["saved"])
        self.assertEqual(self.flow.state()["event_count"], before)

    def test_actual_scope_rejects_arbitrary_files_and_large_content(self):
        for name in ["../task.txt", "manifest", "/tmp/outside", "history/spec"]:
            with self.subTest(name=name), self.assertRaises(ValueError):self.flow.read(name)
        with self.assertRaises(ValueError):self.flow.save("spec", "가"*65536, "x")
        self.assertEqual((self.root / "task.txt").read_bytes(), b"original task input\n")

    def test_log_append_keeps_existing_bytes_and_reports_provenance(self):
        path = self.root / ".agent/events.jsonl";before=path.read_bytes()
        e = self.flow.log("verification", "Synthetic test: command not executed", {"status": "not-run", "command": "example only"})
        self.assertTrue(path.read_bytes().startswith(before))
        self.assertIn("not independently verified", e["provenance"])
        for evidence in [{}, {"status": "success"}, {"status": []}]:
            with self.assertRaises(ValueError):self.flow.log("verification", "invalid result", evidence)

    def test_interrupted_save_does_not_log_success(self):
        old = self.flow.read("spec")
        real = workflow.atomic_write
        def fail_artifact(path, data):
            if path.name == "spec.md":raise OSError("simulated interruption")
            return real(path,data)
        with patch("workflow.atomic_write",side_effect=fail_artifact), self.assertRaises(OSError):
            self.flow.save("spec", "attempted change", old["sha256"])
        self.assertEqual(self.flow.read("spec")["sha256"], old["sha256"])
        self.assertEqual(self.flow.state()["recent_events"][-1]["kind"], "artifact_save_started")

    def test_concurrent_writers_are_serialized_and_stale_one_rejected(self):
        sha = self.flow.read("spec")["sha256"]
        def save(text):
            try:self.flow.save("spec",text,sha);return "saved"
            except ValueError:return "stale"
        with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(save,["writer one","writer two"]))
        self.assertCountEqual(result,["saved","stale"])
        self.assertEqual(len(list((self.root / ".agent/history").iterdir())),1)

    def test_malformed_log_is_reported(self):
        with (self.root / ".agent/events.jsonl").open("ab") as f:f.write(b'{"partial":')
        with self.assertRaises(ValueError):self.flow.state()

    def test_resume_reads_saved_state_and_actual_hashes(self):
        old=self.flow.read("status")
        self.flow.save("status","Completed: spec only. Next: implement the empty-state path.",old["sha256"])
        resumed=Workflow(self.root)
        self.assertIn("spec only",resumed.read("status")["content"])
        current={a["name"]:a["sha256"] for a in resumed.state()["artifacts"]}
        self.assertEqual(current["status"],hashlib.sha256((self.root / ".agent/status.md").read_bytes()).hexdigest())

    def test_mcp_lifecycle_inventory_errors_and_writes(self):
        self.assertIn("error",Session(self.flow).handle(request("tools/list")))
        session=self.session()
        names={t["name"]:t for t in session.handle(request("tools/list"))["result"]["tools"]}
        self.assertEqual(set(names),{"agent_brief","agent_state","agent_read","agent_save","agent_log"})
        self.assertFalse(names["agent_save"]["annotations"]["readOnlyHint"])
        bad=session.handle(request("tools/call",{"name":"agent_read","arguments":{"name":"../task.txt"}}))
        self.assertTrue(bad["result"]["isError"])
        self.assertIn("error",session.handle(request("tools/call",{"name":"execute_shell"})))
        old=self.flow.read("spec")
        result=session.handle(request("tools/call",{"name":"agent_save","arguments":{"name":"spec","content":"MCP saved spec","expected_sha":old["sha256"]}}))
        self.assertFalse(result["result"]["isError"])
        self.assertEqual(self.flow.read("spec")["content"],"MCP saved spec")

    def test_real_stdio_read_save_log_resume_round_trip(self):
        sha=self.flow.read("spec")["sha256"]
        messages=[request("initialize",{"protocolVersion":PROTOCOL,"capabilities":{},"clientInfo":{"name":"subprocess","version":"1"}},1),
                  {"jsonrpc":"2.0","method":"notifications/initialized"},request("tools/list",ident=2),
                  request("tools/call",{"name":"agent_save","arguments":{"name":"spec","content":"R-001: synthetic subprocess requirement","expected_sha":sha}},3),
                  request("tools/call",{"name":"agent_log","arguments":{"kind":"decision","summary":"Synthetic test decision"}},4),
                  request("tools/call",{"name":"agent_state"},5),
                  request("tools/call",{"name":"agent_brief"},6)]
        run=subprocess.run([sys.executable,"-B","-X","utf8",str(ROOT/"server.py"),"--workspace",str(self.root)],input="\n".join(map(json.dumps,messages))+"\n",capture_output=True,encoding="utf-8",cwd=self.tmp.name,timeout=15)
        self.assertEqual(run.returncode,0,run.stderr)
        replies=[json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual(len(replies),6)
        self.assertTrue(all(not r.get("result",{}).get("isError",False) for r in replies))
        self.assertIn("R-001",Workflow(self.root).read("spec")["content"])
        self.assertEqual(Workflow(self.root).state()["event_count"],4)
        brief=json.loads(replies[-1]["result"]["content"][0]["text"])
        self.assertIn("R-001",brief["sections"][0]["excerpt"])

    def test_real_cli_init_and_read_from_other_directory(self):
        target=self.root/"new task";target.mkdir()
        cmd=[sys.executable,"-B","-X","utf8",str(ROOT/"workflow.py"),"--workspace",str(target)]
        for suffix in [["init"],["read","spec"],["state"],["brief"]]:
            run=subprocess.run(cmd+suffix,cwd=self.tmp.name,capture_output=True,encoding="utf-8",timeout=15)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertIsInstance(json.loads(run.stdout),dict)

    def test_brief_reads_current_context_without_creating_records(self):
        for name,content in [("spec","R-001: group requests by status"),("status","In progress: grouping; not-run: empty input check")]:
            old=self.flow.read(name);self.flow.save(name,content,old["sha256"])
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        brief=self.flow.brief()
        sections={s["name"]:s for s in brief["sections"]}
        self.assertIn("R-001",sections["spec"]["excerpt"])
        self.assertIn("not-run",sections["status"]["excerpt"])
        self.assertEqual(sections["status"]["sha256"],self.flow.read("status")["sha256"])
        self.assertEqual(before,{str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_brief_marks_truncation_and_has_no_duplicate_summary_file(self):
        old=self.flow.read("spec");self.flow.save("spec","x"*600,old["sha256"])
        result=self.flow.brief(200);section=result["sections"][0]
        self.assertTrue(section["truncated"]);self.assertEqual(len(section["excerpt"]),200)
        self.assertFalse((self.root/".agent/brief.md").exists())
        for n in [0,True,4001]:
            with self.assertRaises(ValueError):self.flow.brief(n)

    def test_mcp_brief_reflects_updates_without_gating_implementation(self):
        session=self.session();old=self.flow.read("plan")
        self.flow.save("plan","Next: implement parser in src/parser.py",old["sha256"])
        reply=session.handle(request("tools/call",{"name":"agent_brief"}))
        self.assertFalse(reply["result"]["isError"])
        data=json.loads(reply["result"]["content"][0]["text"])
        self.assertIn("src/parser.py",next(s["excerpt"] for s in data["sections"] if s["name"]=="plan"))
        # Normal host-side coding is unaffected by unfinished spec/evidence records.
        (self.root/"implementation.py").write_text("answer = 42\n",encoding="utf-8")
        self.assertEqual((self.root/"implementation.py").read_text(encoding="utf-8"),"answer = 42\n")


if __name__=="__main__":unittest.main()
