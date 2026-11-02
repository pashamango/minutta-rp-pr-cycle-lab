# AMDE-OUT: applications and monetization schemes

**Ticket:** MIN-92  
**Parent direction:** PRD-31  
**Status:** Builder draft for independent review  
**Date:** 2026-11-02

## Outcome

AMDE should be commercialised first as a narrow **trust and verification
product**, not as a general-purpose mathematical platform. The recommended
sequence is:

1. paid proof-verification reports for teams that already have a theorem or
   numerical claim;
2. certified numerical packages with reproducible intervals and machine-
   readable evidence;
3. licensed demo/engine access after repeatable demand and support boundaries
   are understood.

The first sellable unit is a bounded verification job with a clear input
contract, a fixed evidence bundle, and a human-readable report. This keeps the
initial sales motion close to the existing AMDE-LEAN and AMDE-NUM artifacts and
avoids promising an unproven universal solver.

## Scope and evidence boundary

This is a strategy estimate, not customer validation, a legal opinion, or a
claim that AMDE has proved a mathematical conjecture. The document relies on
the project direction described in PRD-31 and the existence of adjacent
formalisation/numerics work in the repository. Prices, conversion rates, and
market size below are planning assumptions that must be replaced by interview
and pilot data.

## Product applications

### 1. Proof-verification service (recommended beachhead)

**Buyer:** research groups, quantitative R&D teams, and software vendors that
need an independent check before publication, release, or an internal design
decision.

**Input:** a bounded theorem/proof obligation or a precisely stated numerical
claim, plus source files and an allowed dependency list.

**Output:** verification verdict (`PASS`, `FAIL`, or `INCONCLUSIVE`), checked
commit and manifest, proof/numerical logs, reproducibility command, and a
short report explaining assumptions and uncovered cases.

**Candidate pricing (USD):** $2,000–$7,500 for a fixed-scope verification;
$8,000–$20,000 for a multi-lemma or publication-grade package; $1,000–$3,000
for a follow-up rerun when inputs are unchanged. Quote only after a
preflight confirms that the claim is in scope.

**Why it can win:** the customer pays for an auditable decision and reduced
review risk, rather than for raw compute. The service also creates labelled
failure cases that improve the product.

### 2. Certified numerical package (repeatable product)

**Buyer:** developers and research engineers who need reliable bounds for
special functions, dynamical systems, or parameter sweeps in a larger pipeline.

**Deliverable:** versioned package/API, interval or ball-arithmetic results,
precision and domain declarations, reference vectors, deterministic replay,
and a signed evidence manifest. A package must fail closed when a bound cannot
be certified.

**Candidate pricing (USD):** free read-only examples; $500–$2,000 per
developer seat/year for evaluation and local use; $5,000–$25,000/year for a
team licence with support and release pinning; separately quoted integration
work.

**Commercial boundary:** “certified” means certified relative to the stated
algorithm, dependencies, precision, and domain. It does not mean that every
downstream use is safe or that the underlying conjecture is true.

### 3. Demo and engine licensing

**Buyer:** universities, advanced R&D groups, and software companies that want
to embed the engine or run controlled demonstrations without commissioning a
new proof each time.

**Tiers:**

| Tier | Use | Indicative price | Entitlement |
|---|---|---:|---|
| Demo | browser/notebook exploration | $0 | capped examples, no production SLA |
| Research | local experiments | $1,500–$5,000/year | named users, pinned version, community support |
| Team | internal pipeline | $10,000–$40,000/year | seats/service account, release support, audit export |
| OEM/embedded | customer product | $50,000–$150,000/year + usage or revenue share | redistribution and integration rights |

The engine licence should follow, rather than precede, evidence that the API,
upgrade path, and support burden are predictable.

## Monetization schemes and unit economics

### Base-case planning model

The following is a deliberately modest first-year scenario, not a forecast:

| Stream | Volume | Average price | Gross revenue |
|---|---:|---:|---:|
| Fixed verification | 12 jobs | $4,000 | $48,000 |
| Certified packages | 8 licences | $3,000 | $24,000 |
| Team/OEM pilots | 2 pilots | $15,000 | $30,000 |
| **Total** |  |  | **$102,000** |

Planning assumptions: one builder can complete two bounded verifications per
month after preflight; 70% of quoted jobs are accepted; direct delivery cost
(compute, review time, and customer support) is 35–50% of service revenue;
licence gross margin is higher only after release automation exists. Under
these assumptions, the first-year gross contribution is approximately
$55,000–$67,000 before product development, sales, tax, and legal costs.

### Pricing mechanics

- Use fixed price for a fixed claim and a fixed evidence contract.
- Charge a 30–50% discovery/preflight fee for ambiguous or oversized inputs;
  credit it against a subsequent statement of work.
- Use annual subscription for versioned packages and support, not for an
  unlimited “proof guarantee.”
- Meter expensive compute or high-volume API calls separately with a hard cap.
- Offer a paid rerun only when the input, dependency lock, and target commit
  are recorded; otherwise treat it as new scope.

### Funnel targets for a pilot

For the first 90 days, success should be measured by evidence, not vanity
traffic:

| Metric | Target | Decision rule |
|---|---:|---|
| Qualified discovery calls | 12 | fewer than 6 means reposition or narrow ICP |
| Paid preflights | 4 | fewer than 2 means the pain is not urgent enough |
| Completed paid verifications | 3 | fewer than 2 means delivery or scope is broken |
| Repeat/expansion requests | 1+ | zero means do not accelerate licensing |
| Evidence bundles replayed independently | 100% | any failure blocks a “certified” claim |

These are experiment gates, not guaranteed benchmarks.

## Recommended go-to-market sequence

**Phase 0 — package the trust boundary (2–4 weeks).** Define supported claim
classes, input manifest, dependency lock, evidence schema, report template,
and explicit `INCONCLUSIVE` behaviour. Produce one public example and one
redacted internal example.

**Phase 1 — paid design partners (4–8 weeks).** Approach 10–15 prospects in
research software, formal methods, and quantitative R&D. Sell fixed-scope
preflights and verification jobs. Record cycle time, failure modes, and what
customers would have paid for without changing the result.

**Phase 2 — package the repeated path (6–12 weeks).** Turn the most common
verified computation into a pinned numerical package with replay tests and a
small CLI/API. Publish a compatibility policy and support limits.

**Phase 3 — selective licensing.** Offer team or OEM licensing only when three
independent runs reproduce the same evidence format, upgrades are rollbackable,
and support time per customer is known.

## Risks, controls, and non-goals

| Risk | Control | Stop condition |
|---|---|---|
| Overclaiming mathematical certainty | state domain/precision/dependencies; allow `INCONCLUSIVE` | any marketing claim broader than the evidence |
| Services become bespoke consulting | strict preflight and change-order boundary | median job exceeds 2× estimate for two cycles |
| Reproducibility breaks after upgrade | pinned manifests, replay CI, signed artifacts | any certified bundle fails replay |
| Support cost erodes licence margin | seat/usage caps and support SLA tiers | support exceeds 30% of recurring revenue |
| IP or export/licensing conflict | counsel review and dependency inventory | unresolved third-party restriction |
| Weak willingness to pay | paid preflight before free custom work | fewer than two paid pilots in 90 days |

Non-goals for the first release: universal theorem proving, an unlimited cloud
compute promise, an unsupervised safety-critical certificate, or a claim that
AMDE replaces peer review.

## Acceptance checklist

- [x] Practical applications cover proof verification, certified numerics,
  and demo/engine licensing.
- [x] Monetization schemes include prices, entitlement boundaries, and a
  base-case estimate.
- [x] Assumptions are labelled and separated from verified evidence.
- [x] Roadmap, funnel gates, risks, and stop conditions are included.
- [ ] Customer interviews and willingness-to-pay data: **PENDING**.
- [ ] Independent reviewer receipt: **PENDING**.

## Evidence / Artifacts

- `research/MIN-92-AMDE-OUT-applications-monetization.md` — this strategy
  document.
- Commit and remote coordinates are supplied in the handoff receipt after
  commit/push.

## Checks

- Markdown structure and required sections checked with the command below.
- No credentials, private keys, customer data, or unsupported proof claims
  added.

## Limitations

No external customer interviews, competitor pricing study, legal review, or
independent mathematical validation was performed in this task. The numerical
estimates are hypotheses for a bounded pilot and must not be presented as
revenue guidance.
