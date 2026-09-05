# Darwin MAILBOX

DARWIN-MAILBOX-0001 adds an outbound GitHub consumer for `codex@darwin.local`, host
`Darwin`. This mailbox address is a protocol identity, not a DNS endpoint or SMTP account.
Only `pashamango/minutta-rp-pr-cycle-lab`, author `pashamango`, open issues with the v1
marker, `ready`, R0/R1 and that exact agent/host pair are eligible. The six-field local
policy must match the compiled allowlist. Arbitrary identities cannot be supplied by an issue.

## Compatibility and boundaries

The adapter loads the existing watcher, dispatcher and reporter as local modules.
Wolfram entry points, policy and launchd files retain their defaults. The only shared
code changes are an optional dispatcher storage root (old default retained) and a reporter
branch-prefix constant (default `agent/wolfram/`). Darwin selects `agent/darwin/` locally.
No Wolfram installation, service, claim, issue or repository is changed.

Darwin adds a nonblocking OS file lock spanning the whole poll, claim, Codex process and
reporting. All supported Darwin entry points use this one lock; distinct tasks cannot
execute concurrently through this consumer. An arbitrary manually launched Codex outside
the mailbox does not participate in this lock. Wolfram and Darwin may operate independently.
This is not a distributed lock or distributed exactly-once execution.

Never reassign a task ID by editing an issue. Use a new ID and a previous-attempt link.
Darwin requires GraphQL `lastEditedAt: null`, including at refetch and reporting, and rejects
body edits even before first observation. It checks all current open and closed issue bodies
for ID collisions (bounded pagination fails closed instead of truncating). Historical erased
IDs are not a global registry. The unchanged, already-installed Wolfram consumer cannot gain
new cross-host historical enforcement without an explicitly approved future upgrade; owners
must obey the new-ID rule on both nodes. Never claim that a local claim prevents all possible
cross-node reassignment or that GitHub editing is a safe retry mechanism.

Admission records remain immutable and source digested. The fresh source is checked before
claim. Only `updatedAt` is normalized to the admitted timestamp to tolerate reporter comments;
all content fields remain bound, and body edit evidence is checked separately. Claims and
leases use atomic exclusive writes. Errors and timeouts keep their claims permanently.
The fixed policy preamble precedes untrusted source text, passed via stdin without shell
interpolation. Model, effort, authentication, sandbox and approval options are not overridden.

Each task runs in its private `state/runs/<task-id>/<lease>/` directory, also containing its
outcome, so no extra writable directories or permission overrides are needed. It never uses
the home directory as its working root. Directory symlinks are refused at installation.
The mailbox is not a security boundary against another process with the same macOS UID.

Codex is bounded to 900 seconds (180 for smoke), with at most 1 MiB retained per stdout/stderr
stream. Pipes continue to drain after the retention limit. Timeout kills the process group;
no automatic task retry follows. Private directories use 0700 and a 0077 umask. Immutable
evidence/log files remain inside private directories. History is retained; total historical
disk usage grows with task count. LaunchAgent stdout/stderr go to `/dev/null`; bounded poll
status is recorded locally, and writeback failures store only the exception class.

The reporter validates source, authoritative claim, envelope, lease, result and log hashes,
strict bounded JSON outcome, and exact Darwin PR branch/main/trusted repository bindings.
It publishes allowlisted machine receipts without summaries, prompts, secrets or raw logs.
Completed, blocked and failed outcomes remain distinct. Exit zero only means
EXECUTION_FINISHED. Repeated polls may reconcile receipt delivery but cannot re-execute a claim.

## Local paths and installation

* Development checkout: `~/ChitAkasha-Darwin/agent-mailbox/source/`
* Pinned installed files: `~/ChitAkasha-Darwin/agent-mailbox/releases/<merged-commit>/`
* Trusted installed policy: `~/ChitAkasha-Darwin/agent-mailbox/config/policy.yaml`
* Private evidence: `~/ChitAkasha-Darwin/agent-mailbox/state/{inbox,seen,claims,runs,control}/`
* Controlled future Git workspace hint: `~/ChitAkasha-Darwin/agent-mailbox/storage/workspaces/git/`
* User LaunchAgent: `~/Library/LaunchAgents/com.chitakasha.darwin-agent-mailbox.plist`

Before manual merge, only the isolated source checkout exists; no dispatcher is activated.
The PR handoff supplies ONE exact command with the actual PR number and full tested head SHA:

```sh
python3 ~/ChitAkasha-Darwin/agent-mailbox/source/tools/darwin-mailbox-manage activate --pr <PR> --expected-head <TESTED-40-CHAR-HEAD>
```

The command requires that exact PR/head, branch, repository, merged state and main base.
It proves the merge commit is an ancestor of current main, compares each installed file's
bytes at that merge commit to the locally checked commit AND local bootstrap files, then
installs only those verified files. Unrelated main changes are harmless; changed mailbox
files require new review, not a silent substitution. Existing different files, symlinks,
foreign installations and unknown LaunchAgents cause failure. Matching files are idempotent.
No polling for merge, automatic upgrades, branch writes, auto-merging or credential setup occurs.
Use the source checkout's manager for activation; installed copies have no Git checkout.

`install` with the same PR/head arguments installs the merged version in inactive mode.
`activate` snapshots the highest existing issue number (open and closed) and records an
initial activation timestamp before creating the smoke issue. Only higher issue numbers
with creation timestamps at or after that second can execute, regardless of first poll time.
The number watermark excludes the old queue even when GitHub timestamps share the same second;
a new smoke created within that second is not lost. The watermark never advances on repeated
activation. The installer creates at most one smoke
issue (records intent before POST; ambiguous POST failure is reconciled, never blindly retried).
It then enables only the Darwin LaunchAgent at 60-second intervals, initially in smoke-only mode.

The real CLI smoke reads `platform.system()` and `platform.node()`, writes identity evidence
and a bound outcome. The reporter independently compares that evidence to the current machine.
The smoke must have CLAIMED → EXECUTION_FINISHED → TASK_COMPLETED receipts. A subsequent
poll verifies delivery and the existing claim without a second execution before opening the
new-task queue. Failed/blocked smoke leaves the consumer in smoke-only mode for owner review;
no other task runs. Activation initiates this bounded test and returns immediately. It does
not claim completion before evidence exists. Old DARWIN-CORE tasks remain excluded permanently.

```sh
python3 ~/ChitAkasha-Darwin/agent-mailbox/source/tools/darwin-mailbox-manage status
python3 ~/ChitAkasha-Darwin/agent-mailbox/source/tools/darwin-mailbox-manage disable
```

Status shows loaded state, pinned hashes, watermark, smoke validation and last poll. Only a
loaded service with validated smoke and subsequent idempotent poll is reported CONNECTED.
Disable writes a local gate first and boots out only the Darwin label, preserving all history.
An in-flight execution interrupted by bootout remains claimed and will not retry. Repeating
the exact activation command removes only this adapter's disable marker and retains the
original watermark/history. It does not repeat a completed or failed smoke.

This is a per-user LaunchAgent: logout stops it; it does not poll during sleep; after reboot
it starts only after this user logs into a GUI session. Missed intervals do not imply an
always-on queue or a guaranteed catch-up schedule. A successful bootstrap alone proves neither
continuous availability nor a task outcome. No power settings are changed.

## Bootstrap observations and checks

Observed on Darwin 2026-09-05: `codex-cli 0.153.4`, executable
`~/.npm-global/bin/codex`; allowlisted local config fields `model = "gpt-6-astra"` and
`model_reasoning_effort = "medium"`. These are configuration observations, not evidence of
a completed future model request. CLI help confirms stdin input and the inherited configuration
flags used by the legacy dispatcher. OpenAI's [CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
documents the command interface. Global configuration and authentication were not changed.
Existing `gh` authorization is `pashamango` with repository ADMIN permission. Credentials are
not copied or recorded in evidence. The initial target directory and Darwin plist were absent.

Run `python3 -m unittest discover -s tests -v`. Bootstrap validation on 2026-09-05 passed
all 70 tests in 17.519 seconds on Python 3.14.6, including 25 Darwin tests and all existing
Wolfram tests. `git diff --check` passed; local status was INACTIVE with no installation,
activation or loaded Darwin label. The PR records the checked head. Automated tests use
fake Codex/GitHub and temporary homes; they are not live
smoke evidence. The only real smoke is initiated after manual merge by the command above.
Machine receipts in GitHub and notification delivery to the owner are different events;
no phone push is asserted.
