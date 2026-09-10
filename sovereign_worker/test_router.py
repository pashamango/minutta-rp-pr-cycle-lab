import unittest
from unittest.mock import patch
from router import classify, route
class RouterTests(unittest.TestCase):
    def test_private_is_local(self): self.assertEqual(classify("summarize private correspondence").lane, "local-private")
    def test_public_is_external_without_secret(self):
        result=route("compare two public repository licenses"); self.assertEqual(result["status"], "AUTH_REQUEST_REQUIRED"); self.assertNotIn("key", str(result).casefold())
    @patch("router.run_local", return_value={"lane":"local-private","model":"test","response":"ok"})
    def test_private_route_calls_local(self, run_local):
        result=route("analyze a private design note"); run_local.assert_called_once(); self.assertEqual(result["lane"], "local-private")
if __name__ == "__main__": unittest.main()
