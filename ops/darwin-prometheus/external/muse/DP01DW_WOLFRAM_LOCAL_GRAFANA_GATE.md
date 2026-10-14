# DP-01D-W — Wolfram-Hosted Grafana / Prometheus: host capacity & safe pilot

Tracking: [MIN-55](https://linear.app/mindrock/issue/MIN-55/dp-01d-w-wolfram-localhost-grafana-and-prometheus-pilot), parent [MIN-53](https://linear.app/mindrock/issue/MIN-53/dp-01d-sovereign-muse-metrics-and-grafana-visualization).

**Status: PREPARED; no software installed, no new listening port, no local Wolfram probes by this ChatGPT session.** Minutta is physically disassembled; Minutta capability work MIN-54 is HARDWARE_BLOCKED until it is powered on and hardware validated.

## Why Wolfram is workable, pending measurement

- macOS Grafana OSS supports native Homebrew and standalone macOS installation (official guide https://grafana.com/docs/grafana/latest/setup-grafana/installation/mac/). Prometheus offers prebuilt binaries (https://prometheus.io/docs/prometheus/latest/installation/). Pin versions and verify Mac OS / CPU compatibility.
- Wolfram already uses Ollama and Colima/PentAGI, with limited 16 GiB memory; do not assume currently unused RAM. Avoid adding another container VM by default.
- Darwin already produces normalized private Muse `muse_telemetry.prom` (29 lines, 1697 bytes, reported SHA-256 `166a16120573c9616c5fa4bc446f2e38f639d04d78914121b03f6cbeadb162c4`) from first preliminary Muse report.
- Wolfram-originated strict authenticated SSH to Darwin is already proven for exact-file transfers. **Only the sanitized .prom may be transferred for monitoring**, not E1/shadow/Muse raw ledgers or original agent JSON, and only with existing authorized account access.
- Grafana alone cannot consume a bare .prom; use a local exporter endpoint (127.0.0.1) → local Prometheus scrape/storage → Grafana Prometheus datasource, all local-only.

## Gate A — inspect Wolfram READ-ONLY (run on Wolfram as normal user)

```bash
umask 077
sw_vers
uname -sm
sysctl -n hw.memsize
vm_stat
memory_pressure
sysctl vm.swapusage
df -Pk -- "$HOME"
uptime
for binary in brew grafana prometheus promtool python3 ssh; do
  if command -v "$binary" >/dev/null 2>&1; then
    printf '%s PRESENT\n' "$binary"
  else
    printf '%s ABSENT\n' "$binary"
  fi
done
if command -v colima >/dev/null 2>&1; then colima list; fi
if command -v ollama >/dev/null 2>&1; then ollama ps; fi
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null || true
```

Before sharing receipt, REDACT usernames, personal paths, tokens and unrelated process arguments. `memory_pressure` percentages and `vm_stat free` are not the same measurement. Recheck under normal Ollama/Colima load and note swap *growth*, not merely current swap number. Report READ_BLOCKED where APIs require elevated permissions: no sudo.

Gate A decision must say `CAPACITY_PASS` or `CAPACITY_BLOCKED`; do not install until capacity is acceptable and affected workloads inventoried. If genuinely low memory, stop and propose even leaner native alternatives rather than interrupt Ollama/Colima.

## Gate B — after CAPACITY_PASS, reversible LOCALHOST-only pilot

1. Check approved macOS-version and architecture-specific native Grafana OSS and Prometheus build artifacts, vendor hashes/signatures, provenance and licensing. Avoid unpinned Homebrew `brew update` touching unrelated packages or auto-start of services. No sudo. Installation only under user writable directory or approved Homebrew prefix; no editing existing default Grafana instance.
2. Before allocating any port, verify port availability. Candidate LOCALHOST addresses (not guarantees): exporter `127.0.0.1:9108`, Prometheus `127.0.0.1:9098`, Grafana `127.0.0.1:3300`. Do NOT listen on 0.0.0.0 or Tailnet; no VPN, firewall or SSH listener edits.
3. With Wolfram -> Darwin existing strict SSH (`BatchMode=yes`, `StrictHostKeyChecking=yes`), first check remote user is authorized to read the 0600 sanitized Muse textfile. If not, stop `READ_BLOCKED` — do not chmod. Stage only the sanitized bytes in Wolfram user-private `0700/0600` location; verify source and receiver SHA-256, allowlist `simsim_muse_*` metrics, and record generated_at.
4. Exporter must run as same unprivileged user and serve fixed vetted .prom file **read-only** from loopback. No arbitrary file path/query, no remote execution or egress; client request timeout and file-size ceiling.
5. Native Prometheus locally scrapes exporter `/metrics` and is explicitly bounded (propose `--storage.tsdb.retention.time=7d`, `--storage.tsdb.retention.size=1GB`, binding to 127.0.0.1 and local TSDB directory). These are proposed limits only; confirm exact flags with installed version. Do not mark scrape as PASS until actual `GET /api/v1/query?query=simsim_muse_daily_runs` returns a matching value. The first Muse report states 86 runs and PRELIMINARY.
6. Grafana uses **real** existing/promised locally configured Prometheus datasource and dashboard draft at `ops/darwin-prometheus/external/muse/grafana_dashboard.json`. Do not auto-publish Grafana UI or use default credentials unattended; keep `127.0.0.1` bind and secure admin credentials locally. Validate a panel returns the Muse report timestamp and the weekly 7% **Muse** quota (not ChatGPT Work).
7. Monitor resource footprint while all three pilot processes run. Preserve original E1/DP01B/Muse/Governor on both hosts and verify that increasing Grafana load does not affect SSH pushes. No LaunchAgent persistence yet; separate gate for unattended use.
8. Rollback is stopping **only** new pilot processes and removing only the dedicated pilot data/config. Never delete or modify old ledgers.

## Evidence hierarchy

- SOURCE_READ: exact Drive/Muse textfile content and source bytes, with SHA-256 verified.
- EXTERNAL_AGENT_TESTIMONY: Muse's self-reported 86/86 runs and quota, not proof the jobs executed.
- `PRELIMINARY`: source generated 2026-10-13 20:20 PDT. A real nightly 23:30 delivery not verified; don't enable hourly snapshots that mask stale source as fresh.
- UI_READY: actual Grafana dashboard populated by **real** local Prometheus query; do not infer from local file existence.
- DP-02 Work quota remains UNVERIFIED_FOR_WORK.

## Acceptance receipts

- `WOLFRAM_GRAFANA_CAPABILITY_RECEIPT/v1`: timestamp, macOS version and architecture, memory pressure and swap *delta*, disk, existing listener inventory (sanitized), installed binaries and exact versions, safe or blocked verdict, impact budget, untouched E1/DP01B/Governor.
- `WOLFRAM_GRAFANA_PILOT_RECEIPT/v1`: pinned binary checks, sanitized metrics SHA on both hosts, actual exporter scrape success, Prometheus query response, Grafana datasource/panel proof, loopback binding, resource envelope, rollback plan. If unable to start, `GRAFANA_PENDING` with exact blocker.

## Minutta hardware

Minutta is currently disassembled, so MIN-54 on-host capacity cannot proceed. A bootable MemTest86/Memtest86+ USB is a RAM diagnostic medium that normally relies on a functioning motherboard UEFI/BIOS; it is not a standalone custom BIOS. BIOS recovery/flashing may need board-specific vendor procedures and exact revision verification. Keep these as a separate hardware repair task.
