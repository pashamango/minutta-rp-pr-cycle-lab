import unittest
from sovereign_worker.capability_session import *


class CapabilitySessionTests(unittest.TestCase):
    def setUp(self):
        self.state = SyntheticState("b1", "bin1", "pol1", "m1", "t1")
        self.approval = Approval("n1", "task", "lease", 1)
        self.lease = TaskLease("task", "src", "lease", "read", 1, 100)
        self.s = CapabilitySession(self.state, FakeApprovalVerifier([
            ("n1", "task", "lease", 1)]))

    def test_positive_and_exact_scope(self):
        self.assertTrue(self.s.authorize(self.approval, self.lease, 1))
        self.assertTrue(self.s.execute(self.lease, task_id="task", source_sha256="src", lease_id="lease", capability_class="read", now=2))
        self.assertFalse(self.s.execute(self.lease, task_id="other", source_sha256="src", lease_id="lease", capability_class="read", now=2))

    def test_invalidations_fail_closed(self):
        for field in ("boot_id", "capabilityd_digest", "policy_digest", "machine_identity", "tailnet_identity"):
            changed = {"b1": "b2", "bin1": "bin2", "pol1": "pol2", "m1": "m2", "t1": "t2"}[getattr(self.state, field)]
            values = self.state.__dict__ | {field: changed}
            s = CapabilitySession(self.state, FakeApprovalVerifier([])); s.observe(SyntheticState(**values))
            self.assertEqual(s.state_name, SessionState.REAUTH_REQUIRED)
            self.assertFalse(s.authorize(self.approval, self.lease, 1))

    def test_expiry_revocation_scope_nonce_and_replay(self):
        self.assertFalse(self.s.authorize(self.approval, self.lease, 100))
        self.assertFalse(self.s.authorize(self.approval, TaskLease("task", "src", "lease", "write", 1, 100), 1))
        self.assertFalse(self.s.authorize(Approval("bad", "task", "lease", 1), self.lease, 1))
        self.assertTrue(self.s.authorize(self.approval, self.lease, 1))
        self.assertFalse(self.s.authorize(self.approval, self.lease, 1))
        self.s.revoke(); self.assertFalse(self.s.execute(self.lease, task_id="task", source_sha256="src", lease_id="lease", capability_class="read", now=2))

    def test_sleep_wake_and_python_replacement_do_not_change_bound_state(self):
        self.s.observe(self.state); self.assertEqual(self.s.state_name, SessionState.ACTIVE)


if __name__ == "__main__": unittest.main()
