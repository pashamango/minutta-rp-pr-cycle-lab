import tempfile, unittest
from pathlib import Path
from sovereign_worker.runner import Runner, Capability, StubExternal, NoAuthExternal, GeminiExternal

class Local:
    def capability(self): return Capability("fake-local", "private", True, "test", "configured")
    def infer(self, prompt): return "bounded answer: " + prompt, {"provider":"fake-local","model":"test","latency_ms":1,"usage":{},"retries":0}

class RunnerTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.db=Path(self.tmp.name)/"jobs.sqlite3"
    def tearDown(self): self.tmp.cleanup()
    def test_local_restart_idempotency_and_receipt(self):
        r=Runner(self.db, Local(), NoAuthExternal()); r.submit("j1","summarize fixture","private")
        first=r.process("j1"); self.assertEqual(first, r.process("j1")); self.assertEqual(first, Runner(self.db,Local(),NoAuthExternal()).process("j1")); self.assertTrue(first["receipt"]["artifact_sha256"])
    def test_public_no_auth_stays_queued_and_stub_works(self):
        r=Runner(self.db, Local(), NoAuthExternal()); r.submit("j2","public synthetic fixture","public"); self.assertEqual(r.process("j2")["state"],"queued")
        s=Runner(self.db, Local(), StubExternal()); self.assertEqual(s.process("j2")["state"],"completed")
    def test_private_never_external_and_billing_closed(self):
        r=Runner(self.db, Local(), StubExternal()); r.submit("j3","contains secret material","private"); self.assertEqual(r.process("j3")["receipt"]["route"],"private")
        with self.assertRaises(ValueError): r.submit("j4","contains secret material","public")
        with self.assertRaises(PermissionError): Runner(self.db, Local(), paid=True)
    def test_capability_card_is_sanitized(self):
        card=Runner(self.db, Local(), NoAuthExternal()).capability_card(); self.assertEqual(card["protocol"],"worker-capability-card/v1"); self.assertNotIn("prompt",str(card)); self.assertEqual(card["credentials"],"not_exposed")

    def test_gemini_without_key_is_auth_required(self):
        g=GeminiExternal(api_key=None)
        self.assertEqual(g.capability().availability, "auth_required")
        with self.assertRaisesRegex(PermissionError, "AUTH_REQUIRED"): g.infer("public synthetic probe")

    def test_default_runner_uses_fail_closed_gemini_lane(self):
        r=Runner(self.db, Local()); r.submit("j5", "public synthetic fixture", "public")
        self.assertEqual(r.process("j5")["state"], "queued")
