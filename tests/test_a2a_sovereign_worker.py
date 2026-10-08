import importlib.util
import sys
import unittest
from pathlib import Path


path = Path(__file__).parents[1] / "research/A2A-SOVEREIGN-WORKER-0001/probe.py"
spec = importlib.util.spec_from_file_location("a2a_probe", path)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


class SovereignWorkerTests(unittest.TestCase):
    def test_vertical_slice_boundaries_and_lifecycle(self):
        result = probe.run()
        self.assertEqual(result["first"]["state"], "completed")
        self.assertEqual(result["first"], result["duplicate"])
        self.assertEqual(result["first"]["evidence_sha256"], probe.digest({"task_id": "synthetic-001", "artifact": {"echo": "public fixture"}}))
        self.assertEqual(result["denied"]["state"], "denied")
        self.assertEqual(result["denied_primitive"]["state"], "denied")
        self.assertEqual(result["cancelled"], result["after_cancel"])
        self.assertFalse(result["private_fixture_exposed"])


    def test_capability_card_contains_only_allocatable_metadata(self):
        card = probe.Worker().capability_card()
        self.assertEqual(set(card), {"protocol", "task_classes", "privacy_class", "runtime_class", "budget"})
        serialized = str(card)
        for forbidden in ("credential", "filename", "history", "sentinel", "host_state"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
