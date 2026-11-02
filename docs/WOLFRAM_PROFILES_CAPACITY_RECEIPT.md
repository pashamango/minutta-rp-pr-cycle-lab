# WOLFRAM_PROFILES_CAPACITY_RECEIPT/v1

**Document ID:** `WOLFRAM_PROFILES_CAPACITY_RECEIPT/v1`  
**Linear Reference:** [MIN-56](https://linear.app/mindrock/issue/MIN-56/wolfram-profilesv1-local-ai-forge-and-formal-math-modes)  
**Parent Project:** Darwin Prometheus — Sovereign Intelligence Observatory  
**Target Host:** MacBook Wolfram (Apple Silicon arm64, 16 GiB Unified Memory, macOS 26.6.2)  
**Authority:** Principal Pavel Cherkashin (`pavel@mindrock.capital`)  
**Status:** PROPOSED & BENCHMARKED (Read-Only / No host service mutation authorized)

---

## 1. Executive Summary & Objective

The objective of **WOLFRAM_PROFILES/v1** is to maximize sovereign, on-device compute utility on Wolfram (16 GiB Apple Silicon) for reducing external coding and research token costs without exhausting RAM, introducing latency jitter, or destabilizing the existing Token Governor and network daemons.

This receipt records:
1. Live, empirical host capacity and memory pressure probes.
2. The specification of three mutually exclusive operational profiles (`GUARD`, `FORGE`, `MATH`).
3. Strict arbitration and abort guardrails protecting existing daemons.
4. Independent dashboard placement alternatives evaluated outside of Wolfram.

---

## 2. Empirical Host Observations & Capacity Probing

### 2.1 Live Probing Data (2026-11-02 Wolfram arm64)

```text
Host Architecture:         Apple Silicon arm64
Total Hardware Memory:     16.00 GiB (17,179,869,184 bytes)
Hardware Page Size:        16,384 bytes (16 KiB)
System Memory Free:        72.0% (memory_pressure probe)
Swap Usage (Encrypted):    total = 14,336.00 MiB | used = 12,812.10 MiB | free = 1,523.90 MiB
Mach Compressor Stats:     1,741,795 pages compressed (~27.8 GiB uncompressed held in swap/compressor)
I/O Activity:              Pageins: 749,540,364 | Pageouts: 8,471,936
Process Footprint Note:    Chrome renderer ~1.9 GiB RSS; Ollama resident (0 active loaded models)
```

### 2.2 Key Memory Dynamics Finding: High Resident Swap $\neq$ Swap Growth

A critical observation from both the 2026-10-14 baseline and 2026-11-02 measurements:
- macOS Apple Silicon memory management deliberately retains clean pages in swap and compressed pools rather than aggressively discarding them.
- **High resident swap (~12.8 GiB) is steady-state behavior**, not a leak or active thrashing.
- System-wide memory pressure reports **72% free**, indicating ample working set headroom.
- **Decision Rule:** Abort triggers must be driven by **swap growth rate** ($\Delta \text{swap} > 512\text{ MiB}$ over a 5-minute sampling window) and **memory pressure drops** ($< 25\%$ free), rather than single-point RSS or total swap usage numbers.
- Automated swap purging (`purge` command) is strictly **prohibited** as it forces mass unneeded disk re-reads and freezes interactive tasks.

---

## 3. Three Mutually Exclusive Operational Profiles

Wolfram operates strictly in one of three profiles at any time:

```
                      ┌─────────────────────────────────┐
                      │          GUARD (Base)           │
                      │  RAM Ceiling: 0 extra MiB       │
                      │  Governor + Telemetry + Tailnet │
                      └───────────────┬─────────────────┘
                                      │
                   Exclusive Arbitration (FORGE xor MATH)
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐
│            FORGE             │              │             MATH             │
│   (Local AI Generator)       │              │      (Formal Research)       │
│  RAM Ceiling: 4 GiB RSS      │     XOR      │  RAM Ceiling: 6 GiB RSS      │
│  Single 3B-8B Ollama LLM     │              │  Lean4 / Mathlib / SymPy     │
│  Max Parallel = 1            │              │  Compiler Spike Headroom     │
└──────────────────────────────┘              └──────────────────────────────┘
```

### 3.1 Profile Specifications

| Dimension | GUARD (Base Profile) | FORGE (Local Generator) | MATH (Formal Research) |
|---|---|---|---|
| **Role** | Sovereign telemetry & telemetry guardian | Resource-bounded local code generation | Formal verification & symbolic math |
| **Active Heavy Process** | None | Single Ollama 3B–8B model | Lean4 / Rust compiler / SymPy |
| **Max Extra RSS Ceiling** | `0 MiB` | `4,096 MiB` (4 GiB) | `6,144 MiB` (6 GiB) |
| **Max Parallelism** | `0` | `1` (max_parallel=1) | `1` (single active proof run) |
| **Context / Gen Limit** | N/A | $\le 4,096$ ctx / $\le 2,048$ tokens | Bounded search depth / timeout 300s |
| **Colima / VM Usage** | Prohibited | Bare-metal Apple Silicon preferred | Prohibited |
| **Candidate Tasks** | Telemetry, Governor, Tailscale | Scaffolding, test design, lint, fixtures | Lean4 lemmas, invariant check, SymPy |
| **Prohibited Actions** | Terminating daemons for RAM | Proof certification, direct git push | Heavy LLM inference concurrently |

---

## 4. Profile Arbitration & Safety Guardrails

### 4.1 Read-Only `profile plan` First

No operational profile switch may be executed without first generating a verified, read-only transition plan:
```bash
python3 tools/wolfram-profiles plan --target FORGE --current GUARD
```
The plan inspects:
1. Current host memory pressure (`memory_pressure`).
2. Current swap usage and pageout rates.
3. Protected daemon preservation.
4. Active heavy workloads (ensuring `FORGE xor MATH` mutual exclusion).

### 4.2 Protected Daemon List (Non-Destructive Guarantee)

Under no circumstances may the profile harness stop, suspend, or signal the following processes:
- `fleetd` (Fleet orchestrator and vacuum dispatcher)
- `token_governor` (Codex/external token quota enforcement)
- `wolfram-agent-watcher` & `wolfram-agent-reporter` (Issue mailbox pipelines)
- `tailscaled` (Private mesh connectivity to Darwin and Cloud)
- `Google Chrome` / `Chrome` (User browsing sessions)
- `sshd` / `launchd` (Host system management)

The harness is only authorized to stop non-critical processes started **by the profile harness itself** (e.g., unloading an Ollama model before switching to MATH).

### 4.3 Automated Abort Thresholds

A running FORGE or MATH session must abort immediately if any of the following occur:
1. System memory free percentage falls below **25%**.
2. Swap usage increases by more than **512 MiB** during the task epoch.
3. Pageout rate exceeds **2,500 pages/minute** in steady-state operation.
4. Any network disconnect or Tailscale peer loss with Darwin occurs.

---

## 5. Dashboard Alternatives Analysis (MIN-53 / MIN-55 Boundary)

Hosting Prometheus or Grafana servers locally on Wolfram consumes 1.5–3.0 GiB RSS and constant I/O, which directly competes with FORGE/MATH compute headroom. In alignment with MIN-53/MIN-55, visualization is decoupled from Wolfram:

1. **Option A: Grafana Cloud Free Managed UI**
   - Free tier ($0) supports up to 10k active series and 14-day metrics retention.
   - Requires outbound, authenticated, sanitized metric push from Darwin/Wolfram collector.
   - Zero resident dashboard RAM on Wolfram.
2. **Option B: Google Sheets + Looker Studio**
   - Nightly aggregated CSV/JSON ledger sync.
   - Zero server process, sovereign raw ledger preserved.
   - Readily accessible for Principal review.
3. **Option C: On-Demand Local HTML Preview**
   - Ephemeral static HTML reporting generated only on request.
   - 0 MiB background memory footprint.
   - Fully sovereign with zero external network transmission.

**Conclusion:** Local resident Grafana on Wolfram is rejected. Dashboarding is relegated to Option A (managed cloud push) or Option C (on-demand static preview).

---

## 6. Verification & Admissibility Gate

The `tools/wolfram-profiles` harness is fully verified with 16 automated unit tests (`tests/test_wolfram_profiles.py`), validating:
- Sysctl and memory pressure parsing.
- Headroom threshold calculation.
- Mutual exclusion between FORGE and MATH.
- Protected daemon immunity.
