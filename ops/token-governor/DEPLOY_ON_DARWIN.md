# PILOT-511 Darwin Codex handoff — 2026-10-13
Status: DEPLOYMENT HANDOFF; **not yet installed or verified on physical hosts**.
Tracking: https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511
Source branch: `agent/darwin/token-governor-pilot-511-20261013`
Source dir: `ops/token-governor/` (governor.py, test_governor.py, install_codexbar_local.py, install_launchagent.py, README.md).
Local code review: 15/15 Python unittest fixtures PASS on assistant container, not on hosts. Original archive checksum previously verified to match issue #511; this staging branch contains two source hardening tests and code changes.

## User authorization
Pasha explicitly authorizes installing/testing pilot #511, including access via existing trusted SSH to Darwin and Wolfram. This permits bounded installation and local read-only telemetry. Do NOT change global macOS security settings, bypass authentication, export credentials, invoke Work/Codex jobs for quota burn, or publish private logs. Do not incur paid cloud costs or silently modify ChatGPT model/effort. The agent may use SSH, git/gh, Python 3 and launchctl under current authorized local user.

## Procedure for Codex running on Darwin
1. Identify Darwin hostname, local OS and Python 3 version, Tailscale status, disk availability; do not capture secrets. Check whether a pilot installation already exists, preserve old files/config before replacement.
2. Obtain this branch using already-authenticated `gh` or git, in a fresh, user-owned temporary directory. Do not checkout or change another repository. If private repo access unavailable, stop with READ_BLOCKED and state remediation. Verify paths in `ops/token-governor/` and record branch commit SHA.
3. Stage files in `$HOME/token-governor` with restrictive permissions (`umask 077`); keep full provenance. Run `python3 -m unittest discover -s "$HOME/token-governor" -p 'test_*.py' -v`; 15 tests should pass. Record count.
4. Discover Wolfram in tailnet (`tailscale status`, `tailscale ping`), determine real SSH username from existing trusted SSH configuration. DO NOT guess credentials or bypass host-key verification. Verify connection with `ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o ForwardAgent=no -o ConnectTimeout=10 USER@WOLFRAM 'printf wolfram-reachable'`. If SSH trust/key missing, stop remote steps and give Pasha a single precise requested action; never copy a private key.
5. Copy only the four .py files plus README to `$HOME/token-governor` on Wolfram using safe `scp` or `tar|ssh` with existing auth (no agent forwarding). Check remote Python 3 and OS; run 15 unit tests there. Detect existing CodexBar CLI; if missing and Wolfram OS supports it, run `python3 "$HOME/token-governor/install_codexbar_local.py"` on Wolfram only. Installer fetches only official steipete/CodexBar release, verifies SHA-256 from GitHub release asset metadata, fails closed on mismatch; never use curl|sh or sudo. Check CLI version. Do not assume GUI CodexBar app compatible with Darwin macOS 12.7.6.
6. On Wolfram execute `python3 "$HOME/token-governor/governor.py" probe`. Capture only the **sanitized stdout JSON**, not raw CLI output, OAuth material or account identity. If UNAVAILABLE, stop and diagnose locally without publishing secrets. If source is Codex CLI, **do not claim confirmed ChatGPT Work quota** until compared with a human-supplied Usage screen. Mark Work attribution UNATTRIBUTED_CLOUD_WORK.
7. On Darwin run `python3 "$HOME/token-governor/governor.py" poll --host USER@WOLFRAM` followed by `python3 "$HOME/token-governor/governor.py" status`; record outcome and persisted SQLite existence/permissions. Pilot may return exit 2 for a deliberate quota alert; do not interpret as Python test failure. If quota is stale/blocked, status must fail closed and no synthetic data enters real database.
8. Only after verified live SSH+Wolfram probe, install hourly agent via `python3 "$HOME/token-governor/install_launchagent.py" --host USER@WOLFRAM`. If existing plist, inspect and back it up before using --replace. Bootstrap `launchctl bootstrap gui/$(id -u) "$HOME/Library/LaunchAgents/org.chitakasha.token-governor.plist"` only if logged-in GUI domain is available; kickstart, then `launchctl print gui/$(id -u)/org.chitakasha.token-governor`. If GUI session unavailable over SSH, do NOT claim scheduled monitoring; explain how to load it in the logged-in session. Verify one logged run and local log.
9. Optional GitHub test: if local `gh auth status` succeeds, publish **one** clearly marked minimal sanitized deployment receipt to issue #511, without hostname/user/email/IP/auth material. Use pilot --notify-issue only after verifying it will not flood unrelated alerts. If unavailable, record LOCAL_LEDGER_ONLY and do not claim delivery.
10. Return final machine-readable summary (status per Darwin and Wolfram, explicit verified dates, CLI version, anonymized source, quota freshness, local tests results, SSH poll outcome, launchd loaded/not-loaded, persistence and GitHub delivery, limitations/next actions). Work quota source match must remain UNVERIFIED_FOR_WORK until independently compared. Mark DONE only if real evidence supports it; otherwise BLOCKED/PARTIAL with exact reason.

## Rollback
Darwin: `launchctl bootout gui/$(id -u) "$HOME/Library/LaunchAgents/org.chitakasha.token-governor.plist"` (only if loaded). Disabling the LaunchAgent stops future polls without deleting the retained local SQLite audit database. Do not delete previous data or change unrelated user services.

## Safe command examples
```sh
set -eu
umask 077
BRANCH=agent/darwin/token-governor-pilot-511-20261013
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pilot511.XXXXXX")"
gh repo clone pashamango/minutta-rp-pr-cycle-lab "$WORKDIR/repo" -- --branch "$BRANCH" --single-branch --depth 1
mkdir -p "$HOME/token-governor"
cp "$WORKDIR/repo/ops/token-governor/"*.py "$WORKDIR/repo/ops/token-governor/README.md" "$HOME/token-governor/"
python3 -m unittest discover -s "$HOME/token-governor" -p 'test_*.py' -v
```
