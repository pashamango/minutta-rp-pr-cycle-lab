# POW-0001 — Formal Scarcity and Falsification Gate

## Decision

**Final verdict: HYPOTHESIS_FALSIFIED**

The pure predicate

\[
3(A+x)+1\equiv0\pmod {2^k}
\]

is an exactly invertible coordinate equation, not a probabilistic work puzzle. For every
admissible `A` and every `k >= 1`, one ordinary modular subtraction produces the sole valid
residue after a network-wide constant has been precomputed. Increasing `k` increases integer
width, but it does not introduce an expected-trials work factor, scarce identity, sequential
delay, or resource-backed chain weight. A process can therefore extend every fork and every
Sybil template at negligible marginal cost. `NOTHING_AT_STAKE = PROVED` for the predicate
under test.

This report evaluates only the M0 construction described in Issues #43 and #44. It does not
specify or implement a Bitcoin fork, does not interact with mainnet or Testnet4, and does not
endorse a redesign.

## Model and definitions

Let `R_k = Z / 2^k Z`, with canonically encoded representatives in `[0, 2^k)`. An admissible
`A` is any element of `R_k`. A candidate is a pair `(A, x)` accepted exactly when the displayed
congruence holds. This is the strongest interpretation for the proposal: all block/header
conditioning is assumed to have already produced `A`, and all of `A` is bound to the candidate.

For a concrete implementation on machine `H`, define:

* `C_alg(B; H)` as elapsed CPU time or deterministic arithmetic operations needed to derive and
  validate `x` for block template `B`;
* `C_scarce(B)` as consumption of the protocol's claimed externally scarce resource which an
  adversary cannot obtain merely by adding identities or parallel templates.

Bitcoin-like work requires the second quantity to be tunable, objectively inferable from a
valid proof, costly to replay, and approximately additive across competing histories. Ordinary
finite computation makes `C_alg > 0`; that fact alone does not establish `C_scarce > 0`.

## Obligation A — trivial inversion theorem: PROVED

**Theorem 1 (existence and uniqueness).** For each `A in R_k` and integer `k >= 1`, exactly one
`x in R_k` satisfies the predicate, namely

\[
x\equiv-3^{-1}-A\pmod {2^k}.
\]

**Proof.** Since `gcd(3, 2^k) = 1`, multiplication by 3 is a bijection on `R_k` and has a unique
inverse. Rearranging gives `3(A+x) = -1`; multiplying by `3^-1` gives the stated residue, proving
existence. If `x` and `x'` both work, then `3(x-x') = 0` in `R_k`; multiplying by `3^-1` gives
`x=x'`, proving uniqueness. QED.

**Exact Newton/Hensel role.** Start with `y_0 = 1`, an inverse of 3 modulo 2. If `y` is correct
modulo `2^m`, set

\[
y'=y(2-3y).
\]

Then `1-3y' = (1-3y)^2`, so its 2-adic valuation at least doubles and `y'` is correct modulo
`2^(2m)` (or any requested lower precision). This is Newton inversion of the unit 3 in the
2-adic ring. Algebraically, on the unit domain it is also Newton's method for
`f(y)=y^-1-3`: because `f'(y)=-y^-2`, the Newton update is
`y-f(y)/f'(y)=2y-3y^2`. The inverse and division here are valid only for 2-adic units; the
finite implementation performs the equivalent precision-lifting polynomial update in
`Z/2^n Z`. There is no mathematical distinction between these two derivations of the same
update, but the ring and current precision must be stated.

Starting at one correct bit takes `ceil(log2(k))` updates: 5, 6, 7, 8, and 9 at 32, 64, 128,
256, and 512 bits. That is iteration count, not bit complexity. At precision `n`, an update has
one general `n`-bit multiplication plus constant multiplication, subtraction, and masking.
With multiplication cost `M(n)`, progressive precision costs `O(sum M(2^i)))`, hence
`O(M(k))` for usual superlinear multiplication bounds and `O(k^2)` under schoolbook
multiplication. Once `3^-1 mod 2^k` is precomputed for fixed network `k`, a block solve is only
one `k`-bit subtraction and reduction (masking for a power-of-two modulus): `O(k)` bit work.
No block-dependent expensive computation remains in this predicate.

### Measured practical cost

Command:

```text
python3 research/pow_0001_attacks.py --identities 100000 --forks 1000 --levels 100 --rewrite-blocks 100000
```

Environment: Python 3.12.0, `macOS-26.6.2-arm64-arm-64bit`. Each width measurement includes
deterministic SHA-256 template derivation, analytical solve, and validation for 50,000 distinct
templates, so it overstates the predicate-only solve cost. Timings are bounded observations,
not portable performance guarantees.

| k (bits) | inverse precompute | ns/candidate | candidates/s |
|---:|---:|---:|---:|
| 32 | 11,375 ns | 1,549 | 645,528 |
| 64 | 4,458 ns | 1,524 | 656,335 |
| 128 | 7,750 ns | 1,541 | 648,880 |
| 256 | 4,584 ns | 2,100 | 476,191 |
| 512 | 6,083 ns | 3,249 | 307,791 |

Noise explains the non-monotone microsecond timings. The relevant result is that widening `k`
changes fixed-width arithmetic cost modestly; it never changes success probability because
every template has exactly one directly computed solution.

## Obligation B — work-factor theorem: PROVED (negative scarcity result)

**Theorem 2.** For fixed practical `k`, marginal valid-candidate production is bounded by
ordinary deterministic arithmetic and has no Nakamoto-style work factor.

**Proof.** Precompute `q_k = 3^-1 mod 2^k`. For every block-dependent `A(B)`, the algorithm
`x(B) = (-q_k - A(B)) mod 2^k` succeeds on its first and only attempt. Its post-precomputation
cost is `O(k)` bit operations, success probability is 1, and its output distribution does not
require sampling. By contrast, for an ideal `d`-bit threshold event, independent trials have
success probability `2^-d` and expected count `2^d`. Changing `k` changes operand size and the
deterministic answer; it does not create the Bernoulli trials or an external scarcity source.
Thus `C_alg(B)` is small and `C_scarce(B)=0` for the pure predicate. QED.

This does not claim computation is thermodynamically free. It says the protocol exposes no
difficulty parameter that forces economically meaningful, objectively measurable expenditure.

## Obligation C — fork-cost additivity: FAILS the scarcity property

Let parent `P` have two distinct child templates `B_0` and `B_1` (for example, distinct
coinbase commitments), mapped to `A_0` and `A_1`. The theorem gives
`x_i = -q_k-A_i mod 2^k`; both children are valid immediately. Recursively include each child
identifier in its successor template and apply the same formula to construct two length-`N`
histories.

For deterministic arithmetic, `C_alg(chain_i)=N*c_k+O(1)` and sequentially constructing both
costs `2N*c_k+O(1)`. That trivial CPU additivity is not the required scarcity property because
`c_k` is a few microseconds including template hashing, is not difficulty-tunable, and may be
parallelized across cores/devices. For scarce work,
`C_scarce(chain_0)=C_scarce(chain_1)=C_scarce(both)=0`; hence no positive additive chain resource
exists. The explicit tolerance used here is qualitative but decisive: a candidate mechanism
must exhibit a positive, protocol-tunable resource whose two-history cost is within a stated
nonzero factor of twice one-history cost. This predicate has zero in numerator and denominator,
so it cannot satisfy such a ratio.

Measured Attack 2 generated 1,000 branches for 100 levels (100,000 valid candidates) in
223,590,583 ns: 447,246 candidates/s and 2,236 ns/candidate. CPU time scales linearly with `M*N`
because the script visits each output, but branch admission does not consume a scarce resource.
More hardware reduces wall time, and more identities add no protocol cost.

`NOTHING_AT_STAKE = PROVED`.

## Obligation D — objective cumulative weight: NO NATURAL FUNCTION EXISTS

Suppose `W(chain)=sum w(B_i)` is derived only from valid pure-predicate blocks.

* If `w=1`, `W` is block count and an offline attacker manufactures it at microsecond-scale
  arithmetic cost.
* If `w` is a function of `k`, every block at that declared `k` remains first-attempt solvable;
  a label is not expenditure.
* If `w` uses timestamps, timestamps attest neither elapsed computation nor exclusive resource.
* If `w` uses measured local CPU time, nodes cannot independently verify the miner's measurement.

Therefore no such natural scalar simultaneously represents consumed scarcity, prevents cheap
offline manufacture, makes rebuilding `N` blocks cost `N` scarce units, and charges parallel
forks proportionally. A scalar can be stipulated, but it would not be resource-backed.

Bitcoin is materially different: the consensus header commits to the previous header and Merkle
root and is accepted when its double-SHA-256 hash is below the encoded target; Bitcoin Core
accumulates per-block expected work as `nChainWork`. See the [Bitcoin block-header reference](https://developer.bitcoin.org/reference/block_chain.html),
[Bitcoin Core `pow.h`](https://github.com/bitcoin/bitcoin/blob/master/src/pow.h), and
[Bitcoin Core `chain.h`](https://github.com/bitcoin/bitcoin/blob/master/src/chain.h).

## Obligation E — reversible/Feistel conditioner: FAILS to add work

No canonical conditioner, serialization, round functions, or field split is specified in the
source, so claims about one concrete implementation would be unverifiable. The following exact
counterexamples establish what a conditioner must prevent and why two reversible rounds alone
provide no such guarantee.

1. **ExtraNonce cancellation.** If `A=(PrevHash+ExtraNonce) mod 2^k`, choose
   `ExtraNonce=(p-PrevHash) mod 2^k` to force any desired phase `p`. For XOR conditioning,
   `A=PrevHash xor ExtraNonce`, choose `ExtraNonce=PrevHash xor p`. Thus a mutable `k`-bit field
   exactly cancels the fixed field. A cryptographic hash may remove algebraic cancellation, but
   then it merely turns the mutable field into a grinding input unless success is tied to a
   scarce target event.
2. **Choose phase first, fit header second.** A Feistel network is a permutation. If mutable
   serialized fields span its full input domain, choose desired output `Y` (or phase `n`), compute
   the unique input `P^-1(Y)`, and serialize that input into the mutable fields. If fixed fields
   constrain part of the preimage, exact fitting is not guaranteed; the remaining alternative is
   grinding mutable encodings. Reversibility therefore cannot itself prove binding or scarcity.
3. **Precomputation/template reuse.** `q_k` is reusable globally. Under either cancellation
   construction above, a miner also preselects `p` and reuses `x=-q_k-p`; only the canceling
   ExtraNonce changes with `PrevHash`. Without cancellation, the same constant-time solve is
   reused for every newly conditioned `A`.
4. **Relocated grinding.** In Bitcoin's actual 80-byte header the nonce is 32 bits; changing the
   coinbase changes the Merkle root, creating additional header search space. The official
   [header reference](https://developer.bitcoin.org/reference/block_chain.html) documents this.
   Replacing `Nonce` trials with `ExtraNonce`, transaction-order, Merkle-root, or timestamp trials
   changes the coordinate of search, not its security property. With the analytical equation no
   grinding is needed at all unless a separate target is imposed.
5. **Two-round property.** A balanced Feistel round
   `(L,R)->(R,L xor F(R))` is invertible regardless of `F`. That guarantees a permutation only.
   Concrete counterexample: choose both round functions `F=0`; two rounds are the identity, so
   they provide no diffusion, pseudorandomness, commitment, collision resistance, or grinding
   resistance. Standardized Feistel-based format-preserving encryption instead specifies an
   approved block cipher and many rounds; see [NIST SP 800-38G](https://csrc.nist.gov/pubs/sp/800/38/g/upd1/final).
6. **Canonical binding.** If serialization omits any consensus field, two blocks differing only
   in that field have identical conditioner input and proof. Concrete examples are omitted
   transaction ordering, timestamp, difficulty, or full coinbase bytes. If multiple encodings
   decode to one semantic field (variable-length integers with redundant encodings, ignored
   padding, or noncanonical transaction order), the same state has malleable proofs. No supplied
   specification rules these out, so canonical non-malleable binding is unproved.

Even an ideal permutation or hash binding every canonical field would only commit the candidate;
it would not make the analytically computed `x` costly.

## Obligation F — VDF escape hatch: REDESIGN only, not a rescue

A VDF adds a prescribed number of sequential evaluation steps under a security assumption while
allowing cheaper verification. That is sequential delay; it indirectly consumes hardware time
and energy, and specialized hardware affects the real delay bound. The VDF literature defines
this asymmetry rather than probabilistic leader election; see Boneh, Bonneau, Bünz, and Fisch,
[Verifiable Delay Functions](https://eprint.iacr.org/2018/601.pdf), and Wesolowski,
[Efficient Verifiable Delay Functions](https://eprint.iacr.org/2018/623.pdf).

Answers to the required checks:

1. The scarce quantity is sequential steps per seed, conditional on the VDF's assumptions and a
   hardware model—not identity, stake, or automatically a fixed amount of energy.
2. A deterministic VDF alone is not leader election. One input produces one deterministic output.
3. If all miners use the same seed, all compute the same result and may finish the same slot;
   the VDF supplies no unique winner. Concrete collision: identities Alice and Bob evaluate
   `VDF(PrevHash,T)` and both emit the identical proof/output at step `T`.
4. If seed includes identity, a Sybil creates seeds `H(PrevHash||id_i)` and evaluates them on
   separate devices. Prevention requires an external admission/eligibility or scarce-resource
   rule.
5. On one sequential evaluator, two branch seeds require about `2T` steps. This is genuine
   per-evaluation cost if shortcuts are excluded.
6. Two devices evaluate two branches concurrently in about `T` wall time while consuming two VDF
   evaluations. VDF sequentiality is within one instance, not across independent branches.
7. Nodes might sum a fixed certified delay or parameterized sequential-work score, but only if
   seeds, parameters, uniqueness, difficulty adjustment, and eligibility are consensus-bound.
   Counting duplicate same-seed proofs cannot represent extra work.
8. If this layer supplies all scarcity, the design is proof-of-sequential-time/VDF consensus,
   not evidence that the original 2-adic predicate was PoW.

A credible redesign still needs a leader/eligibility mechanism, unbiasable branch-bound seeds,
calibrated hardware assumptions, additive resource accounting, and a formal fork-choice/security
model. None is provided here; accordingly the original hypothesis remains falsified.

## Obligation G — Collatz/orbit escape hatch: FAILS as stated

The precise accelerated odd map is

\[
U(n)=(3n+1)/2^{v_2(3n+1)},\qquad n\in\{1,3,5,\ldots\}.
\]

An orbit predicate must state a finite maximum step count `L`, an admissible domain, and an
acceptance condition evaluable within `L`. Requiring validators to traverse until reaching 1 or
another globally terminating condition makes consensus liveness depend on the unproved Collatz
conjecture. Lagarias's survey records the problem and its unresolved status; see
[The 3x+1 Problem: An Overview](https://arxiv.org/abs/2111.02635).

An attacker selects mutable header/coinbase data until its decoded starting state has a long
observed path; absent an explicit `L`, the submitted candidate amplifies verifier work without a
protocol bound. This is a verifier-DoS/liveness failure. With a fixed `L`, verification is
`O(L)` big-integer steps and bounded, but the orbit is still deterministic and parallelizable.
It adds computation, not an intrinsic random success target or Sybil-resistant scarcity.
ExtraNonce, Merkle-root, transaction-order, and timestamp freedom can grind starting residues for
favorable orbit classes exactly as any mutable seed can be ground.

A succinct proof could bound verifier work, but its statement must itself cap the represented
trace and bind every input. Proof generation supplies scarcity only if a separate calibrated
proof-of-computation construction forces hard work with no shortcut and additive fork cost; in
that event the proof system, not the Collatz conjecture, supplies the resource. No unbounded
orbit traversal is consensus-safe.

## Deterministic attacks and results

The self-contained script `research/pow_0001_attacks.py` uses Python's standard library. It
derives deterministic `A` values from labeled SHA-256 counters, precomputes `q_k` once, solves
each candidate, verifies the congruence, and emits JSON. SHA-256 here creates reproducible
distinct templates; it is not searched against a target.

| Attack | Construction | Observation | Result |
|---|---|---:|---|
| Sybil block factory | 100,000 labeled identities, one analytic solve each | 215,115,750 ns; 464,866/s; 2,151 ns each | PASS |
| Parallel fork factory | 1,000 parent-bound forks x 100 levels | 223,590,583 ns; 447,246/s; 2,236 ns each | PASS |
| Offline history rewrite | checkpoint plus 100,000 parent-bound successors | 216,438,959 ns; 462,024/s; 2,164 ns each | PASS |

Every generated candidate passed the predicate. For Attack 3, no rule in the pure predicate
prevents immediate overtaking: a changed previous identifier merely changes `A`, after which the
unique `x` is solved again. Network delivery and non-PoW validity rules may constrain which
blocks propagate, but they do not impose historical hash expenditure or resource-backed weight.

Tests:

```text
python3 tests/test_pow_0001_attacks.py -v
```

The tests verify Newton inverses at all five widths, exhaustively prove computed uniqueness for
all `A` at widths 1 through 8, and solve 10,000 deterministic 256-bit templates.

## Comparison baseline

| Property | Bitcoin SHA256d threshold PoW | Pure 2-adic predicate |
|---|---|---|
| Production | Expected independent target trials | One deterministic subtraction |
| Marginal branch cost | New expected trials | Microsecond-scale arithmetic |
| Parallel branches | Divide finite hash resource or buy more | Freely add templates/identities; ordinary CPU only |
| Precomputation resistance | Previous hash/header commitment invalidates prior trials | `3^-1` global constant; every new `A` solved directly |
| Objective cumulative weight | Sum of target-derived expected work | None natural |
| Verification | Hash header and compare target | One multiply/add/mask |
| Difficulty tunability | Target changes success probability | `k` changes width, not success probability |
| Offline rewrite | Reproduce cumulative expected work | Generate analytical chain locally |
| Sybil sensitivity | Identities do not create hash work | Identities create unlimited valid templates |

This is a conceptual resource comparison, not a claim that every hash consumes identical energy
or a mainnet benchmark.

## Classification

| Claim/component | Classification | Finding |
|---|---|---|
| 3 is a unit modulo `2^k` | KNOWN | Elementary modular arithmetic |
| Newton/Hensel inverse lift | KNOWN | Precision doubles; inverse is precomputable |
| 2-adic solve as coordinate transform | REFORMULATION | Correct and useful as arithmetic, not work |
| Pure predicate supplies PoW scarcity | FALSIFIED | Every template is solved on first attempt |
| Pure predicate supplies objective chain weight | FALSIFIED | No resource-backed scalar exists |
| Two Feistel rounds supply security | FALSIFIED as a general claim | Invertibility only; zero round functions give identity |
| Fully canonical conditioner binds all fields | HYPOTHESIS | No bit-level specification supplied |
| Bounded VDF can add sequential delay | HYPOTHESIS / REDESIGN | Requires a concrete construction and consensus model |
| Collatz termination is safe for validation | FALSIFIED as a premise | Global termination remains unproved; traversal must be bounded |
| Bounded orbit work supplies scarcity | HYPOTHESIS, unsupported | Deterministic parallel computation is not sufficient |

## Acceptance matrix

| Check | Status |
|---|---|
| Trivial inversion theorem | PASS — PROVED |
| Practical cost model | PASS |
| Fork-cost experiment | PASS |
| Objective cumulative-weight attempt | PASS — no natural resource-backed weight |
| Feistel conditioner analysis | PASS |
| VDF escape-hatch analysis | PASS |
| Collatz/orbit analysis | PASS |
| Sybil block factory | PASS |
| Parallel fork factory | PASS |
| Offline history rewrite | PASS |
| Final verdict is allowlisted | PASS — HYPOTHESIS_FALSIFIED |
| Mainnet interaction | NONE |
| Bitcoin Core fork created | NO |
| Auto-merge | NO |

## Strongest remaining research question

Can a separately specified, branch-bound, Sybil-resistant sequential-work construction provide
objective additive chain weight under an explicit hardware/adversary model while retaining cheap
bounded verification and decentralized leader selection? That is a VDF-consensus redesign
question. It cannot rehabilitate the pure analytical predicate as Proof of Work.

M1 and all Bitcoin-derived consensus implementation remain blocked pending project-owner review
of this M0 verdict.
