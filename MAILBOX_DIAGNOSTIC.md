# WOLFRAM-MAILBOX-RECOVERY-0001 diagnostic

Date: 2026-11-12 (America/Los_Angeles)  
Scope: read-only diagnosis; no task admission, claim, dispatch, restart, credential change, or Darwin/Forgejo change.

## Verdict

`SRG-0001` / GitHub Issue #512 was not admitted locally and has no local CLAIM or run. The exact failure is that the Wolfram LaunchAgent is not loaded and its recorded mailbox activity stopped before Issue #512 existed. This is a service-lifecycle outage, not an Issue authorization failure.

The issue was created at `2026-11-12T06:54:34Z`; direct `gh issue view` returned `OPEN`, author `pashamango`, the canonical marker, `agent: codex@wolfram.local`, `status: ready`, `risk: R1`, and `host: Wolfram`. Running the installed validator against that exact fetched object in a temporary directory returned `(metadata, None)` and isolated admission returned `accepted` with digest `05e12d281ca3f0cae48f83306c4fe5cd1cea36fc9e669d0cd8ff51a17af5352f`.

## Evidence by gate

| Gate | Evidence | Result |
|---|---|---|
| LaunchAgent configured | `~/ChitAkasha-Wolfram/agent-mailbox/config/mailbox-0001.plist`; label `com.chitakasha.agent-mailbox`; `RunAtLoad=true`, `StartInterval=60` | PRESENT |
| LaunchAgent loaded | `launchctl print gui/501/com.chitakasha.agent-mailbox` -> `Could not find service` | FAIL |
| Recent polling | `logs/launchd.stdout.log` mtime `2026-10-19 12:00:31`; final lines are old watcher/dispatcher counts | STALE |
| Watcher poll path | Installed watcher uses `gh issue list --state open --limit 100` and outbound HTTPS only | CODE PRESENT |
| Issue #512 admission | No inbox filename or JSON contains issue 512/SRG-0001; isolated validator/admission passes | NOT RUN / NOT ADMITTED |
| Dispatcher activation | `state/control/dispatcher-activation.json` exists, activated `2026-09-03T19:04:40.876357Z` | ENABLED IN STATE |
| Claims/runs | No `claims/SRG-0001.json`, no `runs/SRG-0001/` | NONE |
| Codex availability | `/Users/pavelcherkashin/.local/bin/codex`, `codex-cli 0.153.4`; historical daemon ledger has successful exits | NOT THE BLOCKER |
| Resource signal | Host up 23 days; load 2.99/2.68/2.62; `vm_stat` queried without destructive action | NO PROVEN LIMIT |
| Failure state | `state.failure.json`: `ValueError`, state path `/Users/pavelcherkashin/ChitAkasha-Wolfram/agent-mailbox/state` | HISTORICAL / NEEDS CORRELATION |

The log counts (`accepted: 0`, `rejected: 100`, repeated dispatcher counts) prove historical cycles processed only the first 100 open Issues returned by the CLI. They do not prove a current poll of #512, because the service is not currently loaded and the log is stale. The issue is presently within the first 100 open Issues, but no admission was performed by this task to avoid changing authoritative local state.

## Dispatcher conclusion

The dispatcher is installed and its activation watermark exists. Its code fail-closes when activation is absent, creates an exclusive claim before execution, and does not retry failed or timed-out claims. Because #512 has no inbox record, the dispatcher had no eligible input. Authentication/CLI invocation and local limits are therefore not reached for this task.

## Minimum repair recommendation

The minimum confirmed repair is service recovery: restore/load the reviewed LaunchAgent using the existing installation procedure, then observe one normal watcher cycle and verify admission/claim/receipt gates. This requires an explicit operational change and may create the first claim for SRG-0001; it was not performed here. Do not manually copy the issue into the inbox, create a claim, invoke `--record`, or restart/re-dispatch a task as a diagnostic shortcut.

Before repair, preserve and review the current dirty repository and mailbox state. After repair, use a fresh task-specific verification only if the operator authorizes it; do not retry any existing failed or timed-out claim.

## Remaining blockers

1. LaunchAgent is absent from the user launchd domain; no current poll can be attributed to it.
2. `state.failure.json` is historical and its `ValueError` lacks a timestamp/stack trace; it is evidence of a prior failure, not sufficient to identify that prior call site.
3. No Forgejo/Darwin authenticated architecture source was available in this checkout; the migration document below is explicitly split into verified local capabilities and proposed design.
4. No repair was applied, so Issue #512 remains unadmitted and undispatched.

