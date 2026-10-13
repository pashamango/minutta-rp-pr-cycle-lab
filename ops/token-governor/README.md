# TOKEN_GOVERNOR_CODEXBAR_PILOT/v1

**Status:** v1.1 fixture-tested, contains hardening of source labels and SQLite permissions.  Real Wolfram/Darwin deployment **not** yet confirmed.  
**Tracking:** https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511  
**Model/cost:** monitoring is deterministic Python + CodexBar CLI, never runs Work.

## Design

- Wolfram (`probe`): reads quota using a local authenticated CodexBar CLI (`--source oauth`); stdout contains ONLY a sanitized subset of quota data, never email, cookies, tokens or raw session logs.
- Darwin (`poll`): every 60 minutes fetches Wolfram sample via trusted Tailscale SSH and writes local SQLite records. Alert on weekly burn `>=4 pp/hour` AND `>=2 pp` absolute, weekly remaining `<20%`, stale sample, or source failure. Events deduplicated over 6 hours.
- Optional Github escalation: if `gh` CLI is available/authenticated on Darwin, `--notify-issue pashamango/minutta-rp-pr-cycle-lab#511` posts a short alert comment. Without `gh`, alerts are durable but **not delivered**. Do not claim notification has been delivered without a `GITHUB_SENT` receipt.
- No automatic killing of existing Work branches; remote cloud-branch attribution is **UNATTRIBUTED_CLOUD_WORK**.
- A safe-on quota status does NOT grant permission to start Work. Governor `status` only reports whether a subsequently integrated controlled executor *could* run.

## Step 1 — Wolfram (MacBook Pro)

1. Download and unzip `token-governor-pilot-v1.zip` from this chat to `~/token-governor`:

```bash
mkdir -p "$HOME/token-governor"
unzip -o "$HOME/Downloads/token-governor-pilot-v1.zip" -d "$HOME/token-governor"
python3 "$HOME/token-governor/install_codexbar_local.py"
"$HOME/token-governor/bin/CodexBarCLI" --version
```

The installer downloads **only** an official GitHub release asset, requires a published GitHub SHA-256 digest, and installs into `~/token-governor/bin` without sudo. If the asset has no digest or is unavailable, installer **fails closed**. In that case install via the official [CodexBar Releases](https://github.com/steipete/CodexBar/releases) / the GUI, then verify `codexbar --version` or use a local CLI binary. Do not use `curl | sh`.

2. Ensure Codex CLI is authenticated **under your own Wolfram login**. No copy of auth material to Darwin is required. Run:

```bash
python3 "$HOME/token-governor/governor.py" probe
python3 -m unittest discover -s "$HOME/token-governor" -p 'test_*.py' -v
```

If `probe` returns `UNAVAILABLE`, run the more diagnostic **locally only**:

```bash
"$HOME/token-governor/bin/CodexBarCLI" usage --provider codex --source oauth --format json --pretty
"$HOME/token-governor/bin/CodexBarCLI" guard --provider codex --window weekly --min-remaining 20 --json
```

**Do not paste raw CodexBar JSON into a public GitHub issue:** it may include email and account identifiers. Compare the remaining-percent and next-reset values with `ChatGPT Settings → Usage`. If they disagree, mark the quota source `UNVERIFIED_FOR_WORK`.

3. Check SSH is active on Wolfram (System Settings → General → Sharing → Remote Login). Limit access to your own account and Tailscale. Do not change firewall, Keychain, SSH agent forwarding or `sshd_config` in this pilot.

## Step 2 — Darwin (always-on Mac)

1. Unzip exactly the same archive into `~/token-governor`:

```bash
mkdir -p "$HOME/token-governor"
unzip -o "$HOME/Downloads/token-governor-pilot-v1.zip" -d "$HOME/token-governor"
python3 --version
```

2. Replace `<WOLFRAM_SSH_USER>` with the **actual macOS account name on Wolfram**. Set up trusted Tailscale SSH access using your existing configuration. From Darwin test:

```bash
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ForwardAgent=no \
  '<WOLFRAM_SSH_USER>@wolfram' 'python3 "$HOME/token-governor/governor.py" probe'
```

The remote JSON MUST contain `weekly_used_pct`, `weekly_reset_at`, and `observed_at`, but no email or credentials. If SSH is not yet trusted, establish host-key trust interactively after verifying the target host fingerprint. Do not use `StrictHostKeyChecking=no`. If `wolfram` does not resolve, use Tailscale MagicDNS FQDN or an existing SSH config host alias; see `tailscale status` on Darwin. The target hostname must be safe ASCII (`user@host`).

3. Run one real poll (source will be Wolfram):

```bash
python3 "$HOME/token-governor/governor.py" poll --host '<WOLFRAM_SSH_USER>@wolfram'
python3 "$HOME/token-governor/governor.py" status
```

Expected first response: `BASELINE` if fresh and weekly remaining `>=20%` (otherwise `LOW_BUDGET`). This step does not launch a Codex model.

4. Install hourly `launchd` user agent (an already logged-in Darwin user):

```bash
python3 "$HOME/token-governor/install_launchagent.py" --host '<WOLFRAM_SSH_USER>@wolfram'
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.chitakasha.token-governor.plist"
launchctl kickstart -k "gui/$(id -u)/org.chitakasha.token-governor"
tail -n 10 "$HOME/Library/Logs/token-governor.log"
```

The LaunchAgent runs after login and then hourly. To replace/update it, first run `launchctl bootout "gui/$(id -u)" ...`, then rerun installer with `--replace`, then `bootstrap`.

## Step 3 — Optional delivery to Issue #511

To publish alerts from Darwin without ChatGPT tokens, install/sign into GitHub CLI **locally** on Darwin, then validate:

```bash
gh auth status
```

Reconfigure the LaunchAgent after `launchctl bootout`:

```bash
python3 "$HOME/token-governor/install_launchagent.py" --replace \
 --host '<WOLFRAM_SSH_USER>@wolfram' \
 --notify-issue 'pashamango/minutta-rp-pr-cycle-lab#511'
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.chitakasha.token-governor.plist"
launchctl kickstart -k "gui/$(id -u)/org.chitakasha.token-governor"
```

**Alert delivery is not guaranteed:** `gh` may be missing, not authenticated, or unable to send; check `delivery` in the output. Default launch agent leaves GitHub delivery off. For a bounded test you may use synthetic samples (below) and send only the resulting test incident.

## Step 4 — Synthetic test with no Codex/Work consumption

On Darwin, run:

```bash
python3 -m unittest discover -s "$HOME/token-governor" -p 'test_*.py' -v
```

For an end-to-end simulated spike, use the unit tests (they use temporary SQLite databases and never call GitHub). Do not modify production quota observations just to trigger a synthetic alert.

## Diagnostics and stopping

```bash
# Darwin: current authoritative state, without any external call
python3 "$HOME/token-governor/governor.py" status
# Darwin: recent run logs
tail -n 20 "$HOME/Library/Logs/token-governor.log"
tail -n 20 "$HOME/Library/Logs/token-governor-error.log"
# Darwin: stop monitoring (reversible)
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.chitakasha.token-governor.plist"
```

**Success needs actual-on-host evidence:** CLI version, fresh observation on Wolfram, SSH poll on Darwin, at least two time-separated measurements or a synthetic burn spike test, persisted SQLite record, and (if escalation channel configured) confirmed GitHub comment. Current issue is **BOOTSTRAP_REQUESTED**, not DONE.

## Threat model / missing capabilities

- Web UI and CodexBar OAuth quotas may not cover exactly the same subscription budget. Cross-check once before trusting these readings as Work authority.
- Hourly checks can miss short-lived spikes. The fastest reaction is at the next check; 10–15 min interval later if needed.
- Some CodexBar CLI builds or macOS versions may not support OAuth mode. Fails closed.
- Cloud Work-branch attribution is unavailable from CodexBar cost logs alone. Requires explicit run registry or a supported historical mapping from ChatGPT Analytics.
- GitHub comments may not provide push notifications; confirm watch/subscription separately. The local ledger remains the primary audit log.
- Uploaded HTML Usage snapshots can contain account/session identifiers; they are not shipped in this artifact.

## Codex handoff 2026-10-13

The program is intentionally not a ChatGPT cloud automation. Darwin must run its own `launchd` user agent and use a read-only SSH command to Wolfram. Only sanitized local receipts should be posted in GitHub Issue #511. Do not treat passing fixture tests as a live installation. Verify fresh `probe` on Wolfram before enabling the polling LaunchAgent.

**Do not post:** CLI raw JSON, access tokens, paths including user names, machine SSH host keys, unrelated files or full debug logs.