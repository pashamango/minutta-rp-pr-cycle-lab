# MIN-76 NICLI-D: bounded Darwin soak and gated expansion

This runbook extends the MIN-74 dispatcher without changing its safety gates. It
is an execution contract, not evidence that a 24-hour pilot has completed.

## Preconditions

The operator must record all of the following before enabling a worker:

* exact repository, branch, and source commit;
* exact host identity, OS/architecture, owner, and credential scope;
* resolved DISPLAY identifier (`DISPLAY-07` or `DISPLAY-007`) from the current
  source ticket; guessed hostnames are invalid;
* a fresh resource snapshot showing disk, memory pressure, CPU, and existing
  worker count; `max_wip=1` remains mandatory;
* launch mechanism selected from inspected host state (`launchd`, `systemd`,
  or Windows runner), with a reversible kill switch and bounded log paths.

Unknown quota, unknown host identity, unavailable credentials, or a missing
capacity snapshot is a fail-closed blocker. Device count must never multiply a
global quota or WIP budget.

## Receipt separation

Each sample is append-only JSONL and contains `raw_evidence_ref` and
`model_inference_ref` as separate fields. Raw evidence is immutable and must
not contain credentials, prompts, cookies, or unredacted household logs.
Model/Muse review is event-driven or sampled; no perpetual model polling is
permitted.

Required counters are: queue wait, attempted, accepted, rework, failed,
false-DONE, API usage when observable, quota status/unknowns,
requested/observed model, host peaks, duplicate attempts, essential-service
regression, and accepted throughput.

## 24-hour gate

The soak is `PENDING` until a real 24-hour interval has elapsed. A valid
receipt must show start/end timestamps, all samples, kill-switch state,
restart/backoff events, retention behavior, and a rollback demonstration. A
synthetic timestamp or a test run is not a soak result.

Expansion is enabled per host only after that host's canary and resource limits
pass. Offline or incompatible hosts remain `BLOCKED` and do not hold unrelated
projects.

## Current MIN-76 preflight result

`BLOCKED / PENDING`: this checkout contains no authoritative DISPLAY-07 vs
DISPLAY-007 host/OS/owner/capacity resolution and no 24-hour receipt. No
launchd job was loaded, no credentials were changed, and no Darwin or Tailnet
configuration was modified.
