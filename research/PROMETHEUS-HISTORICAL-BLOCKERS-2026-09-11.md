# Historical BLOCKED audit — 2026-09-11

Prometheus diagnoses were posted to Issues #73, #75, #82, #83, #84, and #114. The audit separates genuine execution constraints from handoff defects.

| Issue | first stuck transition | class | safe repair |
|---|---|---|---|
| #114 | exit 0 -> artifact/outcome publication | dependency | recover exact workspace evidence and publish it; do not infer success |
| #75 | runtime preflight -> admitted execution | authority | use the required Luna runtime; do not broaden model policy |
| #73 | capability preflight -> listener-dependent execution | capability | redesign as listener-free simulation or obtain explicit authority |
| #82 | outcome validation -> terminal settlement | representation | replay the strict reporter against bound evidence |
| #83 | reporter outcome -> durable publication | representation | publish exact bound artifacts before settlement |
| #84 | extraction -> reviewable Git publication | dependency | recover by exact task/source/lease binding, without rerun |

## Repair decision

The apparent “narrow constraint” is not uniformly a bug. #73 and #75 are correctly fail-closed security/authority gates; broadening them would violate the task contract. The reproducible repair target is the continuation handoff: `EXECUTION_FINISHED` must leave a durable, replayable reporter continuation, while semantic settlement remains owned by the strict reporter.

The current dispatcher already invokes `TASK_OUTCOME` when the bound outcome exists, and the Darwin reconciler replays bound runs without invoking Codex again. The historical failures therefore remain evidence of missing/ inaccessible bound artifacts or an unavailable continuation trigger, not evidence that reporter validation should be weakened. The new `prometheus/` adapter and tests make this distinction machine-checkable: process end is not semantic completion, and `continuation_only` is the safe retry classification.

## Result

`PARTIAL_REPAIR`

Six issue-level diagnoses are durable. No historical task was rerun, no blocked security boundary was broadened, and no completion was fabricated. The next implementation step is a repository-controlled durable continuation queue/receipt for the Darwin↔Wolfram handoff, with exact `(task_id, source_digest, lease_id)` binding and idempotent reporter replay.
