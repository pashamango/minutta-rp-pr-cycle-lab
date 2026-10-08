import tempfile, unittest
from pathlib import Path
from sovereign_worker.runner import Runner, Capability
class FakeLocal:
    def capability(self): return Capability("fake-local","private",False,"test",None,"configured")
    def infer(self, prompt): return "useful visible output: "+prompt, {"provider":"fake-local","model":"test","latency_ms":1,"usage":{}}
class NoAuth:
    def capability(self): return Capability("gemini","public",True,"external-free",None,"auth_required")
    def infer(self, prompt): raise PermissionError("AUTH_REQUIRED")
class RunnerTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.db=Path(self.tmp.name)/"runner.sqlite3"
    def tearDown(self): self.tmp.cleanup()
    def test_local_duplicate_and_restart(self):
        r=Runner(self.db,local=FakeLocal(),external=NoAuth()); r.submit("x","summarize fixture","private"); first=r.process("x"); self.assertEqual(first,r.process("x")); self.assertEqual(Runner(self.db,local=FakeLocal(),external=NoAuth()).process("x"),first); self.assertIn("useful",first["result"])
    def test_external_auth_required_and_private_not_external(self):
        r=Runner(self.db,local=FakeLocal(),external=NoAuth()); r.submit("p","public fixture","public"); self.assertEqual(r.process("p")["state"],"auth_required")
        with self.assertRaises(ValueError): r.submit("s","contains secret material","public")
    def test_billing_guard(self):
        with self.assertRaises(PermissionError): Runner(self.db,local=FakeLocal(),paid=True)
if __name__ == "__main__": unittest.main()
