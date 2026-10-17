"""Unit tests for NICLI Dispatcher v0.1 shadow-admission CLI (MIN-74)."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from nicli_dispatcher import (
    DEFAULT_CLI_VERSION,
    DEFAULT_PINNED_MODEL,
    NICLI_SHADOW_ADMISSION_SCHEMA,
    DispatcherError,
    LinearIssueSnapshot,
    parse_candidates_json,
    run_shadow_admission,
)
from nicli_dispatcher.cli import main


class TestNicliCli(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = Path(__file__).resolve().parent.parent / "fixtures" / "shadow_admission_fixture.json"

    def test_version_command(self) -> None:
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            code = main(["version"])
        finally:
            sys.stdout = old_stdout

        self.assertEqual(code, 0)
        data = json.loads(buffer.getvalue())
        self.assertEqual(data["version"], DEFAULT_CLI_VERSION)
        self.assertEqual(data["pinned_model"], DEFAULT_PINNED_MODEL)
        self.assertEqual(data["schemas"]["shadow_admission"], NICLI_SHADOW_ADMISSION_SCHEMA)

    def test_parse_candidates_shapes(self) -> None:
        # 1. Array shape
        arr = [{"issue_id": "MIN-1", "uuid": "u1", "team_key": "MIN", "status": "Todo", "title": "T1", "description": "D1", "labels": [], "updated_at": "2026-10-16T00:00:00Z"}]
        snaps1 = parse_candidates_json(json.dumps(arr))
        self.assertEqual(len(snaps1), 1)
        self.assertEqual(snaps1[0].issue_id, "MIN-1")

        # 2. Single object shape
        single = {"issue_id": "MIN-2", "uuid": "u2", "team_key": "MIN", "status": "Todo", "title": "T2", "description": "D2", "labels": [], "updated_at": "2026-10-16T00:00:00Z"}
        snaps2 = parse_candidates_json(json.dumps(single))
        self.assertEqual(len(snaps2), 1)
        self.assertEqual(snaps2[0].issue_id, "MIN-2")

        # 3. Object with "candidates" key
        wrapper = {"candidates": [arr[0], single]}
        snaps3 = parse_candidates_json(json.dumps(wrapper))
        self.assertEqual(len(snaps3), 2)

    def test_fixture_shadow_admission_verdicts(self) -> None:
        content = self.fixture_path.read_text(encoding="utf-8")
        candidates = parse_candidates_json(content)
        result = run_shadow_admission(
            candidates,
            now="2026-10-16T23:30:00Z",
            pinned_model=DEFAULT_PINNED_MODEL,
            cli_version=DEFAULT_CLI_VERSION,
        )

        self.assertEqual(result["schema"], NICLI_SHADOW_ADMISSION_SCHEMA)
        self.assertEqual(result["pinned_model"], "Gemini 3.8 Flash Medium")
        self.assertEqual(result["cli_version"], "0.1.0")
        self.assertEqual(result["summary"]["total_evaluated"], 6)
        self.assertEqual(result["summary"]["admitted_count"], 1)
        self.assertEqual(result["summary"]["rejected_count"], 5)
        self.assertEqual(result["summary"]["model_calls"], 0)

        decisions_by_id = {d["issue_id"]: d for d in result["decisions"]}

        # MIN-68 must be admitted
        self.assertTrue(decisions_by_id["MIN-68"]["admitted"])
        self.assertIsNone(decisions_by_id["MIN-68"]["blocker_code"])
        self.assertTrue(len(decisions_by_id["MIN-68"]["task_revision_hash"]) == 64)

        # Rejections must have exact expected codes
        self.assertFalse(decisions_by_id["MIN-69"]["admitted"])
        self.assertEqual(decisions_by_id["MIN-69"]["blocker_code"], "UNMET_DEPENDENCY")

        self.assertFalse(decisions_by_id["MIN-70"]["admitted"])
        self.assertEqual(decisions_by_id["MIN-70"]["blocker_code"], "MISSING_REPOSITORY_OR_ACCEPTANCE")

        self.assertFalse(decisions_by_id["MIN-71"]["admitted"])
        self.assertEqual(decisions_by_id["MIN-71"]["blocker_code"], "VETO_OR_HOLD")

        self.assertFalse(decisions_by_id["MIN-72"]["admitted"])
        self.assertEqual(decisions_by_id["MIN-72"]["blocker_code"], "CONFLICTING_ROLE_STATE")

        self.assertFalse(decisions_by_id["MIN-73"]["admitted"])
        self.assertEqual(decisions_by_id["MIN-73"]["blocker_code"], "NOT_TODO_STATUS")

    def test_auth_and_quota_validation(self) -> None:
        candidates = parse_candidates_json(self.fixture_path.read_text(encoding="utf-8"))

        with self.assertRaises(DispatcherError) as ctx_auth:
            run_shadow_admission(candidates, auth_mode="unsupported_auth")
        self.assertEqual(ctx_auth.exception.code, "UNSUPPORTED_AUTH_MODE")

        with self.assertRaises(DispatcherError) as ctx_bucket:
            run_shadow_admission(candidates, auth_mode="api_key", quota_bucket="wrong-bucket")
        self.assertEqual(ctx_bucket.exception.code, "QUOTA_BUCKET_MISMATCH")

    def test_cli_execution_determinism(self) -> None:
        buf1 = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buf1
            code1 = main(["shadow-admit", "--input", str(self.fixture_path), "--now", "2026-10-16T23:30:00Z"])
        finally:
            sys.stdout = old_stdout
        self.assertEqual(code1, 0)

        buf2 = io.StringIO()
        try:
            sys.stdout = buf2
            code2 = main(["shadow-admit", "--input", str(self.fixture_path), "--now", "2026-10-16T23:30:00Z"])
        finally:
            sys.stdout = old_stdout
        self.assertEqual(code2, 0)

        # Output must be bit-for-bit deterministic
        out1 = buf1.getvalue()
        out2 = buf2.getvalue()
        self.assertEqual(out1, out2)
        h1 = hashlib.sha256(out1.encode("utf-8")).hexdigest()
        h2 = hashlib.sha256(out2.encode("utf-8")).hexdigest()
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
