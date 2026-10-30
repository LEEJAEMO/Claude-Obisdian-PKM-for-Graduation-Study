import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kit import Knowledge
from server import Session, PROTOCOL


def request(method, params=None, ident=1):
    return dict(jsonrpc="2.0", id=ident, method=method, params=params or {})


def ready():
    s = Session()
    s.handle(request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "local-test", "version": "1"}}))
    s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
    return s


class WorkbenchTests(unittest.TestCase):
    def test_catalog_integrity(self):
        self.assertEqual(Knowledge().check()["entries"], 12)

    def test_task_queries(self):
        # Expected IDs were chosen from task intent, not generated search scores.
        cases = [("요구 stakeholder", "module", "M-REQ"), ("CSV Excel", "troubleshooting", "T-015"),
                 ("UnicodeEncodeError cp949", "troubleshooting", "T-007"),
                 ("FileNotFoundError", "troubleshooting", "T-005"),
                 ("자체 보고", "troubleshooting", "T-006"), ("environment MCP", "spec", "S-ENV")]
        for query, kind, ident in cases:
            with self.subTest(query=query):
                rows = Knowledge().search(query, kind)["matches"]
                self.assertIn(ident, [r["id"] for r in rows])
                self.assertTrue(all(r["kind"] == kind for r in rows))
                self.assertTrue(all("content" not in r for r in rows))

    def test_no_match_is_empty(self):
        self.assertEqual(Knowledge().search("zzznomatch1234")["matches"], [])

    def test_bounded_and_invalid_search(self):
        db = Knowledge()
        self.assertLessEqual(len(db.search("데이터", limit=1)["matches"]), 1)
        for args in [("",), ("x" * 1001,), ("x", "invalid"), ("x", "all", 0), ("x", "all", True)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                db.search(*args)

    def test_unknown_id_cannot_read_paths(self):
        for ident in ["../README.md", "/etc/passwd", "M-999", 3]:
            with self.subTest(ident=ident), self.assertRaises(ValueError):
                Knowledge().read(ident)

    def test_catalog_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "copy"
            shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns("__pycache__"))
            catalog = json.loads((dest / "catalog.json").read_text(encoding="utf-8"))
            catalog[0]["path"] = "../secret.md"
            (dest.parent / "secret.md").write_text("not knowledge", encoding="utf-8")
            (dest / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside"):
                Knowledge(dest)

    def test_tampered_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "copy"
            shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns("__pycache__"))
            db = Knowledge(dest)
            (dest / db.entries[0]["path"]).write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                db.read(db.entries[0]["id"])

    def test_initialize_gate_and_tool_inventory(self):
        self.assertIn("error", Session().handle(request("tools/list")))
        s = ready()
        tools = s.handle(request("tools/list"))["result"]["tools"]
        self.assertEqual({t["name"] for t in tools}, {"pkm_search", "pkm_read"})
        self.assertTrue(all(t["annotations"]["readOnlyHint"] for t in tools))

    def test_tool_error_distinguished_from_protocol_error(self):
        s = ready()
        self.assertTrue(s.handle(request("tools/call", {"name": "pkm_read", "arguments": {"id": "M-999"}}))["result"]["isError"])
        self.assertEqual(s.handle(request("tools/call", {"name": "run_shell"}))["error"]["code"], -32602)
        self.assertEqual(s.handle(request("tools/call", {"name": [], "arguments": {}}))["error"]["code"], -32602)

    def test_bad_arguments(self):
        s = ready()
        for args in [[], {"query": "x", "shell": "x"}, {}]:
            self.assertIn("error", s.handle(request("tools/call", {"name": "pkm_search", "arguments": args})))
        self.assertTrue(s.handle(request("tools/call", {"name": "pkm_search", "arguments": {"query": 1}}))["result"]["isError"])

    def test_invalid_jsonrpc_and_unknown_method(self):
        self.assertEqual(Session().handle([])["error"]["code"], -32600)
        self.assertEqual(ready().handle(request("unknown"))["error"]["code"], -32601)
        self.assertIsNone(ready().handle({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 7}}))

    def test_stdio_real_subprocess(self):
        messages = [request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "stdio-test", "version": "1"}}, 1),
                    {"jsonrpc": "2.0", "method": "notifications/initialized"}, request("tools/list", ident=2),
                    request("tools/call", {"name": "pkm_search", "arguments": {"query": "요구 stakeholder", "kind": "module"}}, 3),
                    request("tools/call", {"name": "pkm_read", "arguments": {"id": "M-REQ"}}, 4)]
        data = "\n".join(json.dumps(m, ensure_ascii=False) for m in messages) + "\n{bad json}\n"
        run = subprocess.run([sys.executable, "-B", "-X", "utf8", str(ROOT / "server.py")], input=data, encoding="utf-8", capture_output=True, cwd=ROOT.parent, timeout=15)
        self.assertEqual(run.returncode, 0, run.stderr)
        lines = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0]["result"]["protocolVersion"], PROTOCOL)
        self.assertEqual(len(lines[1]["result"]["tools"]), 2)
        self.assertFalse(lines[2]["result"]["isError"])
        self.assertIn("M-REQ", lines[3]["result"]["content"][0]["text"])
        self.assertEqual(lines[4]["error"]["code"], -32700)

    def test_portable_copy_and_file_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "새 폴더 with spaces"
            shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns("__pycache__"))
            def hashes():
                return {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob("*") if p.is_file()}
            before = hashes()
            run = subprocess.run([sys.executable, "-B", "-X", "utf8", str(dest / "kit.py"), "read", "T-007"], capture_output=True, encoding="utf-8", cwd=tmp, timeout=15)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["id"], "T-007")
            self.assertEqual(before, hashes())


if __name__ == "__main__":
    unittest.main()
