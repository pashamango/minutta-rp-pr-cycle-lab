# DP-01E — Minutta Observability Host / Authenticated Relay Capability Gate

**Issue:** [MIN-54](https://linear.app/mindrock/issue/MIN-54/dp-01e-minutta-capacity-and-authenticated-observability-transport-gate). **Mode:** READ-ONLY capability audit. **No deployment, no sudo, no Work, no model changes, no network/SSH/Tailscale changes.**

## Evidence already available (host-reported)

Darwin: macOS 12.7.6 x86_64, 16 GiB, 1.37 GiB vm_stat free, `memory_pressure` 87% free (NOT directly comparable), swap 0.00M, 60.2 GiB disk free, load 1.30/1.20/1.15 on 4 CPUs. No prometheus/promtool/node_exporter/Grafana binary detected. Existing Forgejo only `127.0.0.1:3001` on this port (other loopback 3011,3013,51578 observed). Muse `muse_telemetry.prom` is 29 lines, SHA256 `166a16120573c9616c5fa4bc446f2e38f639d04d78914121b03f6cbeadb162c4`, access 0600 beneath 0700. It is NOT scraped; no Grafana datasource. On-host receipt: [GH #511](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/511#issuecomment-6163712168).

The Muse source is preliminary (generated 2026-10-13 at 20:20 PDT), `EXTERNAL_AGENT_TESTIMONY`. Latest independent Drive list showed only original `2026-10-13.json` + `.md`, NOT a later nightly 23:30 report. Freshness is separate MIN-52.

Minutta: Ubuntu server, Ollama/NVIDIA RTX 3090 context reported previously. Exact free resources, authenticated route and installed software are **unverified**. Do NOT claim otherwise.

## Minutta Codex local READ-ONLY commands (sanitize before publishing results)

Run under the current unprivileged user on Minutta:

```bash
set -u
uname -srm
cat /etc/os-release | grep -E '^(NAME|VERSION_ID|PRETTY_NAME)='
getconf _NPROCESSORS_ONLN
cat /proc/loadavg
grep -E '^(MemTotal|MemAvailable|SwapTotal|SwapFree):' /proc/meminfo
cat /proc/pressure/memory 2>/dev/null || true
df -Pk -- "$HOME"
for x in prometheus promtool grafana grafana-server node_exporter docker podman ollama nvidia-smi ssh; do
  command -v "$x" >/dev/null 2>&1 && printf '%s: PRESENT\n' "$x" || printf '%s: ABSENT\n' "$x"
done
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=memory.total,memory.used,utilization.gpu --format=csv,noheader 2>/dev/null || true
fi
ss -ltnH 2>/dev/null || true
systemctl --user list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | sed -E 's/[[:space:]]+/ /g' || true
```

Do not dump process command lines, OAuth tokens, environment, journal files, SSH private keys, `/etc/shadow`, Tailscale peer inventory, usernames, private paths or any secrets. Capture relevant service inventory in the **private local receipt only** and publish sanitized aggregate details.

## Specific required answers

1. How much actual `MemAvailable`, CPU/disk/swap headroom exists with Ollama under representative idle load? Are there bursts? Is RTX/Ollama memory pressure relevant to additional services?
2. Which binaries are installed, what versions, and where is user-space installation allowed without sudo? Do **not** install anything. Do not assume modern Grafana is compatible with older Darwin, which is one reason to evaluate Linux Minutta.
3. What existing listener and port allocations would conflict with local-only exporters (default ports 3000, 9090, 9100 may collide; no binds requested yet)?
4. Which approved authenticated transport *actually exists* between Darwin and Minutta? The only previously verified host path is **Wolfram outbound SSH to Darwin**, not Darwin→Minutta. If no such Minutta path is proven, mark `AUTH_TRANSPORT_UNVERIFIED`, rather than guessing hostnames or enabling any service.
5. Confirm the least-privilege design: Darwin reads its 0600 `.prom` and transmits **sanitized exposition only**, with source SHA256, generated_at, sender hash, receiver hash and receipt. Receiver stores private copy under user-only rights; no remote read access to Darwin's E1, DP-01B shadow or Muse ledger. If route not proven, propose options for a separate approval; no experimental port opening, no unauthenticated HTTP Pushgateway.
6. Is Minutta safe for short retention (begin with a proposed 7-day budget, not a configured fact) and loopback-only Grafana/Prometheus? Consider Ollama load spikes, total RAM, storage wear, cost and documented rollback.

## Possible architecture — proposal, NOT deployed

```text
Muse -> pinned Google Drive -> Wolfram local sync -> existing outbound strict SSH -> Darwin
Darwin private Muse Ledger (immutable, owner only) -> sanitized muse_telemetry.prom
  -> proposed authenticated transfer (direction NOT YET VERIFIED) -> Minutta private metrics staging
  -> proposed user-level textfile-compatible exporter -> localhost Prometheus -> localhost Grafana
  -> separately reviewed authenticated viewing route
```

Prometheus normally scrapes a metrics HTTP endpoint, **not** a file over the network; a 0600 `.prom` file is not externally readable. An exporter must be chosen and actually confirmed compatible. No new listeners, daemons, schedules, downloads or Git/Forgejo writes on either physical host at this stage.

## Acceptance evidence

Return **`MINUTTA_OBSERVABILITY_CAPABILITY_RECEIPT/v1`** with timestamp; read-only command receipts; CPU/RAM/swap/disk; ports/binaries and compatibility; proposed resource cap and retention; `AUTH_TRANSPORT_VERIFIED` or `UNVERIFIED` plus exact evidence; recommended placement Darwin vs Minutta, quantified risk; and precise subsequent pilot authorization gate.

Mark `PASS` for *capability assessment only*, **not** Prometheus/Grafana installation or source transport. Existing DP-01 E1 and DP-01B shadow continue untouched. Work quota `UNVERIFIED_FOR_WORK`; Muse nightly recurrence `UNVERIFIED`.
