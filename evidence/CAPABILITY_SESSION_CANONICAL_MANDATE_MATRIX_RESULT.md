# CAPABILITY_SESSION_CANONICAL_MANDATE_MATRIX_RESULT/v1

task_id: CAPABILITY-SESSION-CANONICAL-MANDATE-MATRIX-0001
source_issue: 238
source_sha256: 1aafd985a9f9ef1b4668d3a3c4123c2be4016c7b198a543949aa503fa0f7a821
lease_id: fbb834c769e04f76a2c71d8bc19abbb3
existing_pr: 237
independent_review_id: 5195372257
branch: agent/wolfram/CAPABILITY-SESSION-CANONICAL-MANDATE-0001

## Continuity

- inherited head: c354478deef4aa1da243bea795b0459fd5638305
- SUCCESSOR_CONTINUITY commit: d7f9f15e47d519a06f865e7fecdd634cf042a46d

## Test and implementation commit

- commit: 03c894773fc4401126a95f1fb382c65b93b0f608
- implementation repair: bind mandate `device_id` to the current machine identity and
  `policy_digest` to the current policy digest during authorization.
- tests: each MandatePayload field is mutated and the original ApprovalProof is reused;
  request task/source/lease/class mismatches and forged lookalikes are rejected;
  device/policy/epoch/expiry, drift and reauthorization, old observation, and unchanged
  sleep/wake plus Python/venv replacement non-triggers are covered.
- focused command: `python3 -m unittest tests.test_capability_session -v`
- focused result: 6 tests, 6 passed, 0 failed.
- repository command: `python3 -m unittest discover -s tests -p 'test*.py' -v`
- repository result: 123 tests, 123 passed, 0 failed, 24.546s.
- `python3 -m unittest discover -v` was not the repository suite and ran 0 tests;
  the explicit `tests` discovery command is the deterministic suite used above.

## Bounded verdict

SYNTHETIC_CANONICAL_MANDATE_READY / CRYPTOGRAPHIC_AND_PRODUCTION_CUSTODY_ABSENT

No real cryptography, WebAuthn/passkey, key custody, protected-resource access,
network, runtime activation, dispatcher/reporter/Commander change, secret, merge, or
main push was performed. No new authority bypass was exposed; no BUTTERFLY record is
required.
