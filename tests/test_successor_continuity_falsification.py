import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from continuation.role_lease import CommanderLease, CommanderStore


class SuccessorContinuityFalsificationTests(unittest.TestCase):
    """Historical reproduction: public metadata plus an unkeyed self-hash is accepted."""

    def test_caller_accessible_promotion_accepts_forged_validation_record(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            record_path = Path(directory) / "forged-validation-record.json"
            store = CommanderStore(state_path, "role-1")
            role = CommanderLease(
                "codex@wolfram.local", "scope", "mandate",
                "2026-09-12T15:00:00Z", "2026-09-12T16:00:00Z", 1,
            )
            store.create_role(role)
            args = (role.principal, role.scope, role.mandate_digest,
                    "2026-09-12T15:10:00Z")
            task_id = "FORGED-CONTINUATION"
            source_sha256 = "a" * 64
            lease_id = "1" * 32
            store.start_child(task_id, source_sha256, lease_id, *args)
            for state in ("EXECUTION_CHECKPOINT", "OUTCOME_CANDIDATE",
                          "REPORTER_VALIDATED"):
                store.advance(task_id, state, *args)

            # These are public trust-root constants copied from the inherited
            # reporter/consumer. No key, signature, or secret is involved.
            protocol = "chitakasha-reporter-validation/v1"
            reporter_authority = "wolfram-agent-reporter"
            reporter_sha256 = (
                "8723f408947bf50962b1b451f44f7d1e33516c9fa6e8adffce76556b1ef0c9ed"
            )
            record = {
                "protocol": protocol,
                "reporter_authority": reporter_authority,
                "reporter_protocol": protocol,
                "reporter_sha256": reporter_sha256,
                "task_id": task_id,
                "source_sha256": source_sha256,
                "lease_id": lease_id,
                "issue_number": 199,
                "outcome_status": "completed",
                "outcome_sha256": "b" * 64,
                "terminal_receipt_state": "TASK_COMPLETED",
                "receipt_key": "sha256:" + "c" * 64,
                "evidence_validation": [],
                "validation_timestamp": "2026-09-12T15:10:00Z",
                "validation_timestamp_source": "result.finished_at",
                "remote_state": "posted",
            }
            # The current consumer calls this payload_sha256, but it is only
            # an unkeyed hash of attacker-controlled JSON.
            record["payload_sha256"] = hashlib.sha256(
                json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            record_path.write_text(json.dumps(record), encoding="utf-8")

            self.assertEqual(
                store.accept_validation_record(record_path, *args, source_issue=199),
                "settled",
            )


if __name__ == "__main__":
    unittest.main()
