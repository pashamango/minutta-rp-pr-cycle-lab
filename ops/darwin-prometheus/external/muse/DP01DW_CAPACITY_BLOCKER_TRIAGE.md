# DP-01D-W — Wolfram capacity and source-resolution triage

**Status:** `CAPACITY_BLOCKED / HOST_IDENTITY_UNVERIFIED / GRAFANA_NOT_INSTALLED`. This is a **read-only reconciliation plan**, not permission to install, clean caches, kill processes, change SSH, or adjust user services.

## Input: WOLFRAM_GRAFANA_CAPABILITY_RECEIPT/v1 (user-supplied)
- The receipt's `evidence.darwin` reports **arm64, macOS 26.6.2 (25G83), 16 GiB**, load 2.61/2.36/2.39, reported 41% memory free, 9.2 GiB swap total with **7.8 GiB used**, disk 55 GiB free. These match the reported **Wolfram** system class, **not** the known Intel Darwin (macOS 12.7.6, x86_64). The JSON field's label **does not establish host origin**. Confirm *which host ran the commands* from local terminal context before attributing measurements.
- Ollama localhost port 11434, no model loaded; Colima installed but stopped; Homebrew 6.0.22, Grafana and Prometheus absent, per receipt. No host changes.
- `wolfram_ssh` was probed against **Wolfram itself on TCP/22**, where inbound SSH is intentionally disabled. **This is not a test of the known allowed direction Wolfram → Darwin.** Do not change Remote Login, sshd, firewall, Tailscale, user SSH config or host keys to 'fix' it.
- Source repo branch `agent/darwin-prometheus/dp-01c-muse-bridge-20261013` and file `DP01DW_WOLFRAM_LOCAL_GRAFANA_GATE.md` **both readable to the ChatGPT authenticated GitHub connector** at HEAD `b56ef6f6b740ebcdf4ca6914313a1460aa7611a3`. Git blob SHA `cf717e00f140a82c6212046b36e446f0576c5842`. A raw GitHub URL returning 404 on the host is **HOST_SOURCE_READ_BLOCKED**, not evidence that the file does not exist; private repo authorization, wrong remote/branch, or URL construction must be investigated read-only. Do not bypass repo permissions or claim the host source read succeeded.

## Next gate: local read-only evidence on **Wolfram terminal only**

1. Locally establish the machine identity from *OS/architecture plus the currently signed-in host context*, but **redact hostnames, usernames, Tailnet IPs and home paths from GitHub/Linear receipts**. Report `HOST=WOLFRAM` only if matching the intended machine is positively established; otherwise `HOST_IDENTITY_UNVERIFIED`.
2. Re-read and compare `sysctl vm.swapusage`, `vm_stat` including pageouts, `memory_pressure`, active RAM; sample once more after a bounded 5–10 min under ordinary workload (no synthetic load), recording timestamps. Neither swap usage fraction nor a single percentage alone proves sustained memory pressure. Do not purge caches, reset Colima, kill apps, disable Ollama or force swap cleanup.
3. Inventory RAM-heavy *categories* only (Ollama, browser, Colima, code editors, etc.) with no private command-line flags or content. If swap continues growing or memory pressure / app lags rise, retain `CAPACITY_BLOCKED`. If stable, return `CAPACITY_ASSESSMENT_PENDING` with bounded pilot recommendation, **not automatic install**.
4. Inspect only an existing authorized local Git checkout using `git rev-parse --is-inside-work-tree`, `git show-ref` and `git cat-file -t b56ef6f6b740ebcdf4ca6914313a1460aa7611a3` (read-only). Do not `git fetch` unless the user has already authorized that repository connection. Do not share private remote URLs or access tokens. If no accessible checkout, label `HOST_SOURCE_READ_BLOCKED` and request a supported signed/verified source handoff.
5. For SSH, identify the **previously documented authorized Darwin destination alias** in Wolfram's existing SSH config/read-only receipt (do not guess host addresses or enumerate hosts). If identified, the sole optional connectivity check is **outbound from Wolfram to Darwin** using `BatchMode=yes` and `StrictHostKeyChecking=yes` with a read-only `true` command. If alias/principal cannot be established, report `DARWIN_OUTBOUND_SSH_UNVERIFIED` without attempting. Never try inbound Wolfram:22.
6. Only after the correct SSH direction succeeds, query access to the sanitized `muse_telemetry.prom` via the approved Darwin owner principal; a user with no read permission **must not** change file modes. Do not transfer raw Muse JSON or original collector source.
7. Return `WOLFRAM_CAPACITY_RECONCILIATION_RECEIPT/v1`, clearly separating: `HOST_IDENTITY`, `SWAP_USED`, `SWAP_DELTA`, `PAGEOUTS_DELTA`, `MEMORY_PRESSURE`, `GITHUB_HOST_ACCESS`, `WOLFRAM_TO_DARWIN_SSH`, `MUSE_PROM_READ`, `GRAFANA_INSTALL_APPROVED=false`.

## Alternative architecture before full stack

If pressure remains high, propose an **on-demand** Wolfram-only read-only local chart/HTML visualization from sanitized Muse `.prom` data instead of resident Prometheus/Grafana, while preserving provenance labels. A static HTML graph does **not** count as Grafana/Prometheus or as a live scraped data source. Do not implement or serve until user approval and a source file is actually accessible.

**No automatic install, no new bind ports or launchd entries, no Work/model changes, no main branch write.**
