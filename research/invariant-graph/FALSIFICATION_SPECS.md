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
| **3** | `CANONICAL-05` | `CLAIM-003` | Durable Dispatch-Boundary Process-Binding | Cluster-3: Distributed Membrane | 8.6 (Band 7.5–8.9) | 9.2 (Band 8.5–9.4) | 8.8 (Band 8.0–8.9) | 9.7 (Band 9.5–10.0) | 8.985 | **9.0** | **SELECTED (Spec 3)** |
| 4 | `CANONICAL-06` | `CLAIM-018` | Cryptographic Zero-Trust Membrane & Attenuating Semilattice | Cluster-3: Distributed Membrane | 8.5 (Band 7.5–8.9) | 9.3 (Band 8.5–9.4) | 8.5 (Band 8.0–8.9) | 9.6 (Band 9.5–10.0) | 8.905 | 8.9 | Below Top 3 Threshold |
| 5 | `CANONICAL-03` | `CLAIM-001` | Golden Trinity Ratio Permutation-Matched Dirichlet Simplex | Cluster-2: Golden Trinity Dynamics | 8.8 (Band 7.5–8.9) | 8.0 (Band 7.0–8.4) | 7.8 (Band 7.0–7.9) | 9.8 (Band 9.5–10.0) | 8.510 | 8.5 | Below Top 3 Threshold |
| 6 | `CANONICAL-04` | `CLAIM-036` | Teleological Semantics & Asymmetric Cause-Purpose Partitioning | Cluster-2: Golden Trinity Dynamics | 7.0 (Band 6.0–7.4) | 7.8 (Band 7.0–8.4) | 7.5 (Band 7.0–7.9) | 9.6 (Band 9.5–10.0) | 7.730 | 7.7 | Below Top 3 Threshold |

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
- **`CANONICAL-05` ($S = 8.985$, Rank 3)**:
  - $C_1 = 8.6$: Semi-formal operational protocol for cross-host process tree telemetry, exit signal decoding, and kernel `/proc` inspection; depends on OS-specific process table semantics.
  - $C_2 = 9.2$: Strong kernel-level and cryptographic identity binding: OS process tables, PID/PPID tree verification, and 3-identity credential invariant resisting single-host forgery. Grounded in Issue #168 comments 5648743239 and 5649439196.
  - $C_3 = 8.8$: Broadly applicable across distributed execution systems and multi-host infrastructure, but specialized to runtime/OS semantics.
  - $C_4 = 9.7$: Ultra-low-cost reproducible test: local subshell process fork and SIGPIPE fault injection script executes in $< 1.0$s ($< 3.5$s) on commodity CPU with $0 external spend.
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
- **`CANONICAL-04` ($S = 7.730$, Rank 6)**:
  - $C_1 = 7.0$: Qualitative structural partition and taxonomy of teleological triplets $(U, D_\varepsilon, \Omega)$ and $(W,A,P,T,G)$ tuples; lacks exact mathematical test statistic or sharp rejection threshold (strictly within band 6.0–7.4).
  - $C_2 = 7.8$: Semantic separation of cause vs purpose; heuristic semantic classification vulnerable to subjective redefinition.
  - $C_3 = 7.5$: Domain-specific to task taxonomy and prompt semantics; limited transfer to systems or cryptographic accounting.
  - $C_4 = 9.6$: Ultra-low-cost reproducible test: semantic tuple parser and validation rules execute in $< 1.5$s on local CPU with $0 external spend.

---

## 3. Bounded Falsification Specifications (Top 3 Candidates)

### Rank 1 (`FALSIF-SPEC-001`): Conserved Evidence Portfolio Simplex & Matched Search-Budget Invariant
- **Target Invariant**: `CANONICAL-01` (Anchor: `CLAIM-011`, Source: [#168#issuecomment-5649859218](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5649859218))
- **Mathematical Formulation**: For any ensemble of exploration agents or hypotheses $\{H_i\}$ with valid e-processes $\{E_{i,t}\}$, the portfolio mixture $E^*_t = \sum_{i=1}^m w_{i,t} E_{i,t}$ under predictable weights $w_t \in \Delta_m$ ($\sum w_{i,t} = 1, w_{i,t} \ge 0$) is an admissible supermartingale with $\mathbb{E}[E^*_t \mid \mathcal{F}_{t-1}] \le 1$. By Doob's optional stopping theorem for non-negative supermartingales on bounded horizon $T_{\max}$, $\mathbb{E}[E^*_\tau] \le \mathbb{E}[E^*_0] = 1.0$ across any $\mathcal{F}_t$-adapted stopping time $\tau \le T_{\max}$. Identity splitting (Sybil forking) under simplex-partitioned weights $\sum_{k=1}^K w_{\text{fork},k,t} = w_{\text{parent},t}$ cannot increase spendable evidence rank or aggregate expected e-wealth. Running suprema $\sup_{t \le T_{\max}} E^*_t$ are governed by Ville's maximal inequality $\mathbb{P}(\sup_{t \le T_{\max}} E^*_t \ge \lambda) \le 1/\lambda$.
- **Null Hypothesis ($H_0$)**: Under null noise drift $\mu = 0$ across $m = 100$ exploration streams over bounded horizon $T_{\max} = 500$ steps, an adaptive Sybil identity splitting intervention with simplex-partitioned weights ($\sum_{k=1}^K w_{\text{fork},k} = w_{\text{parent}}$, conserving total portfolio weight $\sum w = 1$) generates no statistically significant portfolio wealth growth above the supermartingale bound ($\mathbb{E}[E^*_\tau] \le 1.0$) for any adapted stopping time $\tau$ in pre-declared family $\mathcal{T}$, and yields zero expected wealth advantage over un-forked control ($\mathbb{E}[\Delta E^*_\tau] \le 0$). *(Note: Unconstrained identity duplication without simplex partitioning trivially inflates portfolio capitalization via external capital injection, violating the simplex premise rather than falsifying the invariant; invariant falsification requires proving excess wealth extraction under simplex-conserved weights).*
- **Falsification Protocol**:
  1. **Deterministic RNG & Bounded Horizon Setup**: Initialize NumPy PCG64 random generator with fixed seed policy `SeedSequence(20261102)`. Set bounded horizon $T_{\max} = 500$ steps, stream count $m = 100$, and trajectory sample size $N = 5,000$ independent Monte Carlo paths.
  2. **Null Noise Stream & Martingale Generation**: Generate null increments $X_{i,t} \sim \mathcal{N}(0, 1)$ i.i.d. Compute non-negative e-process martingale factors $E_{i,t} = \prod_{s=1}^t \exp(\lambda X_{i,s} - \lambda^2 / 2)$ with fixed betting fraction $\lambda = 0.1$.
  3. **Adversarial Dynamic Sybil Forking with Paired Control**: At step $t = 20$, identify the locally leading stream $i^* = \operatorname{argmax}_i E_{i, 20}$. Run paired parallel trajectories across all $N$ paths using common random numbers: (a) Control trajectory: baseline ensemble with un-forked stream $i^*$ maintaining weight $w_{i^*, t}$; (b) Sybil-forked trajectory: dynamically split stream $i^*$ into $K = 10$ child sub-identities sharing identical historical evidence up to $t = 20$, with simplex weight partitioning $\sum_{k=1}^{10} w_{\text{fork},k,t} = w_{i^*, t}$ (each child receiving $w_{\text{fork},k} = w_{i*} / 10$), preserving total simplex sum $\sum_i w_i = 1$.
  4. **Pre-declared Adapted Stopping Time Family & Sequential Multiplicity Evaluation**: Evaluate portfolio states across a parameterized family of strictly $\mathcal{F}_t$-adapted stopping times $\mathcal{T}$ of size $|\mathcal{T}| = 9$: deterministic fixed horizons $\tau_{\text{fixed}} \in \{50, 100, 250, 500\}$ (4 endpoints); first hitting times $\tau_\theta = \min\{t \le T_{\max} : E^*_t \ge \theta\} \wedge T_{\max}$ for $\theta \in \{1.5, 2.0, 5.0, 10.0\}$ (4 endpoints); and adapted trailing-stop drawdown $\tau_{\text{drawdown}} = \min\{t \le T_{\max} : E^*_t \le 0.80 \cdot \max_{s \le t} E^*_s\} \wedge T_{\max}$ (1 endpoint). Each statistical look evaluates 19 simultaneous endpoints (9 stopping times for portfolio wealth supermartingale bounds $\mathbb{E}[E^*_\tau] \le 1.0$, 9 stopping times for paired Sybil excess neutrality $\mathbb{E}[\Delta E^*_\tau] \le 0.0$, and 1 maximal tail endpoint for Ville's inequality $\mathbb{P}(\sup_{t \le 500} E^*_t \ge 20) \le 0.05$). Across the group-sequential design permitting initial look ($N_1 = 5,000$) and up to $B_{\max} = 2$ adaptive sample extensions (Retry 1: $N_2 = 10,000$, Retry 2: $N_3 = 20,000$; total $K_{\max} = 3$ looks), the complete multiplicity family comprises $|\mathcal{M}| = 19 \times 3 = 57$ simultaneous comparisons. Statistical guarantees are pre-declared under authoritative joint Family-Wise Error Rate (FWER) control at $\alpha_{\text{FWER}} \le 10^{-3}$ across all $|\mathcal{M}| = 57$ comparisons via group-sequential Bonferroni correction ($\alpha_{\text{adj}} = 10^{-3} / 57 = 1.754386 \times 10^{-5}$, two-sided critical value $t_{\text{FWER}} = 4.294$ with $df \ge 4999$). Pointwise confidence bounds ($\alpha_{\text{pointwise}} = 10^{-3}$, $t_{\text{pointwise}} = 3.090$) are documented solely as unadjusted single-comparison reference values. Pathwise maximum $\sup_{t \le 500} E^*_t$ is not an adapted stopping time and is analyzed separately via Ville's maximal inequality.
  5. **Estimator, Paired Difference & Confidence Bound Algorithm**: For each Monte Carlo path $j \in \{1, \dots, N_k\}$ at sequential look $k \in \{1, 2, 3\}$, record stopping values $E^{*(j)}_{\text{control}, \tau}$ and $E^{*(j)}_{\text{sybil}, \tau}$ across all $\tau \in \mathcal{T}$. Compute paired difference $D^{(j)}_\tau = E^{*(j)}_{\text{sybil}, \tau} - E^{*(j)}_{\text{control}, \tau}$. Compute sample means $\bar{E}^*_\tau = \frac{1}{N_k} \sum_{j=1}^{N_k} E^{*(j)}_{\text{sybil}, \tau}$ and $\bar{D}_\tau = \frac{1}{N_k} \sum_{j=1}^{N_k} D^{(j)}_\tau$. Compute sample variances $s^2_\tau$ and $s^2_{D, \tau}$, and standard errors $\mathrm{SE}_\tau = s_\tau / \sqrt{N_k}$, $\mathrm{SE}(D_\tau) = s_{D, \tau} / \sqrt{N_k}$. Calculate operative Studentized confidence bounds under joint sequential FWER Bonferroni standard ($|\mathcal{M}| = 57$, $\alpha_{\text{FWER}} = 10^{-3}$, $t_{\text{FWER}} = 4.294$): $\mathrm{UCB}_{\text{FWER}}(\mathbb{E}[E^*_\tau]) = \bar{E}^*_\tau + t_{\text{FWER}} \cdot \mathrm{SE}_\tau$, $\mathrm{LCB}_{\text{FWER}}(\mathbb{E}[E^*_\tau]) = \bar{E}^*_\tau - t_{\text{FWER}} \cdot \mathrm{SE}_\tau$, $\mathrm{UCB}_{\text{FWER}}(\mathbb{E}[\Delta E^*_\tau]) = \bar{D}_\tau + t_{\text{FWER}} \cdot \mathrm{SE}(D_\tau)$, $\mathrm{LCB}_{\text{FWER}}(\mathbb{E}[\Delta E^*_\tau]) = \bar{D}_\tau - t_{\text{FWER}} \cdot \mathrm{SE}(D_\tau)$. (Unadjusted pointwise bounds $\mathrm{LCB}_{0.999}$/$\mathrm{UCB}_{0.999}$ using $t_{\text{crit}} = 3.090$ serve solely as secondary descriptive statistics).
- **Pass/Fail & Inconclusive Criteria (Exhaustive Ternary Rule with Deterministic Priority & Disjoint Partitions under Operative Group-Sequential FWER Control)**:
  - **Deterministic Priority Order**: **Priority 1: FAIL check $\to$ Priority 2: PASS check $\to$ Priority 3: INCONCLUSIVE check**.
  - **Statistical Guarantees Scope**: Authoritative global decision rule strictly enforces Family-Wise Error Rate (FWER) control across the complete group-sequential multiplicity family of $|\mathcal{M}| = 57$ comparisons (19 endpoints per look $\times$ 3 sequential looks [initial $N=5000$, retry 1 $N=10000$, retry 2 $N=20000$]) via Bonferroni correction at $\alpha_{\text{FWER}} \le 10^{-3}$ (adjusted $\alpha_{\text{adj}} = 1.754386 \times 10^{-5}$, two-sided critical value $t_{\text{FWER}} = 4.294$). Pointwise critical value $t_{\text{pointwise}} = 3.090$ is documented solely as an unadjusted baseline.
  - **Parameters**: $\epsilon_{\text{tol}} = 0.02$, $\mathrm{SE}_{\max} = 0.015$, $|\mathcal{T}| = 9$ (canonical stopping rules: `tau_fixed_50`, `tau_fixed_100`, `tau_fixed_250`, `tau_fixed_500`, `tau_theta_1.5`, `tau_theta_2.0`, `tau_theta_5.0`, `tau_theta_10.0`, `tau_drawdown`), endpoints per look $M_{\text{look}} = 19$, maximum sequential looks $K_{\max} = 3$, total comparisons $|\mathcal{M}| = 57$, $\alpha_{\text{FWER}} = 0.001$, $\alpha_{\text{adj}} = 1.754386 \times 10^{-5}$, $t_{\text{FWER}} = 4.294$, $t_{\text{pointwise}} = 3.090$, retry budget $B_{\max} = 2$ extensions, sample schedule $[5000, 10000, 20000]$, Ville $\lambda = 20.0$, Ville bound $\alpha_{\text{Ville}} = 0.05$, Ville threshold $\hat{P}_{\max} = 0.0632$ (at $N_1 = 5,000$).
  - **Priority 1 (FAIL / Invariant Falsified)**: Triggers if at ANY sequential look $k \in \{1, 2, 3\}$ for ANY comparison in the 19 endpoints: (1) Empirical lower confidence bound $\mathrm{LCB}_{\text{FWER}}(\mathbb{E}[E^*_\tau]) = \bar{E}^*_\tau - 4.294 \cdot \mathrm{SE}_\tau > 1.0$ (statistically significant wealth growth above supermartingale bound under joint sequential FWER $\le 10^{-3}$); OR (2) Paired Sybil excess lower confidence bound $\mathrm{LCB}_{\text{FWER}}(\mathbb{E}[\Delta E^*_\tau]) = \bar{D}_\tau - 4.294 \cdot \mathrm{SE}(D_\tau) > 0.0$; OR (3) Empirical maximal tail lower bound $\hat{P}_{\text{LCB, FWER}}(\sup_{t \le 500} E^*_t \ge 20) = \hat{P} - 4.294 \sqrt{\frac{\hat{P}(1-\hat{P})}{N_k}} > 0.05$ (violating Ville's maximal inequality under joint sequential FWER $\le 10^{-3}$). If any FAIL condition is met, the verdict is immediately FAIL regardless of upper bounds or remaining retry budget.
  - **Priority 2 (PASS / Invariant Validated within Bounded Tolerance)**: Triggers if and only if Priority 1 does NOT trigger AND for ALL 19 comparisons at the current look $k$: (1) Portfolio wealth satisfies $\mathrm{LCB}_{\text{FWER}}(\mathbb{E}[E^*_\tau]) \le 1.0$ AND $\mathrm{UCB}_{\text{FWER}}(\mathbb{E}[E^*_\tau]) = \bar{E}^*_\tau + 4.294 \cdot \mathrm{SE}_\tau \le 1.0 + \epsilon_{\text{tol}}$ (with $\epsilon_{\text{tol}} = 0.02$ and observed $\mathrm{SE}_\tau \le \mathrm{SE}_{\max} = 0.015$); AND (2) Paired Sybil excess satisfies $\mathrm{LCB}_{\text{FWER}}(\mathbb{E}[\Delta E^*_\tau]) \le 0.0$ AND $\mathrm{UCB}_{\text{FWER}}(\mathbb{E}[\Delta E^*_\tau]) = \bar{D}_\tau + 4.294 \cdot \mathrm{SE}(D_\tau) \le \epsilon_{\text{tol}}$ (with observed $\mathrm{SE}(D_\tau) \le \mathrm{SE}_{\max} = 0.015$, where the joint FWER Bonferroni criterion for mean paired Sybil excess constitutes the sole authoritative Sybil endpoint); AND (3) Empirical maximal tail satisfies $\hat{P}_{\text{LCB, FWER}}(\sup_{t \le 500} E^*_t \ge 20) \le 0.05$ AND $\hat{P}(\sup_{t \le 500} E^*_t \ge 20) \le 0.05 + 4.294 \sqrt{\frac{0.05 \cdot 0.95}{N_k}}$ ($0.0632$ at $N_1 = 5,000$; $0.0594$ at $N_2 = 10,000$; $0.0566$ at $N_3 = 20,000$).
  - **Priority 3 (INCONCLUSIVE / Power Insufficient)**: Triggers if and only if NEITHER Priority 1 (FAIL) NOR Priority 2 (PASS) is met at look $k$ (i.e. all $\mathrm{LCB}_{\text{FWER}} \le \text{null}$ thresholds, but $\mathrm{UCB}_{\text{FWER}} > 1.0 + \epsilon_{\text{tol}}$ or $\mathrm{UCB}_{\text{FWER}}(\Delta) > \epsilon_{\text{tol}}$ or $\hat{P} > 0.05 + 4.294 \sqrt{\frac{0.05 \cdot 0.95}{N_k}}$ or observed $\mathrm{SE}_\tau > \mathrm{SE}_{\max} = 0.015$). In this indeterminate region, if look $k < 3$ ($k \in \{1, 2\}$), execute deterministic sample extension: double sample size $N_{k+1} \leftarrow 2 N_k$ ($N_2 = 10,000$, $N_3 = 20,000$) using child RNG stream `SeedSequence(20261102).spawn(k+1)` and re-evaluate at look $k+1$. If indeterminate after $B_{\max} = 2$ extensions ($k = 3, N_3 = 20,000$), terminate deterministically with status `INCONCLUSIVE_RETRY_BUDGET_EXHAUSTED`, halting automated execution and requiring model recalibration rather than ambiguous pass/fail.
- **Cheapest Test**: 120-line vectorized NumPy simulation of $N = 5,000$ paired Monte Carlo runs ($T_{\max} = 500$ steps, seed `20261102`) with adaptive sample doubling up to $B_{\max} = 2$ extensions ($N = 10,000 \to 20,000$). Evaluates $\mathrm{UCB}_{\text{FWER}}$, $\mathrm{LCB}_{\text{FWER}}$, paired delta, Ville bound, and ternary decision logic across complete group-sequential multiplicity family $|\mathcal{M}| = 57$ in $< 3.5$ seconds on commodity CPU, $0 external API spend, 0 external mutations.

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
- **Cheapest Test**: Ultra-low-cost local subshell script: child writes PID and sleeps; parent terminates abruptly with exit 137. Dispatch verifier inspects `/proc` or `ps` output to confirm child survived. Run time $< 1.0$s ($< 3.5$s), commodity CPU, $0 external quota.
