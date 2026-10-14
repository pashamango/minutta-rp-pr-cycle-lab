# DP-01C — Darwin continuation after PASS relay / BLOCKED archive

**Status**: input-file transport PASS (reported by local Wolfram/Darwin Codex); Muse ingestion on Darwin was BLOCKED solely because previous ZIP was not accessible from the host. **GitHub source now available.** Do NOT use stale docs that assumed only ZIP delivery.

**Pinned reviewed source**: GitHub commit `d5e5c4ead524de0851b5e750853b8667baf4adc6` on branch `agent/darwin-prometheus/dp-01c-muse-bridge-20261013` under `ops/darwin-prometheus/external/muse/`. Four newly committed files: `muse_bridge.py`, `test_muse_bridge.py`, `grafana_dashboard.json`, `fixture_synthetic.json`, plus existing runbook and handoff.

**Proven facts from previous host receipts (user-reported; local JSON not independently read by ChatGPT):**
- Muse Drive folder ID `1LVbeYesirNXEwTAKHg6JfCPNg1tYNNyV`; test file 2026-10-13.json locally synchronized on Wolfram.
- SHA-256 `95562d42cc6c002074bc4314c7e683863de73320d1531eabb8d4a389d717edbb` matched both Wolfram and Darwin, file already in private Darwin staging with 0600 permissions.
- Wolfram real `push_first_collector.py` SHA-256 `a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81`, scanner PASS and **private Darwin escrow DONE**. Do not redo or publish the unreviewed original. Remaining: optional private Forgejo review and Wolfram host adapter, independent of Muse ingest.
- No existing Prometheus scraper, node_exporter textfile collector or Grafana datasource was found: `GRAFANA_PENDING`. Do not install or start new network services or claim that `.prom` is already scraped.

## Stage exact code, never touch E1/shadow

On Darwin, under an already authenticated, authorized checkout of `pashamango/minutta-rp-pr-cycle-lab`, verify `git cat-file -t d5e5c4ead524de0851b5e750853b8667baf4adc6` reports `commit`. If missing, fetch only the review branch using the existing approved GitHub auth method; fail with `SOURCE_READ_BLOCKED` rather than bypassing auth.

Set `umask 077`; use a fresh user-owned **0700** staging dir with no symlinks. For the four reviewed files, extract from the pinned commit with `git show d5e5c4ead524de0851b5e750853b8667baf4adc6:ops/darwin-prometheus/external/muse/FILE > STAGING/FILE`. Do NOT checkout, overwrite, merge or alter the active E1 or DP-01B shadow trees.

Run:
1. `python3 -m unittest discover -s STAGING -p test_muse_bridge.py -v` — require all **18/18 PASS**.
2. `python3 STAGING/muse_bridge.py --help` — require exit0.
3. Confirm the existing **Darwin-staged** Muse JSON SHA-256 is exactly `95562d42cc6c002074bc4314c7e683863de73320d1531eabb8d4a389d717edbb`. Keep it private. Do not ask Muse to resend or modify already working relay.
4. Pick an isolated user-owned root `~/.local/share/darwin-prometheus-muse`; verify it is not an E1/shadow directory or symlink. Use `python3 STAGING/muse_bridge.py --root ROOT ingest --input VERIFIED_JSON --drive-file-id 17GWng5rgNxerHZbl3N9658NSzEoqZTI3`. Expect `INGESTED` once, then `DUPLICATE` for identical file with same chain tip, not a second event.
5. Use `verify`, `project`, `verify`, and `export --output ROOT/muse_telemetry.prom`. Expected `PRELIMINARY`, **one** genuine Muse report and five job aggregates. The `.prom` file is local private output, NOT yet live Prometheus/Grafana.
6. Independently verify legacy E1 and DP-01B shadow ledger with their own readers and record prior prefix/tips (they can naturally advance). No writing to either.
7. Issue sanitized `MUSE_EXTERNAL_TELEMETRY_ACCEPTANCE_RECEIPT/v2` with code commit/blob hashes, source JSON SHA, command result statuses, source confidence EXTERNAL_AGENT_TESTIMONY, new Muse chain tip, event/job counts, owner-only permissions, E1 and shadow integrity, and honest `GRAFANA_PENDING`.
8. Do not schedule nightly automatic imports until a later **23:30** Muse report is actually observed and its digest/freshness checked. Generated time 2026-10-13 20:20 PDT is an early PRELIMINARY test report, not evidence of 23:30 recurrence.

**Assistant isolated-container checks 2026-10-13**: pinned source 18/18 unit tests PASS. Actual Muse JSON in separate temporary ledger gave INGESTED → VERIFIED → PROJECTED → private .prom EXPORTED → identical replay DUPLICATE. Source SHA verified. **Not a Darwin host test**.

**Security**: no external code execution from Muse data, no raw report upload to GitHub, no OAuth tokens in chat, no Work/model/effort change, no inbound Wolfram SSH, no new ports, no protected main merge.
