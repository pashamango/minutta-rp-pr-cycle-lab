# Darwin bounded R1 capability broker

This change is authorized by Pasha's local interactive DARWIN-MAILBOX-0002-BOOTSTRAP-01
instruction. Issues #57 and #58 are specification and diagnostic evidence. Their
POLICY_CONFLICT is expected: mailbox task data cannot authorize changing the protocol
that interprets it. Ordinary tasks still cannot upgrade the mailbox.

## Declaration

Use exactly one mailbox metadata block. Capability values use strict single-line JSON
inside that block; YAML lists, duplicate fields, unknown capabilities, unscoped declarations,
and non-R1 declarations fail admission. No field means the original restrictive command
and behavior. Wolfram modules and installation remain unchanged.

```yaml
id: FRESH-PREVIEW-TASK
agent: codex@darwin.local
host: Darwin
status: ready
risk: R1
capabilities: ["loopback-user-service", "tailscale-serve-additive"]
capability_scope: {"application":"example-preview","port":18765,"operation":"install","serve_path":"/example-preview/"}
```

Both declarations are in the source body covered by source_sha256, admitted metadata,
and the envelope. Fresh source validation compares all metadata and capability scope at
reporting. Post-claim body edits and comment-based capabilities cannot grant authority.
The run retains its exclusive permanent claim even when verification or broker execution fails.

The worker prepares static files under its run's `service-content/` and writes
`capability-request.json` with exactly `task_id`, `lease_id`, `source_sha256`,
`capabilities`, and `capability_scope` copied from its envelope. A completed worker
outcome is a request for broker validation, not evidence of deployment success. Only the
installed broker applies changes after validating outcome/source and checking the worker
has not changed protected runtime files, user LaunchAgents, listeners or Serve configuration.
Protected mailbox/LaunchAgent file checks also wrap no-capability workers; their command
and infrastructure authority remain unchanged. Worker PASS checks cannot substitute for the broker's independent evidence.

The compiled server serves static content only, binds 127.0.0.1 on an explicit
nonprivileged port, denies directory listings and path escape, and has no CGI or arbitrary
command feature. Bundle size is limited to 64 MiB / 4096 files; symlinks and special files
are refused. `install` creates or updates only a broker-owned named static preview; `remove` removes it.
A Serve-only capability can attach/detach the named path on an existing verified broker-owned
loopback preview; it cannot point at an arbitrary listener. Existing application/port identity
and owned route must match. Removing a preview with an attached route requires both capabilities.
Application backups and exact inverse-handler plans are retained under `service-backups/<lease>`.
Evidence says `rollback-plan-verified`, not that a live rollback was performed.

The application name is bounded and cannot name mailbox, SSH or Tailscale.
The broker generates the only supported user LaunchAgent. Root, system daemons, arbitrary
executables, arbitrary listeners, LAN/public bind, SSH, credentials, ACL/key/auth changes,
Funnel, cross-host control, automatic merge and mailbox self-modification remain forbidden.

Both capabilities require a read-only Serve preflight. Existing Funnel enablement or an
unowned handler/TCP forward aimed at the preview port blocks even loopback-only creation,
so a new listener cannot activate a dormant Serve exposure.

Serve uses only the existing authenticated local node, HTTPS 443, one non-root path, and
an owned loopback HTTP target. The broker never invokes Funnel, reset, up, login or ACL/key
commands. It rejects unsupported CLI/schema, foreground Serve, Funnel enablement, path
collisions and incompatible TCP 443 usage. Structural before/after comparison permits only
that handler and its required HTTPS listener, preserving other configuration. Rollback
uses only the inverse owned-handler command; scope drift leaves a failure for local review,
never a broad configuration restore.

## Residual boundary

This is a conservative static preview capability, not a general application runtime grant.
Dynamic backends or arbitrary service commands require separate reviewed installed code.
The inherited Codex sandbox/model/effort/approval flags are unchanged. A restrictive worker
need only write inside its run; it does not need permission to administer launchd/Tailscale.
This remains a same-UID trust boundary: a malicious unsandboxed process with the user's full
permissions could tamper with the broker, evidence, history or credentials. File hashes and
pre/post inventories detect ordinary scope drift, not an adversary controlling the entire
account. No claim of OS isolation or transient-action detection is made. Account-owned
Tailscale Serve access must already work; failure is terminal and requires a fresh task.

## Manual upgrade and recovery

The final PR body contains one command pinned to the actual PR number and tested full
40-character head. Pasha runs it locally on the existing Darwin account only after manual
merge. Use a merge commit: a squash/rebase that discards the tested head intentionally fails
the canonical-main ancestry requirement. The command obtains a detached temporary checkout;
it does not alter an existing source checkout or either mailbox's task history.

`darwin-mailbox-upgrade upgrade` verifies the exact PR number, trusted repository, branch,
base, head, closed/merged state and both head/merge ancestry. It compares local git object,
checkout, merged GitHub bytes and staged installed hashes. Existing installed bytes are
checked against the retained installation manifest. Unknown installation layouts fail closed.
The existing non-root account and verified Darwin installation are required; no remote SSH is used.
See the exact host compatibility rule below.

The install and cycle locks exclude active dispatch. The upgrader stages a complete release,
records a durable journal, gates polling, boots out only the Darwin label and atomically
replaces its plist runtime path. It preserves the original interpreter/PATH and installation
manifest. It does not change policy, activation watermark, claims, runs, receipts or history.
The new runtime's offline smoke must pass before the gate is removed. A normal exception
restores the old pointer; an interrupted or failed recovery leaves the gate in place.
No mixed runtime is selected. Immutable staged releases and the journal are retained for audit.

Rollback runs the reviewed `tools/darwin-mailbox-upgrade rollback` from that same detached
checkout (or the verified installed upgraded release). It checks original release hashes,
restores only the owned old plist and preserves even history accumulated after upgrade.
It never clears claims or activation. It deliberately does not undo separate preview tasks;
those use their own explicitly scoped remove requests.

## Harmless verification

Run `python3 <verified-upgraded-release>/tools/darwin-mailbox-upgrade smoke` locally.
It checks the unchanged legacy command and restrictive preamble, empty legacy capabilities,
allowlisted single/two capability declarations and envelope tamper rejection. It verifies
#55/#56/#57/#58 are ineligible even with future timestamps and compares hashes of activation,
claims, admissions, runs and receipts before/after. It never calls dispatch/cycle, Codex,
launchd, Tailscale, or GitHub. Expect `historical-execution-count: 0` and PASS results.
The upgrade journal also records the before/after preserved history and installed smoke.
These offline checks are not a live application deployment or an actual model invocation.
No CEOffice deployment is included; use a fresh subsequent task after upgrade.

The additive CLI syntax and target-optional `off` operation follow the official
[Tailscale Serve command reference](https://tailscale.com/docs/reference/tailscale-cli/serve).
Only the flags documented there are used; CLI help/schema probes and structural checks remain
mandatory on the installed version. Existing tailnet HTTPS authorization must already be
available; this upgrade does not enable or approve it.

## Local identity hotfix after PR #60

The original exact `ComputerName == Darwin` check incorrectly rejected the observed
`Darwin-on-MacBookPro3`. No Mac rename is needed. The hotfix retains macOS/non-root checks
and requires current-user ownership of the existing installation, manifest, activation,
policy and Darwin LaunchAgent. It checks the compiled agent/host/repository policy,
completed activation and an absolute runtime path inside this installation. Existing
installed-byte checks and exact runtime-pointer validation still precede mutation.
A copied installation with stale absolute paths, incomplete state, wrong ownership,
wrong policy, label or installed bytes is rejected.

There is no immutable hardware ID in the original installation: `codex@darwin.local` and
`host: Darwin` identify the logical consumer, not the physical Mac. As an additional narrow
compatibility check, the exact (ComputerName, LocalHostName) pair must be either
(`Darwin-on-MacBookPro3`, `Darwin-on-MacBookPro3`) or legacy (`Darwin`, `Darwin`). No prefix,
substring, suffix or case-folded matching is used. HostName may remain unset; the observed
Tailscale DNS `darwin-on-macbookpro3-4.tail94aa6c.ts.net.` is supporting diagnostic context,
not a new authorization dependency. No Tailscale or naming changes are made.
A complete same-user clone with rewritten/matching paths and those exact names cannot be
distinguished without a previously provisioned hardware-bound identity. The hotfix does
not claim to solve that residual same-UID limitation or silently create a new identity.

The reported PR #60 failure occurred in `local_host()` before remote verification, locks,
release staging, disable gates, journals, or LaunchAgent changes. The wrapper had already
created a disposable detached checkout at `~/ChitAkasha-Darwin/mailbox-upgrade-0002.*`
(possibly including Python bytecode caches). It needs no cleanup for correctness; retain
it for inspection or later remove only the identified disposable checkout. No mailbox
state cleanup or rollback is required for this specific error. This conclusion follows
from the reported error and code ordering, not a remote inspection of Darwin.

Use the hotfix PR's actual-number/full-head replacement command after manual merge with a
merge commit. Its compiled expected branch is `agent/wolfram/DARWIN-MAILBOX-0002-HOTFIX-01`;
merged-state and both canonical-main ancestry checks are unchanged. All capability,
watermark/history, permanent #55/#56/#57/#58 exclusions and rollback behavior remain intact.
