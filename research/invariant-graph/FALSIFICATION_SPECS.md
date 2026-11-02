# MIN-18 Bounded Falsification Specifications & Reproducible Ranking

## 1. Reproducible Scoring Rubric (IDEIR-v1)

To resolve defect MIN-18-QA-04 (where scores `9.8`, `9.2`, and `8.9` were previously ungrounded in explicit rubrics), candidate evaluation is governed by the **Invariant Decidability & Epistemic Impact Rubric (IDEIR-v1)**.

### Evaluation Axes & Weights
$$\text{Score } S = \sum_{k=1}^4 w_k \cdot C_k = 0.35 \cdot C_1 + 0.30 \cdot C_2 + 0.20 \cdot C_3 + 0.15 \cdot C_4$$

1. **$C_1$: Formal Rigor & Falsifiability ($w_1 = 0.35$)**: Existence of a closed-form analytical bound, test statistic, and non-arbitrary rejection threshold under a sharp null hypothesis.
2. **$C_2$: Empirical Grounding & Anti-Sybil Proof ($w_2 = 0.30$)**: Mathematical resistance against search-budget inflation, prompt gaming, and identity branching; grounded directly in empirical observations from Issue #168.
3. **$C_3$: Cross-Domain Generality ($w_3 = 0.20$)**: Structural applicability across multiple operational domains (scientific inference, resource allocation, and multi-host systems).
4. **$C_4$: Implementability & Minimal Test Cost ($w_4 = 0.15$)**: Feasibility of running the cheapest bounded falsification protocol on local commodity hardware in $< 5$ seconds with $0 external spend.

### Component Breakdown Table

| Rank | Candidate ID | Canonical ID | Anchor Claim | $C_1$ (0.35) | $C_2$ (0.30) | $C_3$ (0.20) | $C_4$ (0.15) | Computed $S$ | Rounded Score |
|---|---|---|---|---|---|---|---|---|---|
| **1** | `CANDIDATE-01` | `CANONICAL-01` | `CLAIM-011` | 9.8 | 10.0 | 9.5 | 9.8 | 9.800 | **9.8** |
| **2** | `CANDIDATE-02` | `CANONICAL-03` | `CLAIM-001` | 9.2 | 9.0 | 9.0 | 9.8 | 9.190 | **9.2** |
| **3** | `CANDIDATE-03` | `CANONICAL-05` | `CLAIM-003` | 8.6 | 9.2 | 8.8 | 9.2 | 8.910 | **8.9** |

---

## 2. Bounded Falsification Specifications

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
  - **Pass**: Under $H_0$, $\mathbb{E}[E^*] \le 1.0$ across all stopping times, and 99th percentile $E^* \le 100$ (Markov bound holds). Sybil identity splitting produces zero net gain in portfolio e-value.
  - **Fail**: An actor generates expected portfolio e-wealth growth $> 1.0$ under the null solely by forking identities or searching $m$ parallel branches without weight partitioning.
- **Cheapest Test**: Vectorized NumPy simulation of 5,000 Monte Carlo runs (500 steps each). Compute wall-clock time $< 3.5$s on Apple Silicon / x86_64, $0 external quota.

---

### Rank 2 (`FALSIF-SPEC-002`): Golden Trinity Ratio Permutation-Matched Dirichlet Simplex Invariant
- **Target Invariant**: `CANONICAL-03` (Anchor: `CLAIM-001`, Source: [#168#issuecomment-5648693413](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5648693413))
- **Mathematical Formulation**: The normalized triple $(1, \phi, \phi^2)$ normalized to unit sum $(\frac{1}{2\phi^2}, \frac{1}{2\phi}, \frac{1}{2}) \approx (0.191, 0.309, 0.500)$ represents a genuine structural optimum in Context-Behavior-Value allocation only if its out-of-sample held-out performance exceeds the 95th percentile of exchangeable symmetric Dirichlet triples $\text{Dir}(1,1,1)$ under strictly matched permutation-selection budgets.
- **Null Hypothesis ($H_0$)**: The empirical performance of $(1, \phi, \phi^2)$ on held-out tasks is statistically indistinguishable from (A) the median of Dirichlet triples, or (B) the coarse baseline $(0.25, 0.25, 0.50)$, when both are granted identical 6-permutation selection budgets on training data.
- **Falsification Protocol**:
  1. Normalize candidate $\phi$-triple and 1,000 control triples sampled from $\text{Dir}(1, 1, 1)$ on the 2-simplex.
  2. For each shape, evaluate all 6 permutations of $(w_1, w_2, w_3)$ over training task embeddings.
  3. Select best permutation on training data alone; freeze choice.
  4. Score frozen shapes across 200 held-out evaluation splits.
  5. Compute empirical percentile rank of $\phi$-shape relative to Dirichlet control distribution and paired t-test against coarse $(0.25, 0.25, 0.50)$.
- **Pass/Fail Threshold**:
  - **Pass**: $\phi$-shape out-of-sample percentile $\ge 95.0\%$ among Dirichlet controls AND achieves statistically significant superiority over $(0.25, 0.25, 0.50)$ with $p < 0.01$.
  - **Fail**: $\phi$-shape held-out percentile $< 95.0\%$ OR effect size compared to $(0.25, 0.25, 0.50)$ has 95% CI covering zero.
- **Cheapest Test**: Synthetic allocation benchmark on 200 stratified test vectors using pre-computed task-embedding similarity matrices. Run time $< 2.0$s, $0 external quota.

---

### Rank 3 (`FALSIF-SPEC-003`): Durable Dispatch-Boundary Process-Binding Invariant
- **Target Invariant**: `CANONICAL-05` (Anchor: `CLAIM-003`, Source: [#168#issuecomment-5648743239](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5648743239))
- **Mathematical Formulation**: An orchestration exit status (e.g. status 137, 255) is an execution-membrane event, not verifiable evidence of leaf process termination or resource exhaustion. Incident classification requires a cryptographically bound dispatch receipt binding `(task_lease_id, host_identity, process_tree, leaf_pid, exit_status, raw_signal, memory_telemetry)`.
- **Null Hypothesis ($H_0$)**: Wrapper / transport exit codes faithfully identify leaf process exit causes across remote SSH / UDS execution without kernel process-binding records.
- **Falsification Protocol**:
  1. Spawn a background worker executing an atomic task lease.
  2. Terminate the SSH alias / intermediate wrapper with SIGPIPE / connection break while the worker process remains active.
  3. Capture orchestrator status code (status 137 / 255) vs actual worker OS process table state.
  4. Verify whether dispatcher correctly tags the event as `MEMBRANE_FAULT` / `EVIDENCE_INSUFFICIENT` rather than leaf OOM.
- **Pass/Fail Threshold**:
  - **Pass**: The dispatch system rejects exit code 137 as an OOM proof unless corroborated by leaf PID SIGKILL confirmation and kernel memory pressure telemetry.
  - **Fail**: Dispatch system classifies a broken transport wrapper as a leaf process crash / OOM, resulting in erroneous operator alerts or blind retries.
- **Cheapest Test**: Local subshell script: child writes PID and sleeps; parent terminates abruptly with exit 137. Dispatch verifier inspects `/proc` or `ps` output to confirm child survived. Run time $< 1.0$s.
