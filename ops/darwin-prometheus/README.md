# DP-01 — Darwin Prometheus Event Ledger / v0.1

**Status:** tested in isolated assistant container; **not installed on Darwin**. Tracking: [MIN-44](https://linear.app/mindrock/issue/MIN-44/dp-01-append-only-ledger-provenance-and-low-cost-host-collectors) and [GitHub #511](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511).

## Architecture

```
Wolfram launchd -> CodexBar probe -> sanitized sample -> outbound SSH
                                                       |
                                                       v
Darwin governor.py ingest -> SQLite (existing pilot, do not modify)
                                                       |
                                        read-only DP-01 reconcile (hourly)
                                                       |
                              private UTC-daily JSONL hash-chain (canonical)
                                     /                            \
                         checkpoint digest              rebuildable SQLite view
```

The new collector is **observer-only**. It never triggers `probe`, changes Token Governor's SQLite, contacts Work/GitHub, sends credentials, or runs an AI model. Existing push-first #511 stays operational and must **not** be replaced merely to install this ledger.

**Data types:** `quota.observation` (weekly/session aggregate percentages, source and time), `quota.alert` (kind and delivery; alert message omitted), `host.health` (load averages and disk capacity without paths, process listings, hostnames, or identities). Privacy filter rejects other fields and unsafe source strings. Work remains `UNATTRIBUTED_CLOUD_WORK`; Codex quota is `UNVERIFIED_FOR_WORK` until an independent ChatGPT Usage check.

**Provenance:** Every new event is `SOURCE_READ_LOCAL` from a locally readable Governor SQLite or Darwin OS. `READ_BLOCKED` is reported if the source is unavailable; unknown does **not** mean zero usage or success.

## Local read-only trial on Darwin (before enabling launchd)

In the existing authorized Darwin Codex shell, check the source files in a **new** GitHub review branch, copy these four files to `~/darwin-prometheus` and run:

```sh
set -eu
umask 077
mkdir -p "$HOME/darwin-prometheus"
python3 -m unittest discover -s "$HOME/darwin-prometheus" -p 'test_*.py' -v
python3 "$HOME/darwin-prometheus/event_ledger.py" verify
python3 "$HOME/darwin-prometheus/event_ledger.py" sync-governor
python3 "$HOME/darwin-prometheus/event_ledger.py" project
python3 "$HOME/darwin-prometheus/event_ledger.py" checkpoint
python3 "$HOME/darwin-prometheus/event_ledger.py" verify
python3 "$HOME/darwin-prometheus/run_cycle.py"
```

The **first** sync is expected to import the earlier real quota observations from Darwin's existing `~/.local/share/token-governor/observations.sqlite3` (count may be 1 or more). It MUST never add fixture data into this production database.

Private disk layout:

```
~/.local/share/darwin-prometheus/
  .writer.lock                (flock only)
  journal/2026-10-13.jsonl    (strict append-only, SHA-256 chained across UTC files)
  checkpoints/000000000001-<tip>.json (immutable checkpoint)
  ledger.sqlite3              (rebuildable, replaceable projection)
```

Each journal JSONL record embeds a hash of all other fields including the previous record's hash, deterministic event ID, typed sanitized payload and provenance. Checkpoints detect truncation/rewriting *relative to preserved local checkpoints*. **Important limitation:** This is tamper-evident, not tamper-proof against an attacker with full user write access; export/anchor checkpoint SHA-256 in a separately controlled store (Forgejo/Arweave) after review. Do not publish quota payloads or private journals.

The journal deliberately refuses automatic repair of torn writes, bad schema, altered field values, duplicate IDs with conflicting payload, or clock rollback into a prior UTC segment. Keep a copy and investigate any `INVALID`. Never silently truncate, overwrite or rebuild the primary JSONL. `project` recreates only the derived SQLite index.

## Optional ongoing launchd installation — Darwin **only**

After successful read-only dry-run and careful review of existing LaunchAgents:

```sh
python3 "$HOME/darwin-prometheus/install_ledger_launchagent.py"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.chitakasha.darwin-prometheus-ledger.plist"
launchctl kickstart -k "gui/$(id -u)/org.chitakasha.darwin-prometheus-ledger"
launchctl print "gui/$(id -u)/org.chitakasha.darwin-prometheus-ledger"
tail -n 10 "$HOME/Library/Logs/darwin-prometheus-ledger.log"
```

Runs on login and every 3600 seconds while Darwin's user domain is running. `launchd` does **not** guarantee a sample during sleep, nor does `StartInterval` prove a fresh CodexBar update. Exit 0 means local journal reconciliation, host sample, projection and checkpoint succeeded. If the Governor DB is unreadable, exit 3 / `PARTIAL` with `READ_BLOCKED`; no quota sample is invented.

To disable without destroying evidence: `launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.chitakasha.darwin-prometheus-ledger.plist"`.

## Acceptance checklist / deployment receipt

1. Darwin real Governor DB read-only sync (`SYNCED`) plus correct observation count, no data leakage.
2. `verify` journal chain, `project` rebuild, immutable checkpoint creation; record SHA-256 of checkpoint.
3. Tests run on **Darwin** with exit code 0, plus current unit tests in isolated environment.
4. At least **two distinct** real `observed_at` timestamps from CodexBar arriving in Darwin's Governor DB, separated in time; duplicates do not count.
5. Verify active Darwin LaunchAgent after at least one *later* unattended run, not only `RunAtLoad`.
6. Confirm this ledger leaves Wolfram push agent (`com.chitakasha.token-governor-push`) unchanged; no sudo, TCC, DNS, inbound SSH or model changes.
7. Report disk/memory footprint; remember that a 503 with no fresh sample is `UNAVAILABLE` rather than zero consumption.
8. Reconcile any Cloud Work quota using independent ChatGPT Usage before treating these percentages as Work quota authority.

## Deliberately deferred for DP-01 E2

CPU-percent/sample over time, swap, service uptime, tailscale and Ollama health, Forgejo, rotating storage budgets, permissions/ownership audit, history backfill >80 minutes, signature-backed off-host checkpoint anchor and published official PR require separate acceptance. This first slice consumes tiny CPU and disk and provides a testable append-only spine without disrupting the proven #511 pipeline.