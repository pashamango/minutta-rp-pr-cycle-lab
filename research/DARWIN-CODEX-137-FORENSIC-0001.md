# BLOCKER_ANALYSIS/v1 — Darwin Codex exit 137 forensic

Status: `EVIDENCE_INSUFFICIENT`

Task: `DARWIN-CODEX-137-FORENSIC-0001`  
Source issue: `pashamango/minutta-rp-pr-cycle-lab#170`  
Source SHA-256: `c63311b43465cf786a3874ff19ae4953963d98bd24924fd3750f127c85369431`  
Lease: `cb2d1c351b074c42a333b0d2f4f2824e`

## Scope

Diagnosis only. No repair, configuration change, install, reboot, process kill, or security change is authorized.

## Publication gate

- Skeleton commit: `517bf41`
- Initial PR URL: https://github.com/pashamango/minutta-rp-pr-cycle-lab/pull/171
- Initial PR head: `517bf41`
- Probe window: `2026-09-12T21:13:35Z` UTC, bounded read-only SSH session

## BLOCKER_ANALYSIS/v1

- Verdict: `EVIDENCE_INSUFFICIENT`
- Exact reproduction: the authorized `darwin` SSH alias connected. `/bin/true` returned `127` with `bash: /bin/true: No such file or directory`; `/bin/echo ok`, `/bin/ls /`, and `/usr/bin/uname -a` returned `0`. No Codex-through-helper reproduction was observable from this session.
- Last verified-good transition: SSH transport and remote shell execution; `/bin/echo`, `/bin/ls`, and `/usr/bin/uname`.
- First broken/missing transition: the direct `/bin/true` leaf path is absent on the reachable Darwin host; the Codex execution-path boundary and its reported 137 victim remain unobserved.
- Actual killed process: unobservable. Current process listing showed Codex node/native/app-server processes alive; no matching Codex/node DiagnosticReport was present.
- Strongest killer/cause evidence: none identifying a killer. The host snapshot weakens simple OOM: 87% free memory, no compressor use, zero swap, zero pageouts, unlimited RSS/data limits, and 18% root capacity. Unified logs in the 15-minute window contained no matching kill/termination record.
- Ranked hypotheses: HIGH — missing observability at the Codex dispatch/helper boundary; MEDIUM — path/runtime compatibility issue suggested by missing `/bin/true` (not evidence of 137); LOW — system-wide OOM, per-process limit, watchdog, AMFI/signing, architecture incompatibility, or intentional parent SIGKILL (not supported by this window).
- Wise Broker / #160 rapid `TASK_BLOCKED`: unknown; this probe did not exercise that path.
- Semantic work status: forensic diagnosis incomplete; no research result claimed
- Retry safety: read-only probe is retryable; do not repeat beyond the bounded window
- Minimum missing capability/dependency/representation: a repeatable Codex invocation with its helper/sandbox/leaf PID and exit-status handoff observable, plus a matching failure report or tightly correlated unified-log record.
- Next safe continuation: have the Darwin owner run one already-supported failing Codex command while retaining the parent/child/status evidence, then correlate it to a single timestamped log/report window.
- Cheapest reversible repair proposal: add bounded PID/PPID and wait-status logging at the existing Codex execution handoff, without changing command behavior; do not execute under this task.
- Pasha genuinely required: not for this evidence review; required only if the missing observability must be added to a protected Darwin runner or if the `/bin/true` path discrepancy needs owner action.

## Sanitization

Only hashes and redacted excerpts may be published. Secrets, environment contents, tokens, cookies, personal documents, and unbounded raw logs remain on the origin host.
