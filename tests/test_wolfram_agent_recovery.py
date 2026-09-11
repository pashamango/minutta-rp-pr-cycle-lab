import importlib.machinery
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("recovery", str(ROOT / "tools/wolfram-agent-recovery"))
recovery = loader.load_module()


class RecoveryTests(unittest.TestCase):
    def run_dir(self, outcome=False):
        temp = tempfile.TemporaryDirectory()
        run = Path(temp.name)
        binding = {"task_id": "TASK-1", "source_sha256": "a" * 64, "lease_id": "b" * 32}
        (run / "envelope.json").write_text(json.dumps(binding))
        (run / "claim.json").write_text(json.dumps({"task_id": "TASK-1", "source_digest": "a" * 64, "lease_id": "b" * 32}))
        (run / "result.json").write_text(json.dumps({**binding, "source_digest": "a" * 64, "terminal_state": "execution_finished", "stdout_sha256": "c" * 64, "stderr_sha256": "d" * 64}))
        if outcome:
            (run / "task-outcome.json").write_text(json.dumps({**binding, "source_sha256": "a" * 64, "status": "completed"}))
        return temp, run

    def test_checkpoint_is_allowlisted_and_idempotent(self):
        temp, run = self.run_dir()
        try:
            first = recovery.recover(run)
            second = recovery.recover(run)
            self.assertEqual(first, second)
            self.assertEqual(first["decision"], "checkpoint_only")
            self.assertTrue((run / "execution-checkpoint.json").exists())
            self.assertFalse((run / "task-outcome.json").exists())
        finally:
            temp.cleanup()

    def test_existing_outcome_is_only_reporter_candidate(self):
        temp, run = self.run_dir(outcome=True)
        try:
            self.assertEqual(recovery.recover(run)["decision"], "reporter_reconcile_candidate")
        finally:
            temp.cleanup()

    def test_wrong_lease_cannot_recover(self):
        temp, run = self.run_dir()
        try:
            value = json.loads((run / "claim.json").read_text())
            value["lease_id"] = "e" * 32
            (run / "claim.json").write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "binding"):
                recovery.recover(run)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
