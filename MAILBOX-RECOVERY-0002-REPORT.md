# MAILBOX-RECOVERY-0002

## Recovery verdict

`RECOVERY_READY`. The exact #79 execution is recoverable and already contains a
reviewable implementation at commit `9b2a00d4c7324f8222f43e9f1ebd7e79bff05dc0`.
This successor preserves that implementation and records the bounded regression
analysis below. It does not rerun #79, #75, or #77.

## Exact #79 evidence

- task: `MAILBOX-RECOVERY-0001`
- source SHA-256: `266b540e483cc1c888ae6910d83a5e4868b1cfd1988c1cb6615da507c919d28e`
- lease: `02a9739adf1645318e07582f6431d343`
- execution exit: `0`; terminal state: `execution_finished`
- stdout SHA-256: `67051d67ce18bb917458d15a96f0b79f26e51ac0bbd3eb92a77f067fde02ee7c`
- stderr SHA-256: `26d005e587066e93a97b68b643ccc53b154c2c50a3edbd53e9dcf7f3b7e579f3`
- result SHA-256: `bac203b0f41dd4670ca4ab89cb448003af4384ed0b9626113f62fdc352fb5d63`
- prior branch/commit: `agent/wolfram/MAILBOX-RECOVERY-0001` /
  `9b2a00d4c7324f8222f43e9f1ebd7e79bff05dc0`
- prior checks: 30/30; no push, merge, deployment, credential access, or
  fabricated settlement.

The prior task outcome is bound and says `RECOVERY_READY`; its implementation
validates `(task_id, source_sha256, lease_id)`, writes only an allowlisted
checkpoint for an unsettled execution, and leaves semantic settlement to the
strict reporter.

## Historical semantic states

### #75 — `AUTH_REQUIRED`

Bound task `PROJECT-GD2-FORK-0002`, lease
`1864fd074fab423bb4e2c7aa5763c6fc`, source
`f3e732ce662a668f83844c071b50abca6cd1dcfb554f68092135cd541e5ae425`.
The recorded result exited 0, but the bound outcome is `blocked`: the trusted
runtime exposed `gpt-6-astra` at low effort while the task required GPT-5.6
Luna. No research started and no implementation artifact exists. Therefore
neither `BUILD_NEXT` nor `REDESIGN` is semantically supported. The exact next
bounded action is a trusted runtime correction selecting GPT-5.6 Luna, followed
by a newly admitted run; this report does not authorize that run.

### #77 — `REDESIGN` (reporter reconciliation candidate)

Original lease recovered exactly as `c2cc319b543544f2a9fca6b68ac2cb71`, task
`SOVEREIGN-WORKER-RUNWAY-0001`, source
`3b37fecc10b003ef4941b77a87aa6288faace9f14d958b9c4a474333f63731c7`.
Its bound result records router policy tests 3/3 and loopback Ollama
reachability, but private Gemma inference timed out after 60 seconds. External
Gemini remained unverified and required explicit `AUTH_REQUEST`; no credential
was accessed. Existing evidence supports `REDESIGN`, not `BUILD_NEXT` and not
a genuine `AUTH_REQUEST`: the smallest next work is to redesign/diagnose the
local inference timeout under a separately admitted task, while any Gemini
credential request remains separately gated. No #77 rerun occurred.

## Adversarial and authority evidence

The carried tests pass for idempotent recovery, an existing outcome being only
a reporter-reconciliation candidate, and a wrong lease being rejected. The
implementation also rejects mismatched task/source/result/outcome bindings and
does not create an outcome, receipt, push, merge, or semantic completion. A
stale, wrong-task, or unbound result therefore cannot settle. The recovery
ledger is keyed by the three-part binding and preserves the postcondition that
semantic settlement is unchanged.

## Rollback and smallest next action

Rollback is to close this review branch/PR and remove only the successor report;
leave historical mailbox run state and the #79 branch untouched. No installed
policy or capability files need rollback. The smallest next action is for the
existing strict reporter to reconcile this bound recovery candidate and, if
accepted, review the branch/PR below; no merge is requested.

## Review publication

- branch: `agent/wolfram/MAILBOX-RECOVERY-0002`
- base: `main`
- commit: recorded in the successor task outcome after validation
- PR: recorded in the successor task outcome after publication
