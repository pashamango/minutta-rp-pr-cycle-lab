import json
import tempfile
import unittest
from pathlib import Path
import subprocess

from evidence_publication import EvidencePublisher, PublicationError


class EvidencePublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        self.publisher = EvidencePublisher(self.root)
        self.kw = dict(task_id="SYNTHETIC-SCHEDULER-0001", source_digest="a" * 64,
                       lease_id="b" * 32, artifacts=[{"type": "report", "ref": "artifacts/a.md"}],
                       checks=[{"type": "test", "ref": "checks/a.json"}], outcome_ref="outcome.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_publish_precedes_independent_blocked_settlement_and_is_restart_safe(self):
        first = self.publisher.publish(**self.kw)
        self.assertEqual(first["status"], "EVIDENCE_PUBLISHED")
        self.assertTrue((self.root / "evidence/published/SYNTHETIC-SCHEDULER-0001" / ("b" * 32) / "manifest.json").exists())
        decision = self.publisher.settle(first, "blocked")
        self.assertEqual(decision.status, "blocked")
        resumed = self.publisher.resume(self.kw["task_id"], self.kw["lease_id"])
        self.assertEqual(resumed["publication_identity"], first["publication_identity"])
        second = self.publisher.publish(**self.kw)
        self.assertEqual(second["publication_identity"], first["publication_identity"])

    def test_exact_binding_and_failure_are_explicit(self):
        self.publisher.publish(**self.kw)
        with self.assertRaises(PublicationError):
            self.publisher.publish(**{**self.kw, "lease_id": "c" * 32})
        with self.assertRaisesRegex(PublicationError, "retryable"):
            self.publisher.publish(**self.kw, fail=True)
        with self.assertRaises(PublicationError):
            self.publisher.resume(self.kw["task_id"], self.kw["lease_id"])

    def test_three_artifacts_remain_reviewable_when_reporter_blocks(self):
        args = {**self.kw, "task_id": "REGRESSION-130", "artifacts": [
            {"type": "report", "ref": "artifacts/one.md"},
            {"type": "report", "ref": "artifacts/two.md"},
            {"type": "test", "ref": "checks/three.json"}]}
        published = self.publisher.publish(**args)
        self.assertEqual(len(published["artifact_refs"]), 3)
        self.assertEqual(self.publisher.settle(published, "blocked").status, "blocked")
        self.assertEqual(len(self.publisher.resume("REGRESSION-130", "b" * 32)["artifact_refs"]), 3)

    def test_comment_only_ref_is_data_not_continuation_authority(self):
        published = self.publisher.publish(**{**self.kw, "outcome_ref": "comment:continue"})
        self.assertEqual(published["outcome_ref"], "comment:continue")
        self.assertEqual(self.publisher.settle(published, "blocked").status, "blocked")


if __name__ == "__main__":
    unittest.main()
