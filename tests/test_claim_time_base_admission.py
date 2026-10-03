import unittest

from tools.claim_time_base_admission_harness import Admission, AdmissionError, admit


class ClaimTimeBaseAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.admission = Admission("TASK", "SOURCE", "LEASE", "B")

    def test_descendant_main_does_not_overwrite_claim_base(self):
        trace = []
        bound = admit(self.admission, task_id="TASK", source_sha256="SOURCE",
                      lease_id="LEASE", remote_main="M", known_heads={"B", "M"},
                      trace=trace)
        self.assertEqual(bound, "B")
        self.assertNotEqual("B", "M")
        self.assertIn("REMOTE_MAIN_DESCENDANT:M", trace)
        self.assertEqual(trace[-1], "ADMISSION:SUCCESS")

    def test_negative_controls(self):
        cases = [
            {"task_id": "OTHER"},
            {"lease_id": "OTHER"},
            {"task_ref": "UNKNOWN"},
            {"known_heads": {"M"}},
        ]
        for override in cases:
            args = {"task_id": "TASK", "source_sha256": "SOURCE", "lease_id": "LEASE",
                    "remote_main": "M", "known_heads": {"B", "M"}}
            args.update(override)
            with self.subTest(override=override), self.assertRaises(AdmissionError):
                admit(self.admission, **args)


if __name__ == "__main__":
    unittest.main()
