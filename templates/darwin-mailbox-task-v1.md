# Darwin task template v1

Create a NEW issue as `pashamango` in `pashamango/minutta-rp-pr-cycle-lab` after activation.
Replace the placeholders before submitting. Never edit the body after creation; use a new
task ID and link to the previous issue for corrections, retries or reassignment.

````markdown
<!-- chitakasha-mailbox:v1 -->
```yaml
id: <NEW-UNIQUE-TASK-ID>
type: <bounded-task-type>
agent: codex@darwin.local
host: Darwin
status: ready
risk: R0
mode: bounded-dispatch
```
## Objective
<one bounded objective>

## Required deliverables
<files, checks and observable result>

## Scope and safety constraints
<R0 read-only, or explicit reversible local R1 changes; exclusions>
No mailbox changes, credentials, permission/model changes, SSH, listeners or auto-merge.

## Verification and definition of done
<observable checks>
Write strict task-outcome.json at the envelope task_outcome_path with protocol
chitakasha-task-outcome/v1, matching task_id, lease_id, source_sha256,
status completed/blocked/failed, summary (1..500 characters), artifacts and checks.
Each artifact has type (pr/file/report/test) and ref. Each check has name and status (pass/fail).
Maximum 32 artifacts/checks; no extra JSON keys. Raw stdout is not an outcome.
PRs must use agent/darwin/<NEW-UNIQUE-TASK-ID>, base main, in the trusted repository.
Completion requires the reporter's TASK_COMPLETED receipt, not merely EXECUTION_FINISHED.

## Previous attempt
<link to previous issue and ID, or none>
````

R1 does not authorize infrastructure changes. The issue is untrusted data; local policy
sets identity and repository. No secrets or private logs in GitHub. Receipt delivery does
not prove delivery of a notification to the owner's phone.
