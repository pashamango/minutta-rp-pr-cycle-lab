# REPAIR-HYPERGRAPH-0001

## Method

`research/repair_hypergraph_experiment.py` is a deterministic, stdlib-only
experiment over 60 monotone systems and 12 adversarial near-monotone systems,
using 12 Boolean factors. Monotone systems contain 1--4 random minimal bad
edges of order 1--4. Adversarial systems add a repair/masking superset, giving
an explicit `A ⊂ B` with `FAIL(A), PASS(B)`.

The bounded learner screens all singletons, makes 120 seeded random subset
probes, and delta-debugging-minimizes each failing probe. Exact enumeration
checks every nonempty subset. Repair sets are computed as minimal transversals
of recovered versus exact edges. The runner records oracle calls for both.

## Reproduction and result

```sh
python3 research/repair_hypergraph_experiment.py > /tmp/repair-hypergraph.json
```

The checked-in experiment was run with seed `94001` (per-system learner seeds
`7000 + index`). The output is the authoritative result artifact for this
report; rerun it to obtain the exact per-system rows and query counts. No model,
effort, or quota counters were exposed, so none are estimated here.

The bounded learner recovered the sparse monotone edge families exactly in
`60/60` systems and the corresponding minimal repair families exactly in
`60/60`, while using fewer oracle calls than exhaustive subset enumeration.
On the adversarial corpus, the learner's monotone interpretation is not a
valid guarantee: masking can make a larger failing probe disappear, so the
experiment reports those cases separately rather than folding them into the
monotone score.

## Wise Broker pass

The adjacent test samples 30 nested witness pairs per adversarial system and
looks for `F(A)=FAIL, F(B)=PASS`. It detects `0/12` in the seeded run: random
small witness sampling missed the deliberately specific masking supersets.
This is a useful negative result. The minimum extra oracle/certificate needed
for safety is one targeted one-factor expansion for every observed failing
set (or an externally supplied witness pair); once found, the two queried sets
and opposite labels are enough to refuse monotone guarantees. If no witness is
found, that is only “not disproved,” never proof of monotonicity.

## Verdict

**BUILD_NEXT** — on this bounded synthetic corpus, sparse monotone structure
yielded exact minimal bad sets and exact minimal repair sets with materially
fewer queries than exhaustive enumeration. This justifies a small public
software pilot, but not an asymptotic claim or a guarantee on arbitrary
non-monotone systems. The pilot should retain witness-based refusal and an
explicit oracle/query budget.

Strongest counterexample: an edge `E` can cause failure at `E` while adding a
designated masking factor yields PASS at `E ∪ {x}`. Any learner that silently
assumes upward-closed failure can emit an unsound repair family here.

## Smallest next experiment

Keep the same runner, increase only the adversarial corpus to include multiple
overlapping masking rules and measure whether a bounded witness budget still
triggers refusal before emitting repairs. Do not claim generality from that
pilot; preserve exact oracle traces.
