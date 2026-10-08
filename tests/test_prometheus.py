import unittest

from prometheus.blocker_analysis import auth_required


class PrometheusTests(unittest.TestCase):
    def test_process_end_is_not_semantic_completion(self):
        result = auth_required(task_id="FRIDAY-E2E-2026-09-11", source_digest="sha256:fixture", lease_id="P-1")
        self.assertEqual(result["type"], "BLOCKER_ANALYSIS/v1")
        self.assertEqual(result["semantic_work_status"], "partial")
        self.assertEqual(result["blocker_class"], "authority")
        self.assertTrue(result["requires_pasha"])
        self.assertNotEqual(result["semantic_work_status"], "complete")


if __name__ == "__main__":
    unittest.main()
