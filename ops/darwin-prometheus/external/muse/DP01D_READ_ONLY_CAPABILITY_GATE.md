# DP-01D — Read-only Grafana/Prometheus Capability Gate

Tracking: [MIN-53](https://linear.app/mindrock/issue/MIN-53/dp-01d-sovereign-muse-metrics-and-grafana-visualization). **Not deployed. No live Grafana datasource or Prometheus scrape has been verified.**

## Source truth (2026-10-14)

DP-01C Muse ingestion was reported PASS by local Darwin Codex: code commit `d5e5c4ead524de0851b5e750853b8667baf4adc6`, source JSON SHA-256 `95562d42cc6c002074bc4314c7e683863de73320d1531eabb8d4a389d717edbb`, private Muse journal one event / five job rows, projected / verified, `muse_telemetry.prom` exported (1697 bytes). Existing DP-01 E1 and DP-01B shadow stayed independent. Original host receipt inaccessible in this ChatGPT session. Evidence: [GitHub #511](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511#issuecomment-6163442647).

The `.prom` textfile **is not a Prometheus datasource** by itself. An authorized exporter must expose those metrics, Prometheus must scrape that exporter, and Grafana must be configured to query Prometheus. None of those three connections is confirmed on Darwin. **Never claim LIVE** from a successful file export alone.

## Only authorized next action: host read-only diagnostics

Run in local **Darwin Codex** terminal with no elevation:

1. Record macOS version, architecture, memory size and free disk via read-only `uname`, `sw_vers`, `sysctl -n hw.memsize`, `df -Pk`. Report rough resource headroom only, not personal paths/process command lines.
2. Determine availability of `prometheus`, `node_exporter`, `grafana` or other already approved exporters using `command -v` and local known directories. Do not install, download or start software during this phase.
3. Check loopback listeners relevant to existing services using read-only `lsof -nP -iTCP -sTCP:LISTEN`, but summarize only the port/bind scope and program type, not user identities, authentication material or unrelated processes. Treat permission errors as `READ_BLOCKED`.
4. Re-hash the actual private `muse_telemetry.prom`, validate Prometheus text exposition syntax and ensure no raw Muse JSON, conversations, credentials or PII appear. Confirm `simsim_muse_*` metrics are labelled **EXTERNAL_AGENT_TESTIMONY** in the dashboard text. A metric named `daily_runs` is a **gauge** of the last agent report, not a monotonically increasing counter.
5. Confirm the `.prom` path is inside an owner-only 0700 directory, file 0600. If a later exporter needs access, run it under the **same unprivileged user**, rather than weakening permissions or changing the working Muse ledger.

Return `DP01D_CAPABILITY_RECEIPT/v1`: actual source reads, available binaries, RAM/disk baseline, localhost-only networking feasibility, measured or estimated resource overhead, source file SHA, `DATASOURCE_PRESENT` or `GRAFANA_PENDING`, and proposed bounded next change.

## Separate future Gate: actual local-only visualization

ONLY after verifying platform support, available RAM/disk and safe bind address:

- Prefer user-level processes, pinned authenticated source, fixed minimal retention/storage budget, and localhost-only listeners. Avoid 3001 (existing Forgejo).
- A node_exporter textfile collector is one possible route, **only if** a macOS-compatible binary and collector availability are verified. The exporter must run as a user authorized to read the private `.prom` file. A different compatible authenticated exporter is acceptable if verified.
- Verify a real Prometheus query for `simsim_muse_daily_runs` and `simsim_muse_report_generated_timestamp_seconds`; these must correspond to the last imported Muse report rather than invented synthetic metrics.
- Import `grafana_dashboard.json` using a real local Prometheus datasource UID; verify the panel query returns actual data, and include a local screenshot or redacted receipt if available.
- If old Darwin cannot safely accommodate the footprint, leave `GRAFANA_PENDING` and propose relocating the visualization to a sovereign machine **after** verifying its permissions and network plan. Do not open new Tailnet/internet listeners by assumption.

## Muse 23:30 daily report gate (separate from Grafana)

The pinned Google Drive folder `1LVbeYesirNXEwTAKHg6JfCPNg1tYNNyV` still exposed only the initial 2026-10-13 preliminary JSON+MD at the 2026-10-14 ~00:39 PDT connector check. A later report is **not yet observed**. Filename or Drive file ID **may be reused**: accept a new provider revision when full raw SHA-256 and `generated_at` differ, preserving both revisions. Require recorded local-time source timestamp and evidence of visibility/delivery before claiming a real nightly batch. Presence in Drive proves receipt of bytes, not independent proof of Muse's cron statistics.

**Invariants:** No changes to working E1, DP-01B, Governor, Wolfram collector, SSH/Tailscale, schedules, model/effort, or protected main in read-only gate. No automatic privileged/billable installation, no cloud Work and no public telemetry publication.
