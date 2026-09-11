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
    @patch("router.urllib.request.urlopen")
    def test_local_disables_thinking_and_bounds_output(self, open_url):
        response = open_url.return_value.__enter__.return_value
        response.__enter__ = lambda: response
        response.__exit__ = lambda *args: None
        response.read = lambda: b'{"response":"ok","done_reason":"stop"}'
        import json
        class Context:
            def __enter__(self): return response
            def __exit__(self, *args): return None
        open_url.return_value = Context()
        from router import run_local
        run_local("private test")
        body=json.loads(open_url.call_args.args[0].data)
        self.assertFalse(body["think"])
        self.assertEqual(body["options"]["num_predict"], 64)
if __name__ == "__main__": unittest.main()
