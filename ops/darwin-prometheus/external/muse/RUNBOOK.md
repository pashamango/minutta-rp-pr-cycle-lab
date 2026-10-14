# SIMSIM / Darwin Prometheus — Muse Independent Telemetry Bridge v0.1

**2026-10-14 status:** DARWIN_MUSE_INGEST_HOST_PASS (reported by local Codex); 18/18 host tests, 1 real Muse report + 5 job aggregates, immutable ledger verified, duplicate rejected, private Prometheus textfile exported. **Grafana and Prometheus runtime remain GRAFANA_PENDING; nightly 23:30 recurrence unverified.** All code/tests/fixture/dashboard committed on this review branch. The pinned source commit is `d5e5c4ead524de0851b5e750853b8667baf4adc6`. The supplementary `RETRY_AFTER_RELAY.md` was added later (commit `153706168d34f5896ccf8f78bf7c3f2e1b9dea03`) and therefore does **not** exist at the pinned source commit. Source evidence is user-reported host receipt recorded at https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511#issuecomment-6163442647.

## Confirmed Drive source

- Muse folder ID `1QHNqoJXgpwWuU1HDr7ijbrQoEvZAgSWy`.
- **Specific pinned** telemetry child folder ID `1LVbeYesirNXEwTAKHg6JfCPNg1tYNNyV` (`/Muse/telemetry`). Do not use a generic `name=telemetry` search: Drive has many such folders.
- Test 2026-10-13 JSON file ID `17GWng5rgNxerHZbl3N9658NSzEoqZTI3`; Markdown companion ID `12w4YVMUs7GyeWJ7xxrPiQm-jSRA7GPg-`.
- Connector read of JSON source verified. Raw JSON SHA-256 from the original downloaded Drive object: `95562d42cc6c002074bc4314c7e683863de73320d1531eabb8d4a389d717edbb`.
- The report has `generated_at=2026-10-13T20:20:00-07:00` (a preliminary report, **not** the agreed 23:30 batch). Claims 86 total runs = 86 success + 0 failure, from five jobs; weekly subscription usage 7%, session context usage 33% (different accounting windows). Claims zero anomalies but error registry was initialized that same day. The source embeds `pending_sync`, but the file has since **actually appeared in Drive**; treat pending_sync as historical text, not current Drive state.

## Trust and claim discipline

- `SOURCE_READ`: independently authenticated Google Drive connector observed a file and read its JSON bytes. This does not authenticate Muse as the author, nor prove that its cron jobs really ran.
- `EXTERNAL_AGENT_TESTIMONY`: all numerical fields are claims in that JSON. We only cross-check internal arithmetic, timestamps and schema; we cannot inspect Muse's private scheduler from Darwin.
- `PRELIMINARY` if report generated before 23:30 **America/Los_Angeles** on its report date; `NIGHTLY_CUTOFF` if generated at/after 23:30 but still not an entire 00:00–23:59 day. Later verification can add producer signatures and independent evidence receipts.
- No external source is allowed to assert `SOURCE_READ_LOCAL`, `quota.observation` from CodexBar, or any sovereign owner permissions. No prompt or code from Muse telemetry is interpreted/executed.
- Only normalized aggregates enter dedicated Muse ledger; private free-text, names, content references and folder paths are not written to the event payload. Source `drive_file_id` and raw hash are stored in private ledger for provenance only, not Prometheus.

## Topology — **no direct ChatGPT connector assumption on Darwin**

```text
Muse scheduled exporter (claimed nightly 23:30 PDT)
    -> Google Drive /Muse/telemetry/<YYYY-MM-DD>.json (pinned folder ID)
    -> approved local Google Drive sync on Wolfram (verify mounted folder)
    -> SHA-256 + one-file **Wolfram-originated** authenticated strict outbound SSH
    -> private 0700 inbound staging on Darwin (not a new TCP listener)
    -> python3 muse_bridge.py ingest --input STAGED_FILE --drive-file-id ID
    -> ~/.local/share/darwin-prometheus-muse/{muse.jsonl,muse.sqlite3}
    -> muse_bridge.py export -> private node_exporter textfile .prom
    -> existing Prometheus scraper (ONLY if actually installed) -> Grafana dashboard
```

**Do not invent Darwin access to the in-Chat Google Drive connector.** On Wolfram check whether the actual pinned Muse telemetry folder is locally synced. If not, record `READ_BLOCKED_SOURCE_SYNC` and investigate a permitted, scoped Drive API or other documented authorized transport. No browser-cookie extraction, guessing access tokens, opening external ports or new sudo.

## Stage and acceptance (Darwin Codex)

1. Review the SHA of source commit, install `muse_bridge.py` and optional `grafana_dashboard.json` in a private staging directory (0700). Use actual Python 3.12+ or Python with `zoneinfo` support. Do not overwrite Event Ledger E1, DP01B shadow or Wolfram collector.
2. Run `python3 -m unittest discover -s . -p test_muse_bridge.py -v` (18 tests) and `python3 muse_bridge.py --help`. Check real `2026-10-13.json` only from a **verified authorized mirror**, and SHA-256 match to the known source object. Keep it private.
3. Use `python3 muse_bridge.py --root "$HOME/.local/share/darwin-prometheus-muse" ingest --input /PRIVATE/STAGED/2026-10-13.json --drive-file-id 17GWng5rgNxerHZbl3N9658NSzEoqZTI3`. Then `verify`, `project`, `export --output /PRIVATE/CONFIGURED_TEXTFILE_DIR/muse_telemetry.prom`.
4. Re-ingest identical file to confirm `DUPLICATE` with no new append. A future rewritten same date with different byte hash generates a **new immutable revision**, without deleting or replacing the earlier observation.
5. Verify the source never influences the old E1 or DP01B shadow journal. Record E1 chain prefix/hash and the new Muse journal tip. Restrict Muse ledger permissions to owner (root dir 0700, files 0600); do not pass private home paths/raw content into GitHub Issue comments.
6. Check whether an authorized local node_exporter **textfile collector and Prometheus datasource** actually exist. If absent, leave just the .prom output and Grafana JSON draft; DO NOT claim dashboard is live or launch new services without reviewing permissions and ports.
7. The midnight/23:30 cadence is user-reported. Confirm a *later* provider file with generated_at >= 23:30 local and two separate daily file IDs/digests before asserting recurring production exporter health. A raw zero-error count is not independent incident verification.

## Grafana

`grafana_dashboard.json` uses a Prometheus datasource (`DS_PROMETHEUS` import-time variable) and series `simsim_muse_*`. It shows Muse's weekly used quota, sample age, runs, error claims, jobs and session context separately. The red banner/title explains **external testimony**. No Grafana datasource, Prometheus or node_exporter installation is claimed. A textfile only becomes a Grafana source after an existing authorized exporter/scraper reads it.

## Wolfram source escrow remains independent

The live Wolfram transport is still `push_first_collector.py` SHA-256 `a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81`. Before any private escrow transfer: re-attest local file, scan locally for secrets, human-reviewed authorization, transmit exactly one file via pre-existing Wolfram->Darwin SSH, re-hash on Darwin and keep in private nonpublic storage. No hot-swap with `push_quota.py`. **Escrow HOST_PASS** per Wolfram/Darwin Codex report (SHA-256 matched on Darwin, scanner PASS, private 0600 copy); this is not permission to publish or merge the source. Private Forgejo review remains a separate gate in MIN-51.

## Fail-closed states

`SOURCE_READ` vs `READ_BLOCKED`, `SCHEMA_INVALID`, `DUPLICATE`, `PRELIMINARY`, `NIGHTLY_CUTOFF`, `EXTERNAL_AGENT_TESTIMONY`, `EXPORT_READY`, `GRAFANA_UNVERIFIED` must stay distinct. Never turn absent or stale telemetry into zero, successful task completion, verified Work quota, or agent authority.