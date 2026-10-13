# TOKEN_GOVERNOR_PUSH_FIRST/v1 — Codex handoff 2026-10-13

Source: `pashamango/minutta-rp-pr-cycle-lab`, branch `agent/darwin/token-governor-pilot-511-20261013`, folder `ops/token-governor/`. Push-transport scripts are staged as a companion ZIP attachment in the originating ChatGPT conversation and are NOT yet committed to this GitHub branch; if unavailable, implement them under a new scoped branch and test them before deployment. The previous `DEPLOY_ON_DARWIN.md` describes pull-mode; **do not install that pull-mode LaunchAgent** in this recovery scenario.

## What is proven from Pasha's local Codex ARR-001 report

- Wolfram -> Darwin: authenticated outbound SSH exists with BatchMode, strict host-key validation, no agent forwarding. Pasha reports that a sanitized receipt crossed and its SHA-256 matched.
- `governor.py` and 15 baseline tests passed on Wolfram.
- Inbound Wolfram SSH / Remote Login remains disabled; it is **not** required for push mode.
- CodexBarCLI unavailable; installer failed closed with generic URLError. Root cause **unknown**; do not diagnose as DNS without evidence.
- The companion push transport is fixture-tested in a separate sandbox: **24 tests** together (15 baseline + 9 new). It is not verified on physical machines yet.
- No cloud Work attribution or real ChatGPT Work quota claim is supported.

## Execution objective

1. Install CodexBarCLI on Wolfram through an official signed/source-verified release using whatever *already authenticated* fetch path works (direct on Wolfram or download on Darwin then outbound scp pull from Wolfram). Never copy raw OAuth tokens or Codex files. Do not bypass TLS validation.
2. Run a real `governor.py probe` on Wolfram. Validate sanitized output is current, with weekly observed/reset times and percentages. `UNAVAILABLE` is a valid blocked state, not zero usage. Compare with independent ChatGPT Settings Usage before claiming it represents Work quota.
3. Copy `push_quota.py`, `test_push_quota.py`, and `install_push_launchagent.py` from the provided companion ZIP (or reproduce them and their 9 tests in a new commit) into Wolfram `~/token-governor`. Run all 24 fixture tests on Wolfram. Darwin must have already verified `governor.py ingest`; use the existing trusted outgoing SSH config and actual authorized Darwin username.
4. Execute one `python3 ~/token-governor/push_quota.py --dest pavelcherkashin@100.112.18.4` on Wolfram. Confirm `DELIVERED`, sanitized `sample_sha256`, and >=1 delivered. Check Darwin `python3 ~/token-governor/governor.py status` and SQLite record created with owner-only permissions. If actual SSH username differs, use real existing username. If no source, leave queue untouched and status PROBE_UNAVAILABLE.
5. Only after a fresh real sample is verified on both hosts, install user-level hourly launch agent **on Wolfram**, using `python3 ~/token-governor/install_push_launchagent.py --dest pavelcherkashin@100.112.18.4`. For existing plist, back up and use `--replace`; bootstrap `gui/$(id -u)` in logged-in GUI user domain; verify launchctl running and log receipts. Normal screen lock is fine; sleeping is not guaranteed to run scheduled jobs.
6. Local spool: `~/.local/share/token-governor/spool/{pending,sent,expired,invalid}`. It holds sanitized JSON only, with filename stable by provider+observed time. **Expired (>80 min) observations are archived locally and not falsely imported into Darwin's fresh SQLite DB.** A larger historical backfill is a separate later design task.
7. Check failure/retry without injecting synthetic data into production SQLite. Include accurate `PARTIAL`/`BLOCKED` where appropriate, never DONE without real source+delivery+launchd evidence.

## CodexBar download recovery

The initial Wolfram installer uses Python `urllib.request.urlopen()` for `https://api.github.com/repos/steipete/CodexBar/releases/latest` and for the release asset. It deliberately hides the underlying URLError. Locally classify the failing stage safely (`DNS`, TLS cert trust, HTTP 403/404/429, proxy, timeout, release-asset CDN). Report error class and HTTP status/domain only, never cookies or credentials. Avoid repeated probing.

Official GitHub release **v0.74.1** (published Oct 11, 2026) exposes:

- Apple Silicon: `CodexBarCLI-v0.74.1-macos-arm64.tar.gz`; official release SHA-256 `9db95058eddc88241d228515a30af6868ca067ba9a26452e4642ef59e2f54f52`.
- Intel: `CodexBarCLI-v0.74.1-macos-x86_64.tar.gz`; official release SHA-256 `d1d78412ebb663a47ab9c972aba8177afecd320fb8617a36cfcad55267d62263`.

These digests were checked via GitHub's official Releases API in this Chat session. The Codex executing on machines should independently check release metadata before installing; do not trust filename alone. Detect Wolfram CPU using `uname -m` **on Wolfram**, not Darwin. If direct download fails, Darwin may fetch the correct asset into its own owner-only staging directory, verify SHA-256, and Wolfram may fetch that file via its existing outbound SSH/SCP route to Darwin; verify SHA-256 again on Wolfram. Do not use sudo, curl|sh, `StrictHostKeyChecking=no`, insecure TLS, or arbitrary mirrors. Extract ONLY the `CodexBarCLI` binary into `~/token-governor/bin` with owner-only permissions. CLI may require additional bundled resources; check version and actual usage before declaring success. Code signing/quarantine requirements apply as macOS enforces them; never strip system protections to bypass failures.

Official source: `https://api.github.com/repos/steipete/CodexBar/releases/latest` and `https://github.com/steipete/CodexBar/releases`.

## User-level push agent and proof

```sh
# Wolfram, after real CodexBar probe works:
python3 "$HOME/token-governor/push_quota.py" --dest pavelcherkashin@100.112.18.4
python3 "$HOME/token-governor/install_push_launchagent.py" --dest pavelcherkashin@100.112.18.4
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.chitakasha.token-governor-push.plist"
launchctl kickstart -k "gui/$(id -u)/org.chitakasha.token-governor-push"
launchctl print "gui/$(id -u)/org.chitakasha.token-governor-push"
```

If `launchctl bootstrap gui/...` is not available under the logged-in GUI session, do not claim the agent is running; diagnose user domain instead of forcing privileged changes.

## Acceptance

- Real CodexBar CLI version: observed on Wolfram (or honest failure)
- Real quota reading: fresh and sanitized (or honest failure)
- End-to-end strict-SSH push from Wolfram to Darwin: `DELIVERED` AND Darwin SQLite observation, not just transport hash
- 24 fixture tests on Wolfram, baseline tests on Darwin
- Hourly launchd agent: loaded, kickstarted and a real receipt logged
- No raw credentials in remote payloads or public issue comments
- GitHub Issue #511 receives one concise status receipt, if delivery is authorized and available

Do not mark pilot DONE if any live gate remains unverified.