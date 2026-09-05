# DARWIN-CORE-0001-RETRY-01 — BLOCKED preflight

Darwin baseline is **not complete**. Both documented SSH routes timed out before any target command executed. No Darwin operational measurements were obtained. Overall task outcome: **blocked**.

Executor: **Wolfram.local**, macOS 26.6.2 (25G83), arm64. Inspection target: **Darwin, unverified**. CLI: `codex-cli 0.153.4`. Non-secret installed run header: model **gpt-6-astra**, provider **openai**, reasoning effort **low** (not the owner-reported interactive Max). Only allowlisted header fields from this lease were read; no configuration or authentication changes. The owner-reported application warning was not investigated and no app was launched.

Source: https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/48 . Parent issue #47, previous claims and artifacts are preserved.

## Time and provenance

Dispatch claim: 2026-09-05T20:55:07.401461+00:00. Target preflight ended: 2026-09-05T20:56:48.375496+00:00 (about 101 seconds after claim, within three minutes). Evidence finalized: 2026-09-05T20:59:35.861886+00:00; elapsed since claim: 268.460 seconds. Exact process end/elapsed belongs to the installed reporter after exit. Per-check elapsed is unmeasured unless shown below; no invented timings.

Policy: installed `agent-mailbox/config/policy.yaml` and merged `CHATGPT-MAILBOX-RUNBOOK.md` at origin/main `65a40e06a340b64b1ce060265a79ce1ba50fcb77`. No applicable AGENTS.md was found in checked ancestor paths or tracked repository files. The older local main runbook was stale; the fetched merged version was read and governs this report.

Route authority and host mapping were re-read from `Documents/Home Network with Name Service/runbooks/darwin-macbookpro3-recovery.md` and `inventory/darwin-macbookpro3-2026-06-16.md`. They document `macbook3` and the `macbook3-lan` fallback. The historical MacBookPro13,2 / Monterey 12.7.6 identity remains intended/previously recorded, not observed in this run.

SSH used batch authentication, strict existing host-key checking, one connection attempt, a 10-second connect timeout and a 20-second outer limit. Tailnet attempt began 20:56:08.315337 UTC; LAN attempt began 20:56:38.282496 UTC. Both exited 255 with “Operation timed out”. No authentication/permission bypass, network scan or alternate route was attempted.

## Coverage

| Check | Status | Ran | Seconds | Finding |
| --- | --- | --- | --- | --- |
| local_policy | PASS | yes | unmeasured | Installed policy and merged runbook read; no applicable AGENTS.md found in checked task/repository ancestor paths. Merged origin/main verified at 65a40e06a340b64b1ce060265a79ce1ba50fcb77. |
| executor_identity | PASS | yes | unmeasured | Wolfram.local; macOS 26.6.2 build 25G83; arm64. These are executor observations, not Darwin measurements. |
| cli_version | PASS | yes | unmeasured | codex-cli 0.153.4 |
| model_metadata | PASS | yes | unmeasured | Installed lease header: gpt-6-astra, openai, reasoning effort low. Terminal process success remains pending. |
| darwin_tailnet_ssh | FAIL | yes | 10.099 | ssh: connect to host 100.96.49.15 port 22: Operation timed out; exit 255. Target identity command did not execute. |
| darwin_lan_ssh | FAIL | yes | 10.093 | ssh: connect to host 10.57.5.168 port 22: Operation timed out; exit 255. Target identity command did not execute. |
| target_identity | UNKNOWN | no | 0 | Darwin hostname, macOS and hardware unverified. |
| uptime_disk_memory | UNKNOWN | no | 0 | No uptime, free disk or memory pressure evidence. |
| coordinator_heartbeat | UNKNOWN | no | 0 | No launchd jobs, mailbox heartbeat, last success or stale/error evidence. |
| forgejo_health_listeners | UNKNOWN | no | 0 | No process, version, health or listener evidence. Loopback ports 3001 and 8942 are intended only. |
| tailscale_serve_funnel | UNKNOWN | no | 0 | No Darwin Tailscale status, Serve/Funnel or exposure evidence. No phone test. |
| backups_restore | UNKNOWN | no | 0 | No mechanism, last backup age, destination or restore-test evidence. |
| canonical_git_integrity | UNKNOWN | no | 0 | Canonical paths unverified; no git fsck ran. |
| branch_gatekeeper_safeguards | UNKNOWN | no | 0 | No observed branch protection or VERIFY_ONLY/no-automerge evidence. |
| recent_errors | UNKNOWN | no | 0 | No target log reads; no error counts inferred. |

`UNKNOWN` means absent evidence, not healthy. Loopback Forgejo 3001 and gd2.git static service 8942 are intentions only. Exposure, backup success and restorability are all unknown. No raw target logs were collected or published.

## Blocker and ranked follow-ups

1. Owner: check Darwin locally for power, Ethernet and existing Tailscale/Remote Login health; restore a previously established route. The timeout does not establish which component failed. No new route or installation is requested.
2. After recovery, authorize a separate coordinated mailbox task to collect the baseline. This lease will not retry automatically.
3. Use verified evidence to prioritize coordinator heartbeat/error monitoring, backup age/destination/restore-test evidence, and bounded optimization. No infrastructure fixes were performed.

## Review and verification

Only the three task-scoped evidence files are proposed on `agent/wolfram/DARWIN-CORE-0001-RETRY-01` against `main`. The PR must stay draft and explicitly blocked; manual human merge only. JSON parsing, coverage consistency, redaction review, exact diff scope and SHA256SUMS are checked before publication. No target integrity, service, backup or log checks ran.

The main diagnostic bottleneck was SSH reachability (20.192 seconds across two bounded attempts). This run establishes CLI invocation and tool execution, not a completed Darwin baseline or a reporter receipt. Machine receipts are left to the installed reporter.

Existing GitHub PR notification path only; no phone/push delivery verified. Authenticated author and repository owner are both `pashamango`; a push notification is not verified. No reviewer, account or integration added.
