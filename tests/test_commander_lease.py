import tempfile
import unittest
from pathlib import Path

from continuation.role_lease import CommanderLease, CommanderStore, LeaseError


class CommanderLeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = CommanderStore(Path(self.tmp.name) / "checkpoint.json")
        self.role = CommanderLease("codex@wolfram.local", "scope", "mandate", "2026-09-12T15:00:00Z", "2026-09-12T16:00:00Z", 2)
        self.store.create_role(self.role)

    def tearDown(self):
        self.tmp.cleanup()

    def test_resume_across_process_and_expiry_stops_child(self):
        self.store.start_child("A", "a" * 64, "1" * 32, self.role.principal, self.role.scope, self.role.mandate_digest, "2026-09-12T15:01:00Z")
        self.store.settle_child("A", "a" * 64, "1" * 32)
        resumed = CommanderStore(self.store.path)
        resumed.resume(self.role.principal, self.role.scope, self.role.mandate_digest, "2026-09-12T15:30:00Z")
        resumed.start_child("B", "b" * 64, "2" * 32, self.role.principal, self.role.scope, self.role.mandate_digest, "2026-09-12T15:30:00Z")
        resumed.revoke()
        with self.assertRaises(LeaseError):
            resumed.start_child("C", "c" * 64, "3" * 32, self.role.principal, self.role.scope, self.role.mandate_digest, "2026-09-12T15:31:00Z")
        self.assertEqual(resumed.resumable_children(), ["B"])
        with self.assertRaises(LeaseError):
            resumed.start_child("A", "a" * 64, "4" * 32, self.role.principal, self.role.scope, self.role.mandate_digest, "2026-09-12T15:31:00Z")

    def test_binding_deadline_and_revocation_fail_closed(self):
        cases = [("other", "scope", "mandate", "2026-09-12T15:10:00Z"), ("codex@wolfram.local", "wrong", "mandate", "2026-09-12T15:10:00Z"), ("codex@wolfram.local", "scope", "wrong", "2026-09-12T15:10:00Z"), ("codex@wolfram.local", "scope", "mandate", "2026-09-12T16:00:00Z")]
        for args in cases:
            with self.assertRaises(LeaseError):
                self.store.resume(*args)
        self.store.revoke()
        with self.assertRaises(LeaseError):
            self.store.resume("codex@wolfram.local", "scope", "mandate", "2026-09-12T15:10:00Z")


if __name__ == "__main__":
    unittest.main()
