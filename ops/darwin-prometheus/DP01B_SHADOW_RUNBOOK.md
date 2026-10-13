# DP-01B E2: production-safe SHADOW-first acceptance

**Tracking:** [MIN-51](https://linear.app/mindrock/issue/MIN-51/dp-01b-preserve-deployed-collector-and-add-host-health-adapters) · [Issue #511](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511). **Do not convert existing E1 production ledger to v0.2 format as part of this task.**

## Why shadow instead of in-place migration

Darwin Codex DP01B_STAGING_RECEIPT/v1 (2026-10-13, user-supplied) reported 68/68 PASS, current production journal verified by BOTH readers, no modification to production, and a verified disposable `host.snapshot` write. It also demonstrated that once `host.snapshot` is appended, the old E1 reader returns `INVALID`. In-place append would eliminate simple reader rollback; retaining the original E1 journal entirely unchanged is lower risk.

**Proposed independent sidecar:**

| Resource | E1 production (unchanged) | E2 shadow (new) |
|---|---|---|
| launchd | `org.chitakasha.darwin-prometheus-ledger` | `org.chitakasha.darwin-prometheus-host-shadow` |
| script directory | `$HOME/darwin-prometheus/` | `$HOME/darwin-prometheus-dp01b-shadow/` |
| data root | `~/.local/share/darwin-prometheus` | `~/.local/share/darwin-prometheus-dp01b-shadow` |
| event types | quota.* + host.health | host.snapshot only initially |
| reader | working E1 | isolated DP-01B v0.2 reader |

**Guard:** `host_shadow_cycle.guarded_root()` refuses writing into or enclosing E1 data root, including symlink aliases. It does not modify `run_cycle.py`, `governor.py`, quota collector, VPN or existing plist. New agent will be generated (not loaded) and then loaded only after real disposable smoke tests. A shadow snapshot is **not** yet a production sensor until the host confirms unattended runs.

## Darwin Codex: safe rollout sequence

1. In an authorized Darwin shell, fetch exact reviewed branch SHA. Stage **only** `event_ledger.py`, `host_adapter.py`, `host_shadow_cycle.py`, `install_host_shadow_launchagent.py`, `test_host_shadow_cycle.py`, and earlier DP-01B tests under `$HOME/darwin-prometheus-dp01b-shadow/`. Do not overwrite files in `$HOME/darwin-prometheus/`.
2. Record E1 `verify` output and checkpoint hashes before installing the shadow; check its `launchd` job still loaded. Run tests from the staging folder using the actual Darwin Python. Repeat the existing DP01B 44 fixture tests plus new shadow tests. There should be **55 ledger/adapter/shadow tests** and **24 Governor/push tests = 79 total** in the sandbox reference suite; host may legitimately differ if deployed implementation tests are not staged.
3. Use a disposable root to verify a real host snapshot (and no quota samples) before enabling an agent:

```sh
umask 077
stage="$HOME/darwin-prometheus-dp01b-shadow"
tempdir="$(mktemp -d)"
python3 "$stage/host_shadow_cycle.py" --root "$tempdir/ledger"
python3 "$stage/event_ledger.py" --root "$tempdir/ledger" verify
python3 "$stage/event_ledger.py" --root "$tempdir/ledger" project
python3 "$stage/event_ledger.py" --root "$tempdir/ledger" checkpoint
python3 "$stage/event_ledger.py" --root "$tempdir/ledger" verify
```

4. On success, create the new sidecar user launchd plist, **without touching E1**:

```sh
python3 "$stage/install_host_shadow_launchagent.py" --dry-run
python3 "$stage/install_host_shadow_launchagent.py"
# Only then, from the existing logged-in GUI user's launchd domain:
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.chitakasha.darwin-prometheus-host-shadow.plist"
launchctl print "gui/$(id -u)/org.chitakasha.darwin-prometheus-host-shadow"
```

5. Inspect first `RunAtLoad` receipt. Verify *both* journals and their checkpoints; ensure no change to E1 `ProgramArguments`, governor or Wolfram push agent. **Do not** claim hourly scheduling PASS until the new shadow service completes a later natural unattended run. Use distinct `sampled_at` timestamps, not just 2 `RunAtLoad` invocations. Check disk usage remains bounded. No hourly LLM model or Work task.
6. A failure in the shadow agent should be isolated: `launchctl bootout gui/$(id -u) ...host-shadow.plist` stops only the new agent. Preserve both journals and receipts. Do not delete/alter E1 history; do not silently drop or rewrite shadow corrupt data. Never point old E1 reader at the shadow root.

### If arbitrary code or path differs from the reviewed commit

Fail closed as `DEPLOY_BLOCKED_SOURCE_DRIFT`. Do not automatically hot-replace it. The staging receipt did not authenticate any source code on Wolfram. That is separate.

## Wolfram actual collector source escrow (separate path, no public upload)

1. On Wolfram (local Codex), inspect actual loaded `com.chitakasha.token-governor-push` job and hash `$HOME/token-governor/push_first_collector.py` **without changing running files**. Expected SHA256: `a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81`.
2. Run local `source_attest.py`. The scanner is conservative and **cannot certify absence of secrets**, even when it returns zero matches. Entire source requires manual private review. Never put the raw source, credentials, home path or debug output into a public GitHub Issue, ChatGPT answer or attached logs.
3. Using the established Wolfram-initiated authenticated outbound SSH with `BatchMode=yes`, `StrictHostKeyChecking=yes`, `ForwardAgent=no`, deliver exactly one file into a private Darwin escrow with mode `0600` under a `0700` directory. The receiver must not print source. Independently compare SHA-256 on both ends. Existing SSH host-key trust must hold; do not relax it. Prefer a unique file name and exclusively created destination to prevent overwriting an earlier escrow copy.
4. Do not auto-commit original source anywhere, including private Forgejo. After secrets review, if canonical private Forgejo read/write access is verified, create a **review branch**, explicit manifest and redaction evidence. If unavailable, retain only private local escrow plus sanitized receipt and mark `PUBLISH_BLOCKED`.
5. No migration of Wolfram collector to `push_quota.py`; no additional launchd on Wolfram until a separate request.

## Acceptance receipts

- `DP01B_SHADOW_ACCEPTANCE_RECEIPT/v1`: exact commit/hash, E1 tip/checkpoint before/after (acknowledge natural independent E1 append), E2 tip/checkpoint, 55+24 fixture tests, one real disposable host snapshot, then fresh shadow receipt and after-hour natural run, source statuses, no Work jobs, no auth changes.
- `WOLFRAM_SOURCE_ESCROW_RECEIPT/v1`: true loaded runtime SHA, two-sided digest match, source-scanner flags **without content**, verified destination privacy, unpublished/unmerged status.

**Success means E1 remains compatible and operating, E2 shadow starts independently, and source escrow is recorded accurately.** Neither `MIN-51 Done` nor `#511 Done` should be inferred from staging alone; quotas remain `UNVERIFIED_FOR_WORK`.