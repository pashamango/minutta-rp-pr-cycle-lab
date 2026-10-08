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
        self.prs = {}

    def issue(self, repository, number):
        return self.item

    def comments(self, repository, number):
        return self.items

    def post(self, repository, number, body):
        if self.fail:
            raise RuntimeError("offline secret=must-not-leak")
        self.posts.append((repository, number, body))
        self.items.append({"body": body})

    def pull_request(self, repository, number):
        if number not in self.prs:
            raise RuntimeError("pull request absent")
        return self.prs[number]


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
                       "terminal_state": "execution_finished", "stdout_sha256": "a" * 64,
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

    def write_outcome(self, **changes):
        value = {"protocol": "chitakasha-task-outcome/v1", "task_id": "MAILBOX-0003",
                 "lease_id": self.envelope["lease_id"], "source_sha256": self.envelope["source_sha256"],
                 "status": "completed", "summary": "bounded result", "artifacts": [],
                 "checks": [{"name": "tests", "status": "pass"}]}
        value.update(changes)
        (self.run / "task-outcome.json").write_text(json.dumps(value) + "\n")

    def test_execution_payload_is_allowlisted_and_does_not_leak_input(self):
        client = FakeClient(self.item)
        self.assertEqual(reporter.report(self.run, "EXECUTION_FINISHED", client, watcher), "posted")
        body = client.posts[0][2]
        self.assertIn("EXECUTION_FINISHED", body)
        self.assertIn("result_sha256:", body)
        self.assertNotIn("TOP_SECRET", body)
        self.assertNotIn("touch PWNED", body)
        keys = {line.split(":", 1)[0] for line in body.splitlines() if ":" in line
                and not line.startswith("<!--")}
        self.assertEqual(keys, set(reporter.COMMON_FIELDS + reporter.EXECUTION_FIELDS + ("receipt_key",)))

    def test_all_execution_states(self):
        for local, remote in reporter.EXECUTION_STATES.items():
            with self.subTest(local=local):
                self.result["terminal_state"] = local
                self.result["process_exit_status"] = 0 if local == "execution_finished" else 7
                (self.run / "result.json").write_text(json.dumps(self.result) + "\n")
                client = FakeClient(self.item)
                body, _ = reporter.receipt_payload(
                    remote, self.envelope, self.claim, self.result, self.run)
                self.assertIn(f"\n{remote}\n", body)

    def test_valid_bound_outcome_posts_task_completed_idempotently(self):
        self.write_outcome()
        client = FakeClient(self.item)
        self.assertEqual(reporter.report(self.run, "TASK_OUTCOME", client, watcher), "posted")
        self.assertIn("\nTASK_COMPLETED\n", client.posts[0][2])
        self.assertEqual(reporter.report(self.run, "TASK_OUTCOME", client, watcher), "already_reported")

    def test_task_outcome_writes_bounded_validation_record(self):
        self.write_outcome(summary="secret=fixture; raw worker log")
        client = FakeClient(self.item)
        self.assertEqual(reporter.report(self.run, "TASK_OUTCOME", client, watcher), "posted")
        record = json.loads((self.run / "writeback/validation-record.json").read_text())
        self.assertEqual(record["protocol"], reporter.VALIDATION_PROTOCOL)
        self.assertEqual(record["remote_state"], "posted")
        self.assertEqual(record["validation_timestamp"], self.result["finished_at"])
        self.assertNotIn("secret", json.dumps(record))
        self.assertNotIn("summary", record)
        self.assertEqual(record["reporter_authority"], reporter.REPORTER_AUTHORITY)
        self.assertEqual(record["reporter_protocol"], reporter.REPORTER_PROTOCOL)
        self.assertNotEqual(record["reporter_authority"], self.envelope["agent"])
        self.assertEqual(len(record), 17)

    def test_existing_marker_requires_exact_schema_and_provenance(self):
        self.write_outcome()
        client = FakeClient(self.item)
        body, key = reporter.receipt_payload("TASK_COMPLETED", self.envelope, self.claim,
                                             self.result, self.run,
                                             json.loads((self.run / "task-outcome.json").read_text()), [])
        marker = self.run / "writeback/task_completed.json"
        marker.parent.mkdir()
        cases = [
            {"receipt_key": key, "state": "TASK_COMPLETED"},
            {"receipt_key": "sha256:" + "0" * 64, "state": "TASK_COMPLETED", "remote": "posted"},
            {"receipt_key": key, "state": "TASK_FAILED", "remote": "posted"},
            {"receipt_key": key, "state": "TASK_COMPLETED", "remote": "unknown"},
            {"receipt_key": key, "state": "TASK_COMPLETED", "remote": "posted", "extra": "x"},
        ]
        for value in cases:
            with self.subTest(value=value):
                marker.write_text(json.dumps(value) + "\n")
                with self.assertRaises(ValueError):
                    reporter.report(self.run, "TASK_OUTCOME", client, watcher)
                self.assertFalse((self.run / "writeback/validation-record.json").exists())

    def test_existing_remote_receipt_replay_is_idempotent(self):
        self.write_outcome()
        client = FakeClient(self.item)
        body, key = reporter.receipt_payload("TASK_COMPLETED", self.envelope, self.claim,
                                             self.result, self.run,
                                             json.loads((self.run / "task-outcome.json").read_text()), [])
        client.items = [{"body": body}]
        self.assertEqual(reporter.report(self.run, "TASK_OUTCOME", client, watcher), "already_reported")
        self.assertEqual(reporter.report(self.run, "TASK_OUTCOME", client, watcher), "already_reported")
        self.assertEqual(len(client.posts), 0)

    def test_conflicting_validation_record_fails_closed(self):
        self.write_outcome()
        client = FakeClient(self.item)
        reporter.report(self.run, "TASK_OUTCOME", client, watcher)
        path = self.run / "writeback/validation-record.json"
        value = json.loads(path.read_text())
        value["receipt_key"] = "sha256:" + "f" * 64
        path.chmod(0o644)
        path.write_text(json.dumps(value) + "\n")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            reporter.report(self.run, "TASK_OUTCOME", client, watcher)

    def test_wrong_task_lease_or_source_is_rejected(self):
        for field, value in (("task_id", "MAILBOX-WRONG"), ("lease_id", "f" * 32),
                             ("source_sha256", "f" * 64)):
            with self.subTest(field=field):
                self.write_outcome(**{field: value})
                with self.assertRaisesRegex(ValueError, "binding"):
                    reporter.report(self.run, "TASK_OUTCOME", FakeClient(self.item), watcher)

    def test_malformed_outcome_is_rejected(self):
        self.write_outcome(extra="not allowed")
        with self.assertRaisesRegex(ValueError, "schema"):
            reporter.report(self.run, "TASK_OUTCOME", FakeClient(self.item), watcher)

    def test_pr_absent_rejects_task_completion(self):
        self.write_outcome(artifacts=[{"type": "pr", "ref": "#42"}])
        with self.assertRaises(RuntimeError):
            reporter.report(self.run, "TASK_OUTCOME", FakeClient(self.item), watcher)

    def test_pr_present_and_bound_accepts_task_completion(self):
        self.write_outcome(artifacts=[{"type": "pr", "ref": "#42"}])
        client = FakeClient(self.item)
        client.prs[42] = {"base": {"ref": "main", "repo": {"full_name": watcher.EXPECTED_REPOSITORY}},
                          "head": {"ref": "agent/wolfram/MAILBOX-0003"}}
        self.assertEqual(reporter.report(self.run, "TASK_OUTCOME", client, watcher), "posted")
        self.assertIn('evidence_validation: ["pr:42:repository_branch_base"]', client.posts[0][2])

    def test_malicious_stdout_cannot_create_completion(self):
        self.assertFalse((self.run / "task-outcome.json").exists())
        with self.assertRaises(FileNotFoundError):
            reporter.report(self.run, "TASK_OUTCOME", FakeClient(self.item), watcher)

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
            reporter.report(self.run, "EXECUTION_FINISHED", client, watcher)
        reporter.record_failure(self.run, "EXECUTION_FINISHED", RuntimeError("secret=must-not-leak"))
        self.assertEqual((self.run / "result.json").read_bytes(), before)
        failure = (self.run / "writeback/execution_finished.failure.json").read_text()
        self.assertNotIn("must-not-leak", failure)
        self.assertEqual(len(client.posts), 0)


if __name__ == "__main__":
    unittest.main()
