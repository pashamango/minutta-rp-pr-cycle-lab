# Bounded Falsification Specifications (Top 3 Candidates)
**Task Reference:** MIN-18 | **Author:** `agy@wolfram`  
**Status:** CANDIDATE / NOT EXECUTION-AUTHORIZED  
**Applicable Protocol:** Mindrock Agent Constitution (AGENTS.md)  

---

## 1. Specification Overview

Following the Mindrock epistemic protocol, hypotheses are not adopted by self-declaration or consensus assertion, but only through **bounded, non-destructive falsification experiments**. Below are the complete specifications for the top 3 ranked candidate invariants from the Invariant Graph.

---

## 2. Specification 1: Conserved Evidence Portfolio Simplex & Matched Search-Budget Invariant

### 2.1 Coordinate Identification
- **Spec ID:** `FALSIF-SPEC-001` (Rank 1)
- **Anchor Claim:** `CLAIM-011` ([Issue #168 Comment 5649859218](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5649859218))
- **Domain:** `CROSS-PROJECT / SCIENCE + OPEN-MONEY + AGENT-EVALUATION`
- **Lead Scheduler:** Discovery Steward

### 2.2 Formal Invariant Statement
$$\forall \mathcal{H}_i, \quad E^* = \sum_{i=1}^m w_i E_i, \quad \text{with } w \in \Delta_m, \quad \sum_{i=1}^m w_i = 1$$
Epistemic stake across autonomous scheduler forking is conserved on a unit simplex. Schedulers and subagents may fork arbitrarily, but their aggregated evidence $E^*$ under null hypothesis $P_0$ satisfies:
$$\mathbb{E}_{P_0}[E^*] \le 1$$
Identity splitting (Sybil forking) or transport redundancy multiplication ($	ext{redundancy} \neq \text{value}$) increases availability, but cannot increase spendable evidence rank without consuming independent information.

### 2.3 Null Hypothesis ($H_0$) & Alternative ($H_1$)
- **$H_0$ (Selection & Sybil Confound):** In-sample evidence wealth growth in multi-agent adaptive search is fully explained by uncorrected selection bias ($N$ trials yielding in-sample max $\approx \sqrt{2 \ln N}$) and multi-identity split reporting. Under $H_0$, expected log e-wealth drift is non-positive: $\mathbb{E}[\ln E^*] \le 0$.
- **$H_1$ (Conserved Simplex Robustness):** The fixed weighted arithmetic average $E^*$ preserves the valid e-process martingale property (admissible merge under Wang 2025) and neutralizes Sybil splitting under arbitrary dependence.

### 2.4 Bounded Falsification Procedure
1. **Null Stream Generation:** Generate $100$ independent synthetic noise streams $X_t \sim \mathcal{N}(0, 1)$ over $T=500$ steps.
2. **Adversarial Sybil Attack:** At step $t=20$, Agent 1 observes a random positive fluctuation and splits into $10$ clone sub-identities, reporting individual e-values.
3. **Comparative Evaluation:** Evaluate three reporting regimes:
   - *Regime A (Max-Reporting):* $E_{\max} = \max_j E_j$.
   - *Regime B (Independent Unit Ledgers):* Each clone claims full parent weight $w_j = w$.
   - *Regime C (Conserved Simplex Portfolio):* Weights are strictly partitioned $\sum w_j = w$.
4. **Empirical Calibration:** Run $5,000$ Monte Carlo trajectories and calculate Type I inflation and final e-wealth.

### 2.5 Pass / Fail Criteria
- **PASS Threshold:** Portfolio e-wealth under Regime C strictly satisfies $\mathbb{E}[E^*] \le 1.0$ across all stopping times $\tau$, and empirical false discovery rate at threshold $1/\alpha$ is bounded by $\alpha$ (Markov inequality). Identity splitting produces $0\%$ net advantage over a single honest stream.
- **FAIL Threshold (Falsified):** If an actor can generate expected portfolio e-wealth growth $> 1.0$ under the null solely by forking identities or searching $m$ parallel branches without weight partitioning.

### 2.6 Cheapest Test
- **Execution Cost:** 100-line vectorized NumPy script.
- **Runtime:** $< 3.5$ seconds on local Wolfram node.
- **Network / Budget:** $0 external API cost, $0 mutation of infrastructure.

---

## 3. Specification 2: Golden Trinity Permutation-Matched Dirichlet Simplex Invariant

### 3.1 Coordinate Identification
- **Spec ID:** `FALSIF-SPEC-002` (Rank 2)
- **Anchor Claim:** `CLAIM-001` ([Issue #168 Comment 5648693413](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5648693413))
- **Domain:** `SCIENCE / GOLDEN-TRINITY`
- **Lead Scheduler:** Golden Research Step

### 3.2 Formal Invariant Statement
$$(C, B, V) = \left(\frac{1}{2\phi^2}, \frac{1}{2\phi}, \frac{1}{2}\right) \approx (0.191, 0.309, 0.500)$$
The structural triple $(1, \phi, \phi^2)$ represents a genuine optimum in resource allocation over Context ($C$), Behavior ($B$), and Value ($V$) only if its held-out performance exceeds the 95th percentile of an exchangeable symmetric Dirichlet simplex null under permutation-matched selection budgets.

### 3.3 Null Hypothesis ($H_0$) & Alternative ($H_1$)
- **$H_0$ (Coarse 50% Confound):** Any measured empirical advantage of $(1, \phi, \phi^2)$ is entirely an artifact of:
  1. The coarse allocation rule "allocate 50% to future value" (i.e. Indistinguishable from $(0.25, 0.25, 0.50)$); OR
  2. Selection advantage from choosing the best of 6 permutations on in-sample data.
- **$H_1$ (True $\phi$-Specificity):** $(1, \phi, \phi^2)$ achieves held-out superiority over $(0.25, 0.25, 0.50)$ with $p < 0.01$ and ranks in the top $5\%$ of exchangeable Dirichlet controls $\text{Dir}(1,1,1)$.

### 3.4 Bounded Falsification Procedure
1. **Candidate & Control Generation:** Normalize $\phi$-triple to sum to 1. Sample $1,000$ control shapes $(w_1, w_2, w_3)$ from $\text{Dir}(1,1,1)$, plus the coarse heuristic $(0.25, 0.25, 0.50)$.
2. **Permutation Budget Matching:** For each candidate and control shape, evaluate all 6 label permutations on training task embeddings.
3. **In-Sample Selection:** Select the best permutation using training data only; freeze the permutation.
4. **Held-Out Generalization:** Evaluate the frozen shapes across 200 held-out evaluation splits.
5. **Statistical Ranking:** Compute empirical percentile rank of $\phi$ versus Dirichlet controls and paired t-test against $(0.25, 0.25, 0.50)$.

### 3.5 Pass / Fail Criteria
- **PASS Threshold:** $\phi$-shape out-of-sample percentile $\ge 95.0\%$ among Dirichlet controls AND achieves statistically significant superiority over $(0.25, 0.25, 0.50)$ with $p < 0.01$.
- **FAIL Threshold (Falsified):** If held-out percentile $< 95.0\%$ OR difference with $(0.25, 0.25, 0.50)$ has 95% confidence interval spanning zero.

### 3.6 Cheapest Test
- **Execution Cost:** Benchmark on 200 synthetic task vectors using dot-product similarity metrics.
- **Runtime:** $< 2.0$ seconds on Wolfram.
- **Network / Budget:** $0 external cost.

---

## 4. Specification 3: Durable Dispatch-Boundary Process-Binding Invariant

### 4.1 Coordinate Identification
- **Spec ID:** `FALSIF-SPEC-003` (Rank 3)
- **Anchor Claim:** `CLAIM-003` ([Issue #168 Comment 5648743239](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5648743239))
- **Domain:** `SYSTEM / CROSS-HOST EXECUTION`
- **Lead Scheduler:** Hourly Research Market

### 4.2 Formal Invariant Statement
$$\text{IncidentEvidence}(\text{Task}) = (\text{task\_lease\_id}, \text{host\_id}, \text{process\_tree}, \text{leaf\_pid}, \text{wait\_status}, \text{raw\_signal}, \text{rss\_telemetry})$$
An orchestration exit status (e.g. status 137, 255) is an execution-membrane event, not verifiable evidence of leaf process termination or host OOM. Classifying an incident requires process-bound kernel telemetry.

### 4.3 Null Hypothesis ($H_0$) & Alternative ($H_1$)
- **$H_0$:** Wrapper / transport exit codes faithfully identify leaf process exit causes across remote SSH / UDS execution without kernel process-binding records.
- **$H_1$:** Wrapper exit codes frequently disconnect or report synthetic termination (e.g. status 137 via timeout or channel closure) while leaf worker processes remain healthy.

### 4.4 Bounded Falsification Procedure
1. **Synthetic Worker Spawn:** Launch a child process on host Darwin executing a dummy sleep loop.
2. **Membrane Severing:** Abruptly terminate the parent SSH/pipe connection with `SIGPIPE` / network cut.
3. **Telemetry Capture:** Query Darwin kernel process table via local watchdog.
4. **Classification Audit:** Confirm whether dispatcher records `MEMBRANE_FAULT / EVIDENCE_INSUFFICIENT` instead of falsely tagging leaf `OOM / CRASH`.

### 4.5 Pass / Fail Criteria
- **PASS Threshold:** Dispatcher correctly distinguishes broken transport wrapper from leaf process death in 100% of test cases. Status 137 is never reported as OOM without verified kernel SIGKILL.
- **FAIL Threshold (Falsified):** Dispatcher assigns leaf process failure or initiates unconstrained retries based on wrapper exit code alone.

### 4.6 Cheapest Test
- **Execution Cost:** Local bash subshell script with killed parent and verified child PID.
- **Runtime:** $< 1.0$ second.
- **Network / Budget:** $0 external cost.
