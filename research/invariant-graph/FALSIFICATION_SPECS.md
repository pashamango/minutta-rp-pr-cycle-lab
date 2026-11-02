# MIN-18 Bounded Falsification Specifications & Reproducible Ranking

## 1. Reproducible Scoring Rubric (IDEIR-v1)

Candidate evaluation is governed by the **Invariant Decidability & Epistemic Impact Rubric (IDEIR-v1)**. Component scores are assigned based on objective achievement criteria across four orthogonal axes, and **all six canonical invariants** (`CANONICAL-01` through `CANONICAL-06`) are formally evaluated.

### Evaluation Axes & Weights
$$\text{Score } S = \sum_{k=1}^4 w_k \cdot C_k = 0.35 \cdot C_1 + 0.30 \cdot C_2 + 0.20 \cdot C_3 + 0.15 \cdot C_4$$

### Objective Achievement Criteria & Score Bands

1. **$C_1$: Formal Rigor & Falsifiability ($w_1 = 0.35$)**
   - **9.0 – 10.0**: Closed-form mathematical/probabilistic formulation, exact martingale or conservation law, explicit null hypothesis with provable error bounds or deterministic decision rule (e.g. e-process martingales, linear-algebraic rank matrices, OS kernel binding structs).
   - **7.5 – 8.9**: Semi-formal operational protocol/state-machine with falsifiable pass/fail criteria, but depends on operational heuristic parameters or environment assumptions.
   - **6.0 – 7.4**: Qualitative structural partition or taxonomy lacking exact mathematical test statistic or sharp analytical decision boundary.
   - **< 6.0**: Informal claim without falsifiable operational null hypothesis.

2. **$C_2$: Empirical Grounding & Anti-Sybil Proof ($w_2 = 0.30$)**
   - **9.5 – 10.0**: Mathematically provable immunity to identity splitting, replication cloning, parallel prompt mining, or search budget inflation (e.g. unit simplex conservation $\sum w_i = 1$, rank invariance $\Delta K = 0$). Directly grounded in primary empirical evidence from Issue #168.
   - **8.5 – 9.4**: Strong cryptographic or kernel-level identity binding (Ed25519 proof-of-possession, OS process tables) resisting single-host forgery.
   - **7.0 – 8.4**: Heuristic deduplication or permutation-selection thresholding; lacks cryptographic or kernel-level identity binding.
   - **< 7.0**: No anti-Sybil defense; susceptible to duplicate inflation.

3. **$C_3$: Cross-Domain Generality ($w_3 = 0.20$)**
   - **9.0 – 10.0**: Universal across multi-agent consensus, scientific hypothesis testing, distributed compute allocation, and economic settlement.
   - **8.0 – 8.9**: Broadly applicable across distributed execution systems and multi-host infrastructure, but specialized to runtime/OS capability semantics.
   - **7.0 – 7.9**: Domain-specific to prompt engineering, task taxonomy, or cognitive allocation; limited transfer to systems or cryptographic accounting.
   - **< 7.0**: Narrow single-use or project-specific applicability.

4. **$C_4$: Implementability & Minimal Test Cost ($w_4 = 0.15$)**
   - **9.5 – 10.0**: Ultra-low-cost reproducible test: $< 3.5$s wall-clock time on commodity CPU, $0 external API/network spend, pure vectorized code or local mock.
   - **9.0 – 9.4**: Low-cost local test: $< 5.0$s compute, requires local OS subshell/pipe execution, $0 external spend.
   - **7.5 – 8.9**: Moderate test cost: requires multi-host coordination, daemon execution, or larger corpora evaluation $> 5.0$s.
   - **< 7.5**: High test cost: external paid APIs, specialized hardware, or human-in-the-loop validation.

---

## 2. Complete Canonical Invariants Evaluation Table (All 6 Candidates)

The following table presents the reproducible scoring of all six canonical invariants under IDEIR-v1. The top 3 ranked candidates are selected for formal bounded falsification specifications.

| Rank | Canonical ID | Anchor Claim | Invariant Title | Domain Cluster | $C_1$ (0.35) | $C_2$ (0.30) | $C_3$ (0.20) | $C_4$ (0.15) | Computed $S$ | Rounded Score | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | `CANONICAL-01` | `CLAIM-011` | Conserved Evidence Portfolio Simplex & Matched Search-Budget | Cluster-1: Epistemic Accounting | 9.8 (Band 9.0–10.0) | 10.0 (Band 9.5–10.0) | 9.5 (Band 9.0–10.0) | 9.8 (Band 9.5–10.0) | 9.800 | **9.8** | **SELECTED (Spec 1)** |
| **2** | `CANONICAL-02` | `CLAIM-040` | Target-Conditioned Redundancy vs. True Value | Cluster-3: Distributed Membrane / Epistemic Accounting | 9.1 (Band 9.0–10.0) | 9.6 (Band 9.5–10.0) | 9.2 (Band 9.0–10.0) | 9.6 (Band 9.5–10.0) | 9.345 | **9.3** | **SELECTED (Spec 2)** |
| **3** | `CANONICAL-05` | `CLAIM-003` | Durable Dispatch-Boundary Process-Binding | Cluster-3: Distributed Membrane | 8.6 (Band 7.5–8.9) | 9.2 (Band 8.5–9.4) | 8.8 (Band 8.0–8.9) | 9.2 (Band 9.0–9.4) | 8.910 | **8.9** | **SELECTED (Spec 3)** |
| 4 | `CANONICAL-06` | `CLAIM-018` | Cryptographic Zero-Trust Membrane & Attenuating Semilattice | Cluster-3: Distributed Membrane | 8.5 (Band 7.5–8.9) | 9.3 (Band 8.5–9.4) | 8.5 (Band 8.0–8.9) | 9.6 (Band 9.5–10.0) | 8.905 | 8.9 | Below Top 3 Threshold |
| 5 | `CANONICAL-03` | `CLAIM-001` | Golden Trinity Ratio Permutation-Matched Dirichlet Simplex | Cluster-2: Golden Trinity Dynamics | 8.8 (Band 7.5–8.9) | 8.0 (Band 7.0–8.4) | 7.8 (Band 7.0–7.9) | 9.8 (Band 9.5–10.0) | 8.510 | 8.5 | Below Top 3 Threshold |
| 6 | `CANONICAL-04` | `CLAIM-036` | Teleological Semantics & Asymmetric Cause-Purpose Partitioning | Cluster-2: Golden Trinity Dynamics | 7.6 (Band 7.5–8.9) | 7.8 (Band 7.0–8.4) | 7.5 (Band 7.0–7.9) | 9.6 (Band 9.5–10.0) | 7.940 | 7.9 | Below Top 3 Threshold |

### Objective Score Justifications per Rubric Criteria
- **`CANONICAL-01` ($S = 9.800$, Rank 1)**:
  - $C_1 = 9.8$: Closed-form e-process martingale formulation (Wang 2025 Biometrika admissible merge) with exact Ville's inequality bound $P(\sup E_t \ge 1/\alpha) \le \alpha$ and Kraft sum bound $\sum 2^{-l_i} \le 1$.
  - $C_2 = 10.0$: Mathematically provable anti-Sybil immunity; identity splitting without weight partitioning yields zero expected e-wealth advantage under $H_0$. Grounded directly in Issue #168 comment 5649859218.
  - $C_3 = 9.5$: Universal across multi-agent consensus, scientific hypothesis testing, distributed compute allocation, and economic settlement.
  - $C_4 = 9.8$: Ultra-low-cost reproducible test: vectorized NumPy simulation of 5,000 Monte Carlo trajectories executes in $< 3.5$s on commodity CPU with $0 external spend.
- **`CANONICAL-02` ($S = 9.345$, Rank 2)**:
  - $C_1 = 9.1$: Closed-form linear-algebraic rank formalization: $m$ copies span rank 1; independent atom increases rank to 2. Orthogonal 3-ledger state $(R, K, T)$ with explicit target projection operator and XOR counterexample bounding synergistic value.
  - $C_2 = 9.6$: Mathematically provable anti-Sybil immunity against identity and replication cloning; pure copying or re-encoding strictly conserves rank ($\Delta K = 0$) and cannot mint novel value tokens. Grounded in Issue #168 comments 5655787687 and 5655848243.
  - $C_3 = 9.2$: Universal across multi-agent consensus, scientific hypothesis testing, distributed compute allocation, and economic settlement.
  - $C_4 = 9.6$: Ultra-low-cost reproducible test: vectorized matrix rank and projection test on synthetic provenance vectors executes in $< 2.0$s with $0 external spend.
- **`CANONICAL-05` ($S = 8.910$, Rank 3)**:
  - $C_1 = 8.6$: Semi-formal operational protocol for cross-host process tree telemetry, exit signal decoding, and kernel `/proc` inspection; depends on OS-specific process table semantics.
  - $C_2 = 9.2$: Strong kernel-level and cryptographic identity binding: OS process tables, PID/PPID tree verification, and 3-identity credential invariant resisting single-host forgery. Grounded in Issue #168 comments 5648743239 and 5649439196.
  - $C_3 = 8.8$: Broadly applicable across distributed execution systems and multi-host infrastructure, but specialized to runtime/OS semantics.
  - $C_4 = 9.2$: Low-cost local test: requires local subshell process fork and SIGPIPE fault injection script running in $< 1.0$s with $0 external spend.
- **`CANONICAL-06` ($S = 8.905$, Rank 4)**:
  - $C_1 = 8.5$: Semi-formal product semilattice $(R,O,L)$ and attenuating CRDT join protocol with monotone supersession state machine.
  - $C_2 = 9.3$: Strong cryptographic capability binding with Ed25519 signatures, content hashes, and monotonic attenuation discipline resisting unauthorized elevation. Grounded in Issue #168 comments 5651293792 and 5653556096.
  - $C_3 = 8.5$: Broadly applicable across distributed execution systems and multi-host infrastructure, but specialized to runtime/OS capability semantics.
  - $C_4 = 9.6$: Ultra-low-cost reproducible test: local semilattice join and capability attenuation validator executes in $< 2.0$s on CPU with $0 spend.
- **`CANONICAL-03` ($S = 8.510$, Rank 5)**:
  - $C_1 = 8.8$: Semi-formal ratio allocation model on 2-simplex evaluated under permutation budget matching; lacks closed-form analytical proof of $\phi$-optimality.
  - $C_2 = 8.0$: Heuristic permutation-matching budget; partially vulnerable to high-dimensional parameter tuning or split attacks. Does not possess cryptographic or kernel-level identity binding (strictly within band 7.0–8.4).
  - $C_3 = 7.8$: Domain-specific to prompt engineering, task taxonomy, and cognitive allocation; limited transfer to distributed systems or cryptographic accounting; does not achieve universal cross-domain coverage (strictly within band 7.0–7.9).
  - $C_4 = 9.8$: Ultra-low-cost reproducible test: synthetic Dirichlet benchmark runs in $< 2.0$s with $0 external spend.
- **`CANONICAL-04` ($S = 7.940$, Rank 6)**:
  - $C_1 = 7.6$: Qualitative/semi-formal taxonomy of teleological triplets $(U, D_\varepsilon, \Omega)$ and $(W,A,P,T,G)$ tuples; lacks exact mathematical test statistic.
  - $C_2 = 7.8$: Semantic separation of cause vs purpose; heuristic semantic classification vulnerable to subjective redefinition.
  - $C_3 = 7.5$: Domain-specific to task taxonomy and prompt semantics; limited transfer to systems or cryptographic accounting.
  - $C_4 = 9.6$: Ultra-low-cost reproducible test: semantic tuple parser and validation rules execute in $< 1.5$s on local CPU with $0 external spend.

---

## 3. Bounded Falsification Specifications (Top 3 Candidates)

### Rank 1 (`FALSIF-SPEC-001`): Conserved Evidence Portfolio Simplex & Matched Search-Budget Invariant
- **Target Invariant**: `CANONICAL-01` (Anchor: `CLAIM-011`, Source: [#168#issuecomment-5649859218](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5649859218))
- **Mathematical Formulation**: For any ensemble of autonomous exploration agents or hypotheses $\{H_i\}$ evaluated against null $P_0$ with valid e-values $\{E_i\}$, the aggregate evidence state $E^*$ must be governed by an admissible convex mixture $E^* = \sum_{i} w_i E_i$ where $w \in \Delta_m$ is predictable before step $t$. Identity splitting (Sybil forking) or transport redundancy multiplication cannot increase spendable evidence rank without consuming independent information.
- **Null Hypothesis ($H_0$)**: Adaptive search over $m$ synthetic agent streams under pure noise generates unbounded e-process wealth growth ($\mathbb{E}[E^*] > 1$) when individual agents can spawn child ledgers without partitioned simplex weights.
- **Falsification Protocol**:
  1. Generate 100 independent synthetic noise streams $X_t \sim \mathcal{N}(0, 1)$ under null $\mu = 0$.
  2. Dynamically fork Agent 1 into 10 sub-identities at step $t=20$ upon observing favorable local fluctuations.
  3. Compare unconstrained max-reporting $E_{\max} = \max_i(E_i)$ versus simplex mixture $E^* = \sum w_i E_i$ with $\sum w_i = 1$.
  4. Measure Type I error rate and e-wealth growth under 5,000 independent Monte Carlo trajectories.
- **Pass/Fail Threshold**:
  - **Pass**: Under $H_0$, $\mathbb{E}[E^*] \le 1.0$ across all stopping times, and 99th percentile $E^* \le 100$ (Markov bound holds). Sybil identity splitting produces zero net gain in portfolio e-value compared to the parent weight.
  - **Fail**: An actor generates expected portfolio e-wealth growth $> 1.0$ under the null solely by forking identities or searching $m$ parallel branches without weight partitioning.
- **Cheapest Test**: Vectorized NumPy simulation of 5,000 Monte Carlo runs (500 steps each). Compute wall-clock time $< 3.5$s on Apple Silicon / x86_64, $0 external quota.

---

### Rank 2 (`FALSIF-SPEC-002`): Target-Conditioned Redundancy vs. True Value Invariant
- **Target Invariant**: `CANONICAL-02` (Anchor: `CLAIM-040`, Source: [#168#issuecomment-5655787687](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5655787687))
- **Mathematical Formulation**: Pure replication, fountain/erasure fragments, and retry copies increase availability/recovery probability, but evidential or monetary weight increases only when a genuinely new independently bound provenance atom increases rank under the declared dependency model. In orthogonal state $(R, K, T)$, transport redundancy increases resilience $R$ while strictly conserving epistemic rank $K$ and target-relevant evidence $T$.
- **Null Hypothesis ($H_0$)**: Replication, re-encoding, or fountain fragmentation of existing evidence artifacts increases net epistemic or economic value beyond the rank of their underlying independent provenance atoms.
- **Falsification Protocol**:
  1. Generate a primary evidence record $e_1$ with verifiable provenance digest and observed likelihood ratio.
  2. Produce $N = 100$ distinct replicas, re-encodings, and Luby-transform fountain fragments of $e_1$ across simulated transport channels.
  3. Submit all $N$ replicas to the orthogonal 3-ledger accounting verifier.
  4. Measure resilience state $R$ vs evidence rank $K$ and target-relevant weight $T$.
  5. Verify that $\text{rank}(K) = 1$ and $T(e_1, \dots, e_N) = T(e_1)$, despite $R$ scaling with $N$.
- **Pass/Fail Threshold**:
  - **Pass**: The accounting system strictly maintains $\Delta K = 0$ and $\Delta T = 0$ across all $N$ transport copies, allocating only delivery/resilience service fees while strictly conserving epistemic principal.
  - **Fail**: Any replication, re-encoding, or fragmentation increases evidentiary rank ($K > 1$) or mints unearned settlement weight.
- **Cheapest Test**: Local Python test using numpy matrix rank and orthogonal projection: simulates 1,000 replicated packets, verifies rank invariance ($\text{rank} = 1$) and zero target-value drift. Execution time $< 1.5$s on commodity CPU, $0 external quota.

---

### Rank 3 (`FALSIF-SPEC-003`): Durable Dispatch-Boundary Process-Binding Invariant
- **Target Invariant**: `CANONICAL-05` (Anchor: `CLAIM-003`, Source: [#168#issuecomment-5648743239](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5648743239))
- **Mathematical Formulation**: An orchestration exit status (e.g. status 137, 255) is an execution-membrane event, not verifiable evidence of leaf process termination or resource exhaustion. Incident classification requires a cryptographically bound dispatch receipt binding `(task_lease_id, host_identity, process_tree, leaf_pid, exit_status, raw_signal, memory_telemetry)`.
- **Null Hypothesis ($H_0$)**: Wrapper / transport exit codes faithfully identify leaf process exit causes across remote SSH / UDS execution without kernel process-binding records.
- **Falsification Protocol**:
  1. Spawn a background worker executing an atomic task lease.
  2. Terminate the SSH alias / intermediate wrapper with SIGPIPE / connection break while the worker process remains active.
  3. Capture orchestrator status code (status 137 / 255) vs actual worker OS process table state.
  4. Verify whether the dispatcher correctly tags the event as `MEMBRANE_FAULT` / `EVIDENCE_INSUFFICIENT` rather than leaf OOM.
- **Pass/Fail Threshold**:
  - **Pass**: The dispatch system rejects exit code 137 as an OOM proof unless corroborated by leaf PID SIGKILL confirmation and kernel memory pressure telemetry.
  - **Fail**: If the dispatch system classifies a broken transport wrapper as a leaf process crash / OOM, resulting in erroneous operator alerts or blind retries.
- **Cheapest Test**: Local subshell script: child writes PID and sleeps; parent terminates abruptly with exit 137. Dispatch verifier inspects `/proc` or `ps` output to confirm child survived. Run time $< 1.0$s, $0 external quota.
