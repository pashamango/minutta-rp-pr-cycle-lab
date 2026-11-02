# Formal Assurance Dossier — buyer-facing one-page pitch

**Status:** Commercial hypothesis / candidate offer. Not evidence of customer demand, revenue, certification, or a production safety guarantee.

## The offer

Mindrock turns a narrowly specified system rule into a reviewable, machine-checked assurance package: the model, Lean source, pinned toolchain/dependencies, theorem and axiom report, counterexamples where applicable, replay command, and a short plain-language risk memo. The buyer is paying for a bounded evidence artifact that an engineer, auditor, or instructor can rerun—not for a claim that mathematics makes an autonomous system safe in every environment.

## Buyer problem and first use case

Teams building autonomous workflows often have policies such as “delegation preserves authorization” or “this state transition cannot enter a forbidden class,” but their evidence is spread across prose, tests, and ad-hoc reviews. The first use case is a **pre-release authorization/invariant audit** for one small workflow: formalize the state and transition rules, prove the requested invariant under declared assumptions, generate a countermodel when the claim is too strong, and hand over a replayable evidence bundle for design review.

**Substitutes:** code review and unit/property tests; model checkers and SMT solvers; internal formal-methods teams; external safety/security consultants; and simply accepting an undocumented policy. The differentiator is the combined deliverable—conditional proof plus assumptions, countermodel, provenance, and independent replay—in a scope small enough for a design gate.

## Three buyer segments

1. **AI platform / agent-runtime engineering teams.** A capability or delegation rule is business-critical but changes frequently. Entry offer: one bounded authorization invariant and a CI/review handoff. Adoption friction: formalization time, changing schemas, and fear that a proof is mistaken for runtime safety.
2. **Safety, security, and compliance consultancies.** They need auditable technical evidence without hiring a Lean specialist for every engagement. Entry offer: co-produced evidence pack and reviewer training. Friction: independence, client confidentiality, and acceptance of Lean evidence by the client’s auditor.
3. **Universities and professional training teams.** They need a reproducible bridge from logic to dependable software practice. Entry offer: a local lab with seeded examples, countermodels, and grading rubric. Friction: curriculum fit, instructor time, licensing/attribution, and no claim that toy models transfer automatically to production.

## Reproducible demo (zero paid external compute)

Use a small local Lean project and a deliberately bounded transition system. A participant should be able to: (1) clone the exact repository and commit supplied by the seller, (2) install/use the pinned Lean toolchain and dependency lockfile, (3) run `lake build` plus the project’s theorem/axiom audit, (4) inspect one passing invariant and one countermodel showing why a stronger claim fails, and (5) receive a SHA-256 manifest of the evidence bundle. Success is a fresh local replay with exit code 0 and an explicit assumptions/axioms report. The demo must not require a paid API, cloud GPU, or private credential.

## Adoption and pricing hypotheses

Likely friction is not theorem proving alone: translating an operational policy into a stable formal model, obtaining an independent reviewer, maintaining proofs as code changes, and preventing overclaiming. Validate a service-first wedge before building a platform.

Pricing is **hypothetical**, to be tested rather than represented as a quote or benchmark: a fixed-scope discovery/audit pilot at **$2k–$8k**; a deeper evidence package at **$8k–$25k**; and optional maintenance/review retainer at **$1k–$5k/month**. Actual price should follow buyer-perceived reduction in review risk and required specialist time, not theorem count.

## Demand boundary and validation test

**Observed demand:** none is claimed here. Existing Lean files and internal release evidence show a technical artifact, not a buyer, paid engagement, inbound request, conversion rate, or willingness to pay. **Market hypothesis:** teams with high-cost authorization or audit failures will pay for a bounded, independently replayable formal evidence package.

Run ten no-cost interviews or asynchronous reviews with named target users, using the same two-page demo and a request for a concrete recent review artifact. Record independently: problem occurrence, current substitute, budget owner, time-to-review, objection, request for a paid pilot, and whether the buyer supplies a real non-sensitive rule. A strong signal is at least three requests for a scoped pilot and one signed/paid engagement; likes, profile views, and hypothetical survey interest do not count. Use local Lean and existing hardware only; do not infer demand from internal collaboration.

## Claims, conflicts, and limitations review

- Say **“conditional machine-checked theorem”**, not “proof that an ontology is real,” “AI alignment solved,” “safe autonomous agent,” or “certified compliance.”
- Publish each theorem’s hypotheses, countermodels, axioms, toolchain, dependency revision, source/license attribution, and replay status. A build report is not independent verification until a fresh reviewer replays it.
- Disclose that the seller is also the author/operator of the research artifacts and may benefit from adoption; separate technical review from sales approval and seek an independent reviewer.
- Do not claim customer traction, contract value, certification, or transfer from toy models to production without dated external evidence.

**Evidence boundary used for this draft:** the staged ontology release reports 7 modules and 53 theorem declarations, a clean build/axiom audit in its own evidence ledger, and explicitly keeps publication and independent review gated. Those are technical staging facts, not commercial validation.
