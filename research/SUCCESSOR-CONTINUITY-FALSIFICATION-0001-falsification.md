# FALSIFICATION_RESULT/v1

- task_id: `SUCCESSOR-CONTINUITY-FALSIFICATION-0001`
- continuity_commit: `a6c8d1718de651e04bb2f5f39189cd3d73e2fe9b`
- test: `tests.test_successor_continuity_falsification.SuccessorContinuityFalsificationTests.test_caller_accessible_promotion_accepts_forged_validation_record`
- command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_successor_continuity_falsification`
- result: `1 passed`

The fixture acts as the executor and copies the inherited public reporter
authority, protocol, and reporter-module SHA constants. It supplies a
schema-valid record with attacker-chosen `task_id`, source and lease digests,
outcome digest, receipt key, timestamp, and `remote_state`, then recomputes
`payload_sha256` as an ordinary SHA-256 over that same attacker-controlled
JSON. The inherited consumer accepts the record and returns `settled` after
the caller-accessible promotion path reaches `REPORTER_VALIDATED`.

The first unsafe transition is acceptance of the self-hash as sufficient
validation in `CommanderStore.accept_validation_record`; no secret, HMAC,
signature, or certificate is required. This is a historical reproduction,
not a repair.
