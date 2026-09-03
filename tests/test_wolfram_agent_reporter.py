import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


watcher = load("watcher_for_reporter", ROOT / "tools/wolfram-agent-watcher")
reporter = load("reporter", ROOT / "tools/wolfram-agent-reporter")


def issue(risk="R1", author="pashamango", agent="codex@wolfram.local", number=8,
          extra=""):
    body = f"""{watcher.MARKER}
```yaml
id: MAILBOX-0003
type: infrastructure-bootstrap
agent: {agent}
host: Wolfram
status: ready
risk: {risk}
mode: bounded-dispatch
```
Harmless task. {extra}
"""
    return {"number": number, "title": "MAILBOX-0003", "author": {"login": author},
            "url": f"https://github.com/{watcher.EXPECTED_REPOSITORY}/issues/{number}",
            "createdAt": "2026-09-03T00:00:00Z", "updatedAt": "2026-09-03T00:00:00Z",
            "state": "OPEN", "body": body}


class FakeClient:
    def __init__(self, item, fail=False):
        self.item = item
        self.fail = fail
        self.items = []
        self.posts = []

    def issue(self, repository, number):
        return self.item

    def comments(self, repository, number):
        return self.items

    def post(self, repository, number, body):
        if self.fail:
            raise RuntimeError("offline secret=must-not-leak")
        self.posts.append((repository, number, body))
        self.items.append({"body": body})


class ReporterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.run = Path(self.temp.name) / "runs/MAILBOX-0003/0123456789abcdef0123456789abcdef"
        self.run.mkdir(parents=True)
        self.item = issue(extra="model says token=TOP_SECRET and $(touch PWNED)")
        digest = __import__("hashlib").sha256(
            watcher.normalized_payload(watcher.EXPECTED_REPOSITORY, self.item).encode()).hexdigest()
        self.envelope = {"protocol": "chitakasha-task-envelope/v1", "task_id": "MAILBOX-0003",
                         "source_repository": watcher.EXPECTED_REPOSITORY, "source_issue": 8,
                         "source_url": self.item["url"], "source_sha256": digest,
                         "author": "pashamango", "agent": "codex@wolfram.local", "risk": "R1",
                         "claimed_at": "2026-09-03T00:01:00Z",
                         "lease_id": "0123456789abcdef0123456789abcdef"}
        self.claim = {"task_id": "MAILBOX-0003", "issue_number": 8,
                      "source_digest": digest, "agent": "codex@wolfram.local",
                      "claimed_at": "2026-09-03T00:01:00Z",
                      "lease_id": self.envelope["lease_id"], "status": "claimed"}
        self.result = {"task_id": "MAILBOX-0003", "lease_id": self.envelope["lease_id"],
                       "source_digest": digest, "started_at": "2026-09-03T00:01:01Z",
                       "finished_at": "2026-09-03T00:01:02Z", "process_exit_status": 0,
                       "terminal_state": "completed", "stdout_sha256": "a" * 64,
                       "stderr_sha256": "b" * 64}
        for name, value in (("envelope.json", self.envelope), ("claim.json", self.claim),
                            ("result.json", self.result)):
            (self.run / name).write_text(json.dumps(value) + "\n")
        inbox = self.run.parents[2] / "inbox"
        inbox.mkdir()
        record = {"repository": watcher.EXPECTED_REPOSITORY, "issue_number": 8,
                  "source_sha256": digest, "author_login": "pashamango",
                  "updated_at": self.item["updatedAt"]}
        (inbox / f"repo__8__{digest}.json").write_text(json.dumps(record) + "\n")

    def tearDown(self):
        self.temp.cleanup()

    def test_claim_posts_once_and_is_idempotent(self):
        client = FakeClient(self.item)
        self.assertEqual(reporter.report(self.run, "CLAIMED", client, watcher), "posted")
        self.assertEqual(reporter.report(self.run, "CLAIMED", client, watcher), "already_reported")
        self.assertEqual(len(client.posts), 1)

    def test_completed_payload_is_allowlisted_and_does_not_leak_input(self):
        client = FakeClient(self.item)
        self.assertEqual(reporter.report(self.run, "COMPLETED", client, watcher), "posted")
        body = client.posts[0][2]
        self.assertIn("COMPLETED", body)
        self.assertIn("result_sha256:", body)
        self.assertNotIn("TOP_SECRET", body)
        self.assertNotIn("touch PWNED", body)
        keys = {line.split(":", 1)[0] for line in body.splitlines() if ":" in line
                and not line.startswith("<!--")}
        self.assertEqual(keys, set(reporter.COMMON_FIELDS + reporter.TERMINAL_FIELDS + ("receipt_key",)))

    def test_all_terminal_states(self):
        for local, remote in reporter.TERMINAL_STATES.items():
            with self.subTest(local=local):
                self.result["terminal_state"] = local
                self.result["process_exit_status"] = None if local in {"blocked", "timed_out"} else 7
                (self.run / "result.json").write_text(json.dumps(self.result) + "\n")
                client = FakeClient(self.item)
                body, _ = reporter.receipt_payload(
                    remote, self.envelope, self.claim, self.result, self.run)
                self.assertIn(f"\n{remote}\n", body)

    def test_digest_mismatch_never_posts(self):
        client = FakeClient(issue(extra="revision"))
        with self.assertRaisesRegex(ValueError, "digest"):
            reporter.report(self.run, "CLAIMED", client, watcher)
        self.assertEqual(client.posts, [])

    def test_wrong_repository_issue_agent_and_risk_never_post(self):
        mutations = (("source_repository", "evil/repo"), ("source_issue", 9),
                     ("agent", "other"), ("risk", "R2"))
        for field, value in mutations:
            with self.subTest(field=field):
                changed = dict(self.envelope)
                changed[field] = value
                (self.run / "envelope.json").write_text(json.dumps(changed) + "\n")
                client = FakeClient(self.item)
                with self.assertRaises(ValueError):
                    reporter.report(self.run, "CLAIMED", client, watcher)
                self.assertEqual(client.posts, [])
        (self.run / "envelope.json").write_text(json.dumps(self.envelope) + "\n")

    def test_remote_existing_key_prevents_duplicate(self):
        client = FakeClient(self.item)
        body, key = reporter.receipt_payload("CLAIMED", self.envelope, self.claim, None, self.run)
        client.items = [{"body": f"prior {key}"}]
        self.assertEqual(reporter.report(self.run, "CLAIMED", client, watcher), "already_reported")
        self.assertEqual(client.posts, [])

    def test_github_failure_preserves_local_result_and_is_bounded(self):
        before = (self.run / "result.json").read_bytes()
        client = FakeClient(self.item, fail=True)
        with self.assertRaises(RuntimeError):
            reporter.report(self.run, "COMPLETED", client, watcher)
        reporter.record_failure(self.run, "COMPLETED", RuntimeError("secret=must-not-leak"))
        self.assertEqual((self.run / "result.json").read_bytes(), before)
        failure = (self.run / "writeback/completed.failure.json").read_text()
        self.assertNotIn("must-not-leak", failure)
        self.assertEqual(len(client.posts), 0)


if __name__ == "__main__":
    unittest.main()
