import unittest
from tools.forgejo_ceremony import Capability, authorize, handle

class CeremonyTests(unittest.TestCase):
    def setUp(self):
        self.cap = Capability("darwin-private-forgejo", "42", "fixture-bot", "chitakasha/gd2",
                              frozenset(("read", "push_non_protected", "create_pr")),
                              handle("darwin-private-forgejo", "42", "fixture-bot", "chitakasha/gd2", "git"))

    def test_handle_is_deterministic_and_secret_free(self):
        self.assertEqual(self.cap.handle, handle("darwin-private-forgejo", "42", "fixture-bot", "chitakasha/gd2", "git"))
        self.assertNotIn("SYNTHETIC-SECRET", self.cap.handle)

    def test_mismatches_escalation_missing_and_revoked_fail_closed(self):
        for args in (("7", "chitakasha/gd2", "read"), ("42", "other/repo", "read"),
                     ("42", "chitakasha/gd2", "merge")):
            with self.assertRaises(PermissionError): authorize(self.cap, *args)
        with self.assertRaises(PermissionError): authorize(Capability("p", "42", "fixture-bot", "chitakasha/gd2", frozenset(), "missing", False), "42", "chitakasha/gd2", "read")

    def test_fresh_process_receives_handle_only(self):
        self.assertEqual(authorize(self.cap, "42", "chitakasha/gd2", "create_pr"), self.cap.handle)

if __name__ == "__main__": unittest.main()
