import json
import tempfile
import unittest
from pathlib import Path
from rp_factory.cycle import build, run_cycle, publish_bundle

ANOMALY = {"anomaly_id": "fixture-001", "observation": "repeatable mismatch", "source_receipt": "receipt-001", "owner": "codex@wolfram", "cost": "0 credits", "risk": "L1", "confidence": 0.9}

class RPFactoryTests(unittest.TestCase):
  def test_blocked_without_explicit_authorization(self):
    with tempfile.TemporaryDirectory() as d:
      tmp_path = Path(d); build(ANOMALY, tmp_path)
      self.assertEqual(run_cycle(tmp_path, False, None)["status"], "BLOCKED")
      self.assertFalse((tmp_path / "github-pr-proposal.json").exists())

  def test_pass_then_separate_publication_bundle(self):
    with tempfile.TemporaryDirectory() as d:
      tmp_path = Path(d); build(ANOMALY, tmp_path)
      self.assertEqual(run_cycle(tmp_path, True, "true")["status"], "PASSED")
      self.assertEqual(publish_bundle(tmp_path)["private_evidence"], ["proposal.json", "fixture.json", "issue.json"])

  def test_failed_outcome_cannot_publish(self):
    with tempfile.TemporaryDirectory() as d:
      tmp_path = Path(d); build(ANOMALY, tmp_path)
      self.assertEqual(run_cycle(tmp_path, True, "false")["status"], "FAILED")
      with self.assertRaises(ValueError): publish_bundle(tmp_path)
