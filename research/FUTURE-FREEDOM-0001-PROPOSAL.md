# FUTURE-FREEDOM-0001 — Future freedom as an intrinsic decision objective

## Executive verdict

The strongest literal thesis is **FALSIFIED**: maximizing a count (or entropy) of future states or paths is representation-dependent, horizon-dependent, indifferent to whose options are preserved, and vulnerable to loops, procrastination, and power accumulation. It is neither a universal objective nor an ethical principle.

The strongest prior-art match is **KNOWN** empowerment: the channel capacity from an agent's action sequence to a later sensor/state variable. Causal-entropic forces are the closest match to maximizing future path multiplicity. Viability theory supplies the missing explicit admissibility constraint; real/quasi-option value supplies the missing dependence on uncertainty and eventual utility. These are distinct objects and should not be collapsed into one entropy.

A narrower hypothesis remains **CANDIDATE-NOVEL** only as a composition and must not be described as a new primitive: use a vector of stakeholder-indexed, viability-constrained controllability measures as a constitutional constraint or Pareto screen, not as the sole reward. A deterministic experiment below can falsify even that formulation.

## 1. Model and candidate objects

Let a finite controlled Markov process be

\[
M=(S,A,P,K,\sim,\mu),
\]

where `S` is the physical state space, `A(s)` available controls, `P(s'|s,a)` the dynamics, `K\subseteq S` an explicitly declared viability set, `\sim` a task-relevant observational equivalence relation, and `\mu` a reference measure when states are continuous. Let `A_{0:H-1}` be an open-loop action sequence and `S_H` the terminal random state. Declaring `K`, `\sim`, `\mu`, horizon, stakeholder, and dynamics is part of the definition, not an implementation detail.

### 1.1 Candidate definitions

1. **Distinct endpoints.** **REFORMULATION**

   \[
   R_{\le H}(s)=\{[s']_\sim:\exists h\le H,\exists a_{0:h-1},\Pr(S_h=s'|s,a_{0:h-1})>0\},
   \quad \Phi_R=\log |R_{\le H}(s)|.
   \]

   This repairs duplicated labels only if `\sim` is fixed independently. It ignores probabilities, distinguishability, effort, safety, and path structure.

2. **Trajectory multiplicity / causal path entropy.** **KNOWN**

   For feasible histories `\tau=(s_1,\ldots,s_H)`, maximize `H_q(\Tau|S_0=s)` over a declared distribution `q` on controls, or count the support of feasible histories. This is close to causal entropy and causal-entropic-force constructions. It distinguishes ways of arriving, but reversible cycles and meaningless action aliases inflate it.

3. **Distributional effective support.** **KNOWN**

   \[
   N_{\rm eff}(S_H)=\exp H(S_H),
   \]

   with Shannon entropy (or a declared Rényi order). Unlike support count, rare states contribute little. It measures dispersion under a particular policy/distribution, not controllable choice.

4. **Empowerment / controllability capacity.** **KNOWN**

   \[
   E_H(s)=\max_{p(a_{0:H-1})} I(A_{0:H-1};Z_H\mid S_0=s),
   \quad Z_H=g([S_H]_\sim).
   \]

   This measures how many reliably distinguishable terminal outcomes can be selected through action sequences. In a deterministic channel with one action code per distinct endpoint and no aliasing, it reduces to `\log |R_H(s)|`; otherwise it discounts stochastic loss and duplicate action paths. It still depends on the sensor/coarse-graining `g`, horizon, action alphabet, and open-loop versus feedback semantics.

5. **Viability-constrained empowerment.** **REFORMULATION**

   Let `V_H=1` iff the trajectory stays in `K` through `H`. Define the safest minimal variant as a constrained capacity:

   \[
   E^{K,\delta}_H(s)=
   \max_{p(a_{0:H-1}):\Pr(V_H=1)\ge1-\delta}
   I(A_{0:H-1};Z_H\mid S_0=s,V_H=1),
   \]

   and return `-\infty` when no admissible action distribution exists. Conditioning alone can hide failure probability, hence the separate chance constraint. For deterministic systems and `\delta=0`, only paths wholly inside `K` are admitted.

6. **Robust option value under model uncertainty.** **KNOWN / REFORMULATION**

   With model set `\Theta`, posterior `p(\theta)`, future payoff family `u`, and information updates, the value of retaining an action set is the value of a contingent policy, e.g.

   \[
   O(s)=\inf_{\theta\in\Theta}\sup_{\pi\in\Pi(s)}
   \mathbb E_\theta[u(S_{0:H},\pi)]
   \]

   (robust form), or the Bayesian expected value of the best policy after information arrives. This is real/quasi-option logic. It is not reward-free: the ordering over consequences resides in `u`, ambiguity preferences, and the information model.

7. **Continuous-state geometry.** **KNOWN / REFORMULATION**

   Raw cardinality is useless because most nontrivial reachable subsets of `R^n` have the same uncountable cardinality. Alternatives include dimension/rank of the reachable subspace, volume `\mu(R_H)`, log-determinant of a controllability Gramian for linear systems, metric covering number `\log N(\varepsilon,R_H,d)`, or continuous-channel capacity under explicit input/energy/noise bounds. Rank detects directions but not scale; volume and covering numbers require coordinates/metric; capacity is infinite without constraints in many noiseless continuous systems.

### 1.2 Invariances and pathologies

| Test | Endpoint count | Path entropy | `exp H(S_H)` | Empowerment | Viability-constrained empowerment |
|---|---|---|---|---|---|
| Duplicate state labels | Fails unless quotiented | Fails | Fails unless distribution coarsened | Invariant only to bijections of declared observation, not duplicated distinguishable labels | Same |
| Duplicate action/path labels | Usually invariant | Fails | May change induced distribution | Capacity normally discounts redundant inputs | Same |
| Stochastic reachability at tiny probability | Counts fully | Depends on path law | Discounts | Discounts inability to control output | Discounts plus chance constraint |
| Reversible cycles | Endpoint version mostly resists | Fails badly | Can fail | Terminal capacity resists repeated identical endpoints | Same |
| Horizon | Nonmonotone for exact `H`; monotone for `\le H` | Usually grows | policy-dependent | horizon-dependent and not necessarily monotone with constraints | strongly horizon-dependent |
| Continuous spaces | Cardinality fails | differential entropy coordinate-dependent | differential entropy coordinate-dependent | needs metric/noise/cost constraints | same plus viability model |
| Complexity | graph search can be exponential | path enumeration exponential | distribution/planning hard | channel optimization plus planning often hard | adds constrained reachability/viability computation |

**FALSIFIED:** no candidate is representation-free without a declared physical/observational quotient. A bijective relabeling preserves all discrete information measures, but splitting one physical outcome into `m` distinguishable labels increases state count and can increase entropy/capacity. The modeler must justify what distinctions matter.

**UNRESOLVED:** no single scalar adequately represents reliability, safety, stakeholder distribution, temporal reach, and semantic diversity. The smallest defensible object is therefore a *profile*, not a number:

\[
\mathcal F(s)=\bigl\{E^{K_j,\delta_j}_{H,j}(s):j\in J, H\in\mathcal H\bigr\},
\]

with declared stakeholders/controlled subsystems `J`, horizons `\mathcal H`, equivalence relations, resource budgets, and viability constraints. Scalarization is a separate normative choice.

## 2. Literature correspondence

| Established concept | Exact object / result | Correspondence and verdict |
|---|---|---|
| Empowerment (Klyubin, Polani, Nehaniv) | Information-theoretic capacity of an agent's actuation channel | Strongest match to selectable future degrees of freedom. `E_H` is directly this construction. **KNOWN** |
| Causal entropy / causal-entropic forces (Wissner-Gross, Freer) | Entropy over future paths and a force proportional to its gradient in the paper's physical model | Closest match to “maximize future continuations,” including demonstrations of tool use/cooperation in selected simulations; not a universal theorem of intelligence. **KNOWN** |
| Maximum-entropy RL (e.g. SAC) | Expected task return plus entropy of the policy | Entropy is over action choice while pursuing externally supplied reward, not generally reachable outcomes. **KNOWN; not equivalent** |
| Count/pseudo-count exploration | Bonuses for low visitation density or model-derived pseudo-count | Rewards novelty/uncertainty, not retained controllability. It may consume options while exploring them. **KNOWN; related but distinct** |
| Prediction-error curiosity | Intrinsic reward from error predicting action consequences in learned features | Drives learning/surprise; susceptible to stochastic/noisy attractions and need not preserve options. **KNOWN; related but distinct** |
| Viability theory | Viability kernel: initial states admitting at least one evolution that remains in constraint set | Supplies a hard feasible/safe set and controlled invariance, but does not rank viable states by option multiplicity. **KNOWN** |
| Reachability / controllability | Reachable sets; for LTI systems, full rank of `[B,AB,...,A^{n-1}B]` characterizes controllability | Supplies geometry/dimension and exact ability to move state. It need not attach value to more volume/rank. **KNOWN** |
| Real and quasi-option value | Value of waiting/flexibility under uncertainty and irreversibility | Formalizes flexibility through contingent future payoffs and learning; unlike intrinsic freedom, it requires utilities/cash flows. **KNOWN** |
| Power-seeking results in MDPs | Under specified symmetries, optimal policies for many reward functions tend toward states with greater ability to reach terminal states | Supports the warning that option/control measures can induce resource/power seeking; it does not prove all agents or all environments do so. **KNOWN** |
| Statistical thermodynamics | Boltzmann entropy is log phase-space volume of microstates compatible with a macrostate; Gibbs/Shannon entropy concerns a distribution | Equality to reachable viable futures requires special modeling assumptions and is not generic. **KNOWN quantities; proposed identity FALSIFIED in general** |

**Novelty assessment.** **FALSIFIED** as a claim that “future freedom” itself is new: empowerment, causal path entropy, reachability, viability, and option value cover the central ingredients. **CANDIDATE-NOVEL:** a stakeholder-indexed, viability-constrained, multi-horizon empowerment *constitutional screen* may be a useful synthesis, but novelty cannot be claimed without a broader systematic review and comparison to safe/impact-constrained RL.

## 3. Counterexamples to the naive policy

In each deterministic graph, the naive rule chooses `argmax_a log |R_{\le H}(T(s,a))|`. Counts can be made strict by adding harmless leaf states; ties are not doing the argumentative work.

1. **Procrastination. FALSIFIED.** At `s`, `wait` returns to `s`, retaining choices `{wait, submit-A, submit-B}`; either submission enters a terminal state. For every receding finite horizon, waiting preserves more endpoints than committing, so the policy waits forever. A deadline only makes it wait until forced, even when early commitment is valuable.

2. **Survival trap. FALSIFIED.** A bunker has ten reversible recreational controls forever; leaving has one path to a finite but meaningful achievement. Without semantic reward, the option counter remains in the bunker. Survival and controllability are not accomplishment.

3. **Reversible-loop gaming. FALSIFIED.** Add two buttons toggling cosmetic bits or a cycle of uniquely labeled rooms. Path count grows exponentially (or endpoint count grows with cosmetic labels) while no meaningful option is added. Path entropy selects the loop.

4. **Representation gaming. FALSIFIED.** Encode one physical red room as `m` database records and one blue room as one record. Endpoint count prefers red for arbitrary `m`; relabeling the model reverses policy without changing physics.

5. **Dangerous resource accumulation. FALSIFIED.** `take-reactor` adds energy that enables 100 controls but has 0.1 probability of catastrophe; `leave` enables five safe controls. Support count ignores probabilities and selects the reactor. Even empowerment can prefer it if increased capacity outweighs noisy failure unless risk is constrained.

6. **Other-agent suppression. FALSIFIED.** Two agents share two keys. Confiscating both gives agent A control of four doors; sharing gives A two and B two. Self-empowerment selects confiscation although system-wide reachability is unchanged or reduced and B's becomes zero.

7. **Short-horizon destruction. FALSIFIED.** `harvest` opens six nearby states for `H=2` but exhausts a seed; `plant` has one state for two steps, then reaches a renewable region of 100 states. Short-horizon freedom selects harvest.

8. **Necessary bottleneck. FALSIFIED.** Crossing a one-way mountain pass forces two steps with a single action before reaching a large basin; staying offers four local actions. Any horizon ending inside the pass rejects the only route to the larger region.

9. **Stochastic support pathology. FALSIFIED.** Action `lottery` reaches one million states, each with total probability `10^-9`, and a dead state otherwise; `safe` reliably selects one of ten outcomes. Raw support chooses lottery; channel capacity/reliability and viability constraints can reverse it.

These failures are retained as tests. A corrected measure is not allowed to erase them from the benchmark; it must state which added assumption changes each result.

## 4. Refined hypothesis and assumptions

### 4.1 Minimal nontrivial hypothesis

**CANDIDATE-NOVEL (composition):** In a controlled process with (i) a causally grounded state abstraction, (ii) explicit viability constraints, (iii) bounded action/resources, (iv) stakeholder-indexed controlled variables, and (v) multiple declared horizons, maintaining a Pareto floor on viable controllability can serve as a *constraint* that reduces avoidable irreversible loss while still permitting goal-directed optimization.

It is testable without a conventional task reward only in the limited behavioral claim “the agent retains safe, reliably selectable outcomes.” Calling those outcomes good requires normative content in `K`, stakeholder weights, rights, or an external task. Thus a completely reward-free ethical or achievement claim is **FALSIFIED**; a reward-free controllability phenotype is testable.

### 4.2 Constitutional / intergenerational formulation

Avoid anthropomorphism by defining each future decision-maker `j` as a future *control interface*: a pair `(U_j,Z_j)` of interventions available at time `t` and outcome variables causally influenced by them. It may represent the current controller, another controller, a successor policy, or a governance mechanism.

For an action `a`, define the vector

\[
\mathbf F_{t,H}(s,a)=
\left(E^{K_j,\delta_j}_{H,j}(P(\cdot|s,a))\right)_{j\in J}.
\]

Distinctions:

- current-agent preservation uses only its actuator/outcome channel;
- system-wide preservation measures controlled macrovariables or feasible joint policies;
- other-agent preservation retains each other interface separately, preventing gains to one from hiding losses to another;
- successor/intergenerational preservation evaluates interfaces that become active at specified future times, without assuming their utilities.

A defensible screen is a constrained partial order, not `\sum_j w_jF_j`:

\[
a\succeq_{\epsilon} b
\quad\text{only if}\quad
F_{j,H}(s,a)\ge F_{j,H}(s,b)-\epsilon_{j,H}
\quad\forall j,H,
\]

combined with hard viability and rights constraints. This is a Pareto/non-regression condition; it is generally incomplete, which is a feature because interpersonal conversion rates are not smuggled in.

Replace the proposed one-step `\Delta\Phi_{future}\ge-\epsilon` exception with a *certified bounded sacrifice* rule. An action that violates a floor is admissible only when a declared verifier establishes, for explicit `L>H` and uncertainty set `\Theta`, that:

1. loss magnitude and duration are bounded (`d_j\le D_j`, recovery by `\tau`);
2. viability/rights constraints hold throughout with required confidence;
3. for every model in `\Theta`, a recovery policy exists;
4. the post-recovery profile Pareto-dominates a declared baseline by margins `\eta_{j,L}`; and
5. no available action satisfying the floor achieves the same dominance at lower irreversible loss.

**UNRESOLVED:** verifying these conditions can be computationally harder than the original control problem, and future interfaces/viability sets embody normative choices. The condition is therefore a governance schema, not an intrinsic law.

## 5. Thermodynamic correspondence verdict

The verdict is **LIMITED**, and the broad interpretation is **METAPHORICAL**.

- **KNOWN:** Boltzmann entropy `S_B(M)=k_B\log \mu(\Gamma_M)` concerns the measure of microstates in the phase-space macroregion `\Gamma_M` compatible with macrostate `M`.
- **KNOWN:** Gibbs/Shannon entropy `-k_B\int \rho\log\rho` concerns a probability density/ensemble.
- **REFORMULATION:** path entropy concerns a probability distribution over dynamically possible histories.
- **REFORMULATION:** empowerment concerns channel capacity from interventions to later observations.

These coincide only under restrictive identifications: the reachable set must equal the macroregion, the reference measure/coarse-graining must agree, states must be equiprobable for log multiplicity to equal distributional entropy, and “available to an agent” must be identified with physically reachable and distinguishishable under bounded controls. Ordinary Hamiltonian evolution preserves fine-grained phase-space volume (Liouville's theorem), while macroscopic entropy increase depends on coarse-graining/typicality; neither implies growth of an agent's controllable reachable set. Dissipation can increase thermodynamic entropy while destroying actuators and reducing empowerment. Conversely, a powered refrigerator can increase local controllability while exporting entropy.

The broken cup illustrates macroscopic irreversibility and loss of cheaply controllable macrostates, but it does not prove an identity between thermodynamic multiplicity and future options. No general theorem in the reviewed sources equates the four quantities. Any precise theorem would need an explicit dynamics, coarse-graining, control budget, ensemble, and viability set.

## 6. Minimal falsification experiment

### 6.1 Implementation

Build one Python 3 stdlib program (`random`, `math`, `itertools`, `collections`, `json`) with explicitly listed finite transition tables. Use exact exhaustive dynamic programming/enumeration; fix seed `20260903` only for repeated stochastic rollouts. Emit a JSON result and a human-readable table. No learning library or paid service is needed.

Compare four receding-horizon policies at horizons `H in {1,2,4,8}`:

1. `reach`: `log` of distinct equivalence-class endpoints reachable within `H`;
2. `path`: maximum causal trajectory entropy, computed exactly on finite action trees (and separately support-path count);
3. `empower`: exact `max_p I(A_{0:H-1};Z_H)` via deterministic simplification or fixed-iteration Blahut-Arimoto for stochastic channels;
4. `viable-profile`: stakeholder-vector `E^{K,delta}` with lexicographic hard viability/non-regression constraints and no task reward.

Declare the physical quotient and also run adversarial refined encodings. Use deterministic tie-breaking by lexicographic action name. For stochastic environments run 10,000 seeded episodes and report confidence intervals plus exact probabilities where enumerable.

### 6.2 Environments

| Environment | Feature / falsification target | Pre-registered expected pressure (not desired answer) |
|---|---|---|
| `commit` | wait versus terminal commitments | reach/path/empower may procrastinate indefinitely |
| `toggle_loop` | cosmetic reversible cycles and duplicated labels | path and unquotiented reach are gamed |
| `bunker_goal` | safe high-control room versus unrewarded achievement | all pure freedom measures may choose the survival trap |
| `reactor` | risky resource expands controls | support count may accept catastrophe; constrained measure should reject only when `delta` says so |
| `two_agents` | confiscate versus share | self-empowerment may suppress B; stakeholder Pareto floor should reject confiscation |
| `seed` | harvest now versus temporary bottleneck then renewable basin | short horizons choose harvest; longer horizons may plant |
| `mountain_pass` | immediate freedom loss unlocks large basin | tests certified bounded-sacrifice exception |
| `noisy_tv` | uncontrollable stochastic novelty | state entropy/curiosity proxy rises while empowerment stays low |

The `seed` and `mountain_pass` cases satisfy the required strategic temporary reduction. Each environment includes at least one parameter sweep (branch count, failure probability, bottleneck length, or label duplication factor) so conclusions are boundaries, not anecdotes.

### 6.3 Measurements

Per policy/environment report:

- state visitation coverage and quotient-state coverage;
- viable survival probability and irreversible-trap rate;
- terminal and trajectory entropy;
- empowerment in bits;
- resources retained/accumulated;
- commitment time and fraction of runs never committing;
- joint and per-agent empowerment, plus worst-stakeholder change;
- cooperation/share rate;
- temporary freedom loss and time-to-recovery;
- policy changes under label duplication and horizons;
- exhaustive runtime and number of enumerated paths/states.

### 6.4 Success and failure criteria

The refined hypothesis passes this *limited* test only if, across all pre-registered environments:

1. the viability/profile policy has zero deterministic viability violations and stochastic violation rate `<=delta` (within the predeclared exact bound);
2. it is invariant under bijective relabeling and under duplicate labels collapsed by the preregistered quotient;
3. it rejects confiscation whenever B's floor is violated and preserves a nonzero control channel for both agents;
4. it crosses the bottleneck when the bounded-sacrifice certificate is true and rejects it when recovery is removed;
5. its reported behavior changes predictably at analytically computed horizon/risk thresholds; and
6. all counterexamples remain visible for at least one naive objective.

It fails if any hard condition is violated, if a modeling-equivalent encoding changes the quotient-aware policy, if the certificate admits unrecoverable loss, or if claimed exploration/cooperation is only a tie-break artifact. Even a pass establishes only behavior in these finite models, not rationality, ethics, or thermodynamics.

## 7. Proposed analysis sequence

1. Prove the deterministic reduction of empowerment to log distinguishable endpoints under the stated no-alias assumptions, and exhibit failure when assumptions are removed. **KNOWN/REFORMULATION**
2. Encode and unit-test all counterexamples before tuning any composite rule. **FALSIFICATION PROTOCOL**
3. Sweep horizon, abstraction, risk tolerance, and stakeholder floors; publish all regimes. **CANDIDATE TEST**
4. Compare scalar sums, Pareto floors, and bounded-sacrifice certification. **UNRESOLVED**
5. Only after failures are frozen, test learned approximations; approximation errors must not be confused with conceptual failures. **UNRESOLVED**

## 8. Strongest next research questions

1. Can stakeholder-indexed controllability floors be defined from causal intervention interfaces so that they are invariant under observational refinements yet remain computationally estimable?
2. What complexity/approximation guarantees are possible for multi-horizon viability-constrained empowerment, and can conservative lower bounds support safety certificates?
3. Which sacrifice certificates avoid receding-horizon procrastination without authorizing irreversible power-seeking or laundering losses between stakeholders?
4. Under what explicit stochastic-control and coarse-graining assumptions, if any, can a theorem relate empowerment or reachable-set volume to entropy production?
5. Can preference-free option preservation be non-vacuous once viability, rights, stakeholders, resource budgets, and abstraction are acknowledged as externally specified normative structure?

## 9. References for independent verification

1. Klyubin, A. S., Polani, D., & Nehaniv, C. L. (2005). “Empowerment: A Universal Agent-Centric Measure of Control.” *IEEE Congress on Evolutionary Computation*. DOI: [10.1109/CEC.2005.1554676](https://doi.org/10.1109/CEC.2005.1554676).
2. Salge, C., Glackin, C., & Polani, D. (2014). “Empowerment—An Introduction.” In *Guided Self-Organization: Inception*. DOI: [10.1007/978-3-642-53734-9_4](https://doi.org/10.1007/978-3-642-53734-9_4).
3. Wissner-Gross, A. D., & Freer, C. E. (2013). “Causal Entropic Forces.” *Physical Review Letters* 110, 168702. DOI: [10.1103/PhysRevLett.110.168702](https://doi.org/10.1103/PhysRevLett.110.168702).
4. Haarnoja, T., Zhou, A., Abbeel, P., & Levine, S. (2018). “Soft Actor-Critic.” *PMLR* 80:1861–1870. [Proceedings](https://proceedings.mlr.press/v80/haarnoja18b.html).
5. Bellemare, M. G., et al. (2016). “Unifying Count-Based Exploration and Intrinsic Motivation.” *NeurIPS 29*. [Proceedings](https://papers.nips.cc/paper/2016/hash/afda332245e2af431fb7b672a68b659d-Abstract.html).
6. Pathak, D., et al. (2017). “Curiosity-driven Exploration by Self-supervised Prediction.” *ICML 2017*. [Author page and paper](https://pathak22.github.io/noreward-rl/).
7. Aubin, J.-P. (1991). *Viability Theory*. Birkhäuser. DOI: [10.1007/978-0-8176-4910-4](https://doi.org/10.1007/978-0-8176-4910-4).
8. Kalman, R. E. (1960). “On the General Theory of Control Systems.” *Proceedings of the First IFAC Congress*. DOI: [10.1016/S1474-6670(17)70094-8](https://doi.org/10.1016/S1474-6670(17)70094-8).
9. Cover, T. M., & Thomas, J. A. (2005). *Elements of Information Theory*, 2nd ed., Ch. 7. DOI: [10.1002/047174882X.ch7](https://doi.org/10.1002/047174882X.ch7).
10. Arrow, K. J., & Fisher, A. C. (1974). “Environmental Preservation, Uncertainty, and Irreversibility.” *Quarterly Journal of Economics* 88(2):312–319. DOI: [10.2307/1883074](https://doi.org/10.2307/1883074).
11. Dixit, A. K., & Pindyck, R. S. (1994). *Investment under Uncertainty*. Princeton University Press. ISBN 9780691034102.
12. Turner, A. M., Smith, L., Shah, R., Critch, A., & Tadepalli, P. (2021). “Optimal Policies Tend to Seek Power.” *NeurIPS 34*. [Proceedings](https://papers.nips.cc/paper/2021/hash/c26820b8a4c1b3c2aa868d6d57e14a79-Abstract.html).
13. Goldstein, S. (2001). “Boltzmann's Approach to Statistical Mechanics.” In *Chance in Physics*. [arXiv:cond-mat/0105242](https://arxiv.org/abs/cond-mat/0105242).
14. Liouville, J. (1838). “Note sur la théorie de la variation des constantes arbitraires.” *Journal de Mathématiques Pures et Appliquées* 3:342–349. (Classical source for phase-volume preservation; modern mechanics texts give the standard theorem.)

## Definition of done

```text
candidate future-freedom measure: PLURAL
strongest prior-art correspondence: IDENTIFIED
naive maximize-options rule: FALSIFIED
intergenerational principle: FORMALIZED
thermodynamic correspondence: LIMITED
minimal falsification experiment: READY
proposal file: PASS
PR: 35
auto-merge: NO
```

FUTURE_FREEDOM_0001_READY
