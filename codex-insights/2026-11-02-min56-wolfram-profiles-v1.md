# MIN-56 insight: WOLFRAM_PROFILES/v1 sovereign capacity & generator gate

Run ID: `run-9040b3b5ef15`  
Ticket: `MIN-56` (WOLFRAM_PROFILES/v1 — Local AI Forge and formal math modes)  
Agent: `agy@wolfram`  

## 1. Capacity Reality on Apple Silicon (16 GiB)

High resident swap on macOS arm64 (~12.8 GiB) does not equate to active memory thrashing. The kernel compressor holds over 1.7M compressed pages while system-wide memory pressure reports 72% free. Evaluating capacity on single RSS numbers or attempting automated swap purging (`purge`) causes performance degradation. Safe pilot guardrails require tracking the 5-minute swap delta ($\Delta \text{swap} > 512\text{ MiB}$) and memory pressure drops below 25% free.

## 2. Three Mutually Exclusive Operational Profiles

- **GUARD (Base):** Preserves `fleetd`, `token_governor`, `tailscaled`, `wolfram-agent-*`, Chrome, and telemetry daemons. Zero extra RAM.
- **FORGE (Local AI Generator):** Bounded single-model Ollama (3B–8B quantized, max_parallel=1, ctx $\le 4096$, gen $\le 2048$, RSS ceiling 4 GiB). Bare-metal Metal acceleration preferred over Colima VM. Permitted: scaffolding, test design, lint, synthetic fixtures. Prohibited: direct git push, certifying proofs, unreviewed merge.
- **MATH (Formal Research):** Lean4/mathlib, Rust test harnesses, SymPy invariant search. Headroom reserved: 6 GiB RSS for compiler spikes. FORGE LLM models unloaded during MATH epochs.

## 3. Falsifiable Benefit Test Discipline

Never equate local token volume with economic value or correctness. The 10-task benchmark register (`WOLFRAM_LOCAL_GENERATOR_EVAL_RECEIPT/v1`) enforces a zero-tolerance policy for false DONE claims ($0$) and requires 100% test pass rate. If local generation creates human review debt exceeding external token cost savings, the candidate model is disqualified.

## 4. Observability Decoupling

Resident Grafana/Prometheus servers on Wolfram consume 1.5–3.0 GiB RSS and continuous I/O, competing directly with FORGE/MATH compute headroom. Visualization is decoupled to Grafana Cloud Free push (MIN-53/MIN-55) or on-demand local static HTML previews.
