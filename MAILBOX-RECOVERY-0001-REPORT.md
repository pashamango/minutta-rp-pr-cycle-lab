# MAILBOX-RECOVERY-0001

## Implementation verdict

`RECOVERY_READY`: recovery now performs lease-preserving, idempotent execution-state bookkeeping. It validates the `(task_id, source_sha256, lease_id)` identity across envelope, claim, result, and outcome; writes an allowlisted checkpoint only for an un-settled `execution_finished` run; and leaves semantic settlement to the existing strict reporter.

## Regression observations

- Issue #75 / `PROJECT-GD2-FORK-0002`: existing bound outcome is valid but reports `blocked` because the trusted runtime selected the wrong model. Semantic status: `AUTH_REQUIRED` / trusted runtime correction required. No rerun or fabricated verdict.
- Issue #77 / `SOVEREIGN-WORKER-RUNWAY-0001`: existing bound outcome is valid, with committed artifacts and an evidence-backed `REDESIGN` verdict. Semantic status: `REDESIGN`; recovery marks it a reporter reconciliation candidate. No rerun.

## Safety evidence

Wrong-task, stale-lease, and unbound result bindings are rejected. A recovery ledger keyed by the binding identity makes restart/retry idempotent. Recovery cannot create `task-outcome.json`, post a receipt, merge, or push.

## Rollback

Remove the recovery tool and its tests/report from the branch; the existing dispatcher/reporter behavior is otherwise unchanged. Do not delete historical mailbox run state.
