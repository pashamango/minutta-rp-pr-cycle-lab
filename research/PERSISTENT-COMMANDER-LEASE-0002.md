# PERSISTENT-COMMANDER-LEASE-0002

Verdict: `PARTIAL_MODEL`

This branch continues from predecessor head `3391439eaa03e4cf54ec314d11ac2f3bc67e095a` and implements a local, crash-conscious continuation model. Child records reserve explicit abstract budget units at admission and move monotonically through `CLAIMED -> EXECUTION_CHECKPOINT -> OUTCOME_CANDIDATE -> REPORTER_VALIDATED -> SETTLED`. Settlement requires a structured checkpoint bound to task, source, child lease, commander role lease, outcome digest, and reporter authority/version. Bare settlement, conflicting replay, corrupt state, expired/revoked roles, wrong bindings, and over-budget admission fail closed.

The remaining gap is material: this branch's deterministic unit test exercises the checkpoint contract with a constructed checkpoint, but does not yet run `tools/wolfram-agent-reporter` through its real source/admission/outcome/evidence validation path and feed that result into Commander. Therefore this is not `PERSISTENT_COMMANDER_INTEGRATION_READY`.

Command: `python3 -m unittest discover -s tests -v`

Observed result: 31 tests passed, 0 failed, 0 errors.

Rollback is deleting/reverting this review branch; no production scheduler/runtime, external service, active role lease, or expired mandate was changed. This is persistence of continuation state, not a renewed commander mandate.

Wise Broker observation: the persisted `RoleLease` fields are a minimal dormant-state substrate for a future `STATE_POSITION/v1` record (principal, scope, mandate digest, deadline, revocation), but this task adds no org-chart scope and does not implement #159.
