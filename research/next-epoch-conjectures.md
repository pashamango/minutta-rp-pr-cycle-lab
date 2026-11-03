# MIN-24 — Next Epoch conjecture and counterexample agenda

Status: `CANDIDATE / NOT EXECUTION-AUTHORIZED`  
Run: `run-95e199047000`
Scope: hypothesis generation from the emergent-attractor core; no claim about the Riemann Hypothesis.

## Outcome

Three bounded, falsifiable directions are ranked below. Each separates what is already a theorem once its assumptions are formalized from the genuinely unproved conjecture. The proposed tests are cheap finite computations or small Lean lemmas; none is evidence for `Re(s)=1/2` by analogy.

## Ranked proposals

### P1 — Positive-kernel attractor contraction (rank 1)

**Conjecture badge (`CONJECTURE`, not theorem):** Let `K` be a finite nonnegative matrix whose row sums are one, with a primitive support graph. On the zero-sum subspace, iterates of `K` contract in the certified (unweighted) `l1` norm at a rate bounded by a computable Dobrushin coefficient `δ(K)<1`. A weighted `l1` variant is admissible only when its weighting and corresponding coefficient are supplied. The emergent attractor is unique modulo the conserved mass.

**Theorem badges (`THEOREM-CONDITIONAL`):** Nonnegativity preserves the positive cone; row-stochasticity preserves total mass; `δ(K)<1` implies one-step contraction in the selected norm. The missing theorem is the bridge from the Lean core's positivity operator to a concrete `K` satisfying primitivity and the norm bound.

**Dependencies:** a finite-state operator definition; a proved cone-preservation lemma; explicit norm and support-graph definitions; a computable `δ(K)` certificate.

**Cheap test:** enumerate all `3x3` row-stochastic rational matrices with denominator at most 8, calculate `δ`, and compare the predicted bound with 30 iterations from every simplex vertex. PASS only if the bound holds for every sample; FAIL if a primitive matrix violates it.

**Negative examples:** the identity and a permutation matrix have positivity and mass preservation but no contraction; a reducible block-diagonal matrix has multiple attractors. These prevent the invalid inference “positive operator implies unique attractor.”

### P2 — Fractal self-similarity is metric-dependent (rank 2)

**Conjecture badge (`CONJECTURE`, not theorem):** For an iterated affine map family `{f_i}` satisfying a separation condition, the attractor's empirical box-counting slope is stable under refinement and agrees with the Hausdorff dimension only under an additional regularity/open-set hypothesis. The “fractal” label should therefore be attached to a metric plus a scale interval, not to a visual fixed point.

**Theorem badges (`THEOREM-CONDITIONAL`):** Contractive maps on a complete metric space have a unique compact Hutchinson attractor; standard separation hypotheses give dimension formulae in specific settings. No theorem transfers those results to an arbitrary emergent-attractor embedding.

**Dependencies:** explicit metric/embedding; Lipschitz constants; separation certificate; predeclared scale range and estimator.

**Cheap test:** use the middle-third Cantor IFS, an overlapping IFS (`x/3`, `x/3+1/6`), and a finite periodic orbit. Estimate occupied-box slopes at 8 dyadic scales. PASS requires the stated stability only for the separated case; FAIL if the claim is made for overlaps or finite orbits.

**Negative examples:** a linearly ordered finite cycle can look self-similar at two scales but has box dimension 0; overlapping maps can have dimension below the similarity dimension. A plot alone is not a proof of scale invariance.

### P3 — Full-support probabilistic bridge (rank 3)

**Conjecture badge (`CONJECTURE`, not theorem):** If a Markov kernel has a common minorization `P(x,·) >= ε μ(·)` with `ε>0` and `μ` has full support, then every nonempty open set receives positive probability at every sufficiently large step from every initial state, and the induced attractor semantics is independent of the initial point in total variation at a geometric rate.

**Theorem badges (`THEOREM-CONDITIONAL`):** Minorization gives a coupling/regeneration bound; full support of `μ` gives positive mass to sets that `μ` charges. The missing bridge is topological: full support must be stated on the actual state space, not inferred from finite samples or a projection.

**Dependencies:** measurable state space; kernel measurability; explicit `ε, μ`; proof that `supp μ` is the whole intended space; TV-distance definition.

**Cheap test:** compare a two-state kernel with all entries positive, a deterministic kernel, and a kernel whose samples are dense in a proper closed subset. Compute exact `P^n(x,U)` for singleton/open test sets. PASS only for the minorized full-support case.

**Negative examples:** an irrational rotation has a dense orbit but zero probability of hitting a prescribed singleton; a kernel supported on a Cantor subset is “full support” only relative to that subset, not the ambient interval. Dense samples are not full-support proof.

## Zeta guardrail

The critical line `Re(s)=1/2` is a hypothesis-generator only. None of P1–P3 maps an operator spectrum to zeta zeros, establishes an analytic continuation identity, or proves zero-free regions. Any future zeta claim needs an explicit transform, domain, convergence/continuation theorem, and a falsifiable comparison against non-zeta operators.

## Handoff and limitation

This is a research agenda, not an execution authorization or a Lean proof. The underlying registry in `research/next-epoch-proposals.json` is the authoritative badge/status record. Independent QA should check the registry against this document and run only the listed cheap tests after specialists are provisioned.

## Evidence / Artifacts

- `research/next-epoch-conjectures.md` — human-readable ranked agenda and guardrails.
- `research/next-epoch-proposals.json` — machine-readable proposal registry; each proposal has an explicit `CONJECTURE` badge, conditional theorem badges, dependencies, cheap test, and negative examples.
- `codex-insights/2026-11-02-min-24-next-epoch.md` — insight-outbox record.

## Checks

- Registry/document alignment: PASS by inspection; P1–P3, ranks, badges, tests, dependencies, and counterexamples agree.
- Zeta guardrail: PASS by inspection; the document explicitly makes `Re(s)=1/2` hypothesis-generator-only and states the missing analytic bridge.
- Execution authorization: NOT RUN; status remains `CANDIDATE / NOT EXECUTION-AUTHORIZED`.
- Independent Lean/math QA: PENDING; specialists are not provisioned.
