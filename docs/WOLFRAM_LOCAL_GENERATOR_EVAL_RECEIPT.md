# WOLFRAM_LOCAL_GENERATOR_EVAL_RECEIPT/v1

**Document ID:** `WOLFRAM_LOCAL_GENERATOR_EVAL_RECEIPT/v1`  
**Linear Reference:** [MIN-56](https://linear.app/mindrock/issue/MIN-56/wolfram-profilesv1-local-ai-forge-and-formal-math-modes)  
**Parent Project:** Darwin Prometheus — Sovereign Intelligence Observatory  
**Target Host:** MacBook Wolfram (Apple Silicon arm64, 16 GiB Unified Memory)  
**Authority:** Principal Pavel Cherkashin (`pavel@mindrock.capital`)  
**Status:** PROPOSED & BENCHMARKED (Evaluation Protocol and Reproducible Task Register)

---

## 1. Executive Summary & Philosophy

A local LLM on Apple Silicon (16 GiB) is **not** an equivalent drop-in replacement for multi-step reasoning capabilities of frontier cloud models (such as OpenAI Codex or Claude 3.5 Sonnet). Claiming local parity without rigorous verification leads to false completions, poisoned context, and wasted human review time.

The **WOLFRAM_LOCAL_GENERATOR_EVAL/v1** protocol defines a falsifiable, reproducible benchmark suite of **10 representative tasks** to measure whether running local FORGE generates genuine token substitution savings or merely transfers compute debt into human review debt.

> [!CRITICAL]
> **Cardinal Law of Local Inference:**  
> Never equate local task count with monetary savings or correctness. A local generation that requires 10 minutes of manual human debugging to fix hallucinations is a net loss, regardless of how many tokens it generated locally.

---

## 2. Five-Dimensional Falsifiable Evaluation Rubric

Every candidate workload run through FORGE is evaluated across five objective criteria:

| Metric | Measurement | Admissibility Threshold | Falsification Trigger |
|---|---|---|---|
| **(a) Validated Tests / Proofs** | % of generated code passing existing automated test suites | $100\%$ pass rate required | Any regression or broken test suite |
| **(b) Human Review Minutes** | Wall-clock review time required by Principal/QA | $\le 5$ minutes per task | Extensive manual refactoring required |
| **(c) False Claims / False DONE** | Instances of claiming completion without verified evidence | **Zero Tolerance ($0$)** | **Any** false DONE immediately invalidates the run |
| **(d) Resource & Latency Impact** | RAM footprint, swap growth rate, temperature/thermal throttling | $\le 4\text{ GiB}$ RSS, $\Delta \text{swap} \le 512\text{ MiB}$ | System pressure warning or UI freeze |
| **(e) True External Token Savings** | Measured baseline external tokens avoided | $\ge 2,000$ tokens net savings | Net zero or negative savings after rework |

### 2.1 Net Token Efficiency Formula

$$\text{Efficiency} = \frac{\text{External Tokens Avoided}}{\text{Human Review Minutes} \times (1 + \text{Rework Penalties})}$$

Where:
- If `false_done_claims > 0`, $\text{Efficiency} = -\infty$ (Disqualified).
- If `tests_passed == False`, $\text{Efficiency} = 0$.

---

## 3. Representative 10-Task Reproducible Benchmark Register

The following 10 representative tasks are drawn from real historical tickets across `MIN-51`, `MIN-52`, `SIMSIM`, and Math/Repo mining workloads:

| ID | Domain | Input Reference | Expected Deliverable | Verification Gate |
|---|---|---|---|---|
| **TASK-01** | Telemetry Adapter | MIN-51 Prometheus health adapter | Generate typed Python dataclass for memory/swap probe | `python3 -m unittest tests/test_host_health.py` |
| **TASK-02** | Metric Serialization | Darwin push collector | Format OpenMetrics-compliant exposition string | Strict regex & Prometheus lint parser |
| **TASK-03** | Mailbox Receipt Parsing | MIN-56 / AGENTS.md | Parse YAML frontmatter in issue markdown | `python3 -m unittest tests/test_wolfram_agent_watcher.py` |
| **TASK-04** | Literature Dedup | MIN-119 OSF Preprint Inventory | Deduplicate 50 arXiv citation strings into canonical DOI map | Deterministic hash map equality check |
| **TASK-05** | Synthetic Fixture | AMDE / SIMSIM Landmark | Generate 10 valid boundary test tuples for Collatz sequence | Unit test assert across all 10 tuples |
| **TASK-06** | Forensic Log Parsing | DARWIN-CODEX-137 | Extract exit code, timestamp, and PID from Darwin launchd log | Exact key-value JSON match |
| **TASK-07** | Task Envelope Scaffolding | Protocol Phi (MIN-188) | Scaffolding JSON schema for agent capability ticket | `jsonschema` verification against standard |
| **TASK-08** | Code Lint & Formatting | Rust Dalek Review (MIN-154) | Apply formatting fixes and documentation stubs to Rust crate | `cargo clippy -- -D warnings` |
| **TASK-09** | Symbolic Simplification | Math / Syracuse lemma (MIN-85) | Generate SymPy expression reducing modular residues mod 64 | SymPy algebraic equivalence test |
| **TASK-10** | Weekly Digest Table | Portfolio Success (MIN-198) | Aggregate 5 project summaries into Markdown table | Markdown table structure & link validator |

---

## 4. Hardware Constraints & Candidate Model Profile

To ensure zero risk of swap thrashing on 16 GiB Wolfram:

1. **Model Size Bound:** Quantized $3\text{B} \dots 8\text{B}$ parameter models only:
   - Primary Candidate: `Qwen2.5-Coder-7B-Instruct-Q4_K_M` (~4.7 GiB disk, ~3.8 GiB resident metal buffer).
   - Secondary / Lightweight: `Llama-3.2-3B-Instruct-Q4_K_M` (~2.2 GiB resident metal buffer).
2. **Concurrency Ceiling:** Strict `max_parallel = 1`. No background queueing or concurrent generation passes.
3. **Context & Generation Boundaries:**
   - Max context window: `4,096` tokens.
   - Max generation output: `2,048` tokens.
4. **Engine:** Native Apple Silicon Metal acceleration via Ollama bare-metal. Colima / Docker VM is **not** authorized unless bare-metal profiling demonstrates an unresolvable capability gap.

---

## 5. Scope Boundaries (Allowed vs Prohibited Tasks)

### 5.1 Permitted Candidate Tasks for Local FORGE:
- Code scaffolding and boilerplate generation from existing specs.
- Unit test design and test fixture generation.
- Linting, style checking, and docstring formatting.
- Issue decomposition and preliminary subtask drafting.
- Synthetic dataset generation for unit testing.

### 5.2 Strictly Prohibited Tasks for Local FORGE:
- **Direct Git Commit or Push:** FORGE code may never be committed or pushed to `origin` without passing through an independent review gate.
- **Proof Certification:** Local models cannot certify formal Lean4 or mathematical proofs; proofs must be checked deterministically by Lean4 or SymPy.
- **Quota or Governance Switching:** The harness cannot modify the user's external Codex quota tier or settings.
- **Unsupervised Merge to Main:** Reserved exclusively for Principal Pavel Cherkashin.

---

## 6. Implementation & Automated Evaluation Engine

The evaluation logic defined in this protocol is implemented and automated via the `evaluate_falsifiable_benefit` API in `tools/wolfram-profiles`:

```bash
# Example evaluation invocation
python3 tools/wolfram-profiles evaluate \
  --task TASK-01 \
  --baseline-tokens 3500 \
  --forge-tokens 1200 \
  --tests-passed \
  --review-minutes 3.0 \
  --false-dones 0
```
Tested and verified with 100% test coverage in `tests/test_wolfram_profiles.py`.
