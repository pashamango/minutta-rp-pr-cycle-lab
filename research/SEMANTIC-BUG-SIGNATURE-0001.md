# SEMANTIC-BUG-SIGNATURE-0001

## Method

This is a public-data-only experiment. `corpus.json` is a fixed snapshot of 34 public GitHub issues, collected by seven deterministic GitHub Search API queries (five intended examples per family; one query returned four). The URLs, repository names, titles, bodies, and labels are retained so the run is auditable. No private repository, credential, paid service, or model call was used.

The v1 behavioral signature schema was fixed before collection and scoring:

`S = {violated_invariant, failure_class, operation_pattern, state_transition, test_symptom, repair_family_cue}`

The implementation is deliberately conservative: lowercase vocabulary is retained only when it belongs to the fixed transferable cue set `{error, exception, fail, failed, failure, missing, duplicate, race, stale, schema, null, permission, cache, path, config, ordering, state, retry, serialize, authorization, lookup}`. High-specificity residual candidates are replaced with `<RESIDUAL>` before cue extraction: slash paths, URLs, backtick literals, capitalized identifiers, and numeric literals. This is an operational proxy, not a formal privacy guarantee.

The baseline is cosine similarity over token-count vectors, evaluated leave-one-out against all other incidents. A hit means the nearest incident has the same repair-family label (top-1), or at least one of the nearest three does (top-3). `S+R` appends the removed material as a control.

## Corpus and labels

Seven repair families are represented: idempotency/duplicate execution, unchecked-null lookup, authorization guard omission, stale cache/state mismatch, serialization/schema mismatch, race/concurrency ordering, and path/config mismatch. Labels are experimental family annotations assigned from the fixed search intent; they should be treated as noisy, not as canonical GitHub metadata. An adversarial surface-vocabulary case is the nearest-neighbor confusion between a null-lookup incident and an ordering/concurrency incident: both contain generic “error/failure/state” language but require different repair families.

## Observed results

| representation | top-1 | top-3 |
|---|---:|---:|
| RAW | 64.7% | 88.2% |
| S | 52.9% | 70.6% |
| S+R | 47.1% | 82.4% |

The control behaves unexpectedly at top-1 because this cheap concatenation changes token weighting; it is still useful as an upper-bound-style control only at top-3, not as a claim of optimal RAW retrieval. The hypothesis is not supported by this baseline: S materially underperforms RAW at both ranks and provides no demonstrated generalization advantage in this run.

## Leakage/redaction proxy

Across the stored corpus, S is made only from the fixed cue vocabulary after replacement of high-specificity spans. Measured proxy totals are 13,977 original alphanumeric tokens, 235 signature tokens (98.3% reduction), and 2,186 replaced high-specificity spans. Because the signature intentionally keeps common behavioral words and removes paths, URLs, identifiers, literals, and numbers, it suppresses high-specificity material but does not establish differential privacy or resistance to linkage attacks.

## Wise Broker test

I tested the adjacent opportunity “does S improve cross-project generalization?” by inspecting nearest-neighbor repository overlap in the same leave-one-out run. The corpus is dominated by one incident per repository, so retrieval is necessarily cross-project; S still fell from RAW 64.7%/88.2% to 52.9%/70.6%. Result: no observed cross-project advantage under this encoder.

## Verdict

**STOP**

The smallest justified continuation would be a new, preregistered corpus with independently verified repair labels and a second cheap encoder (e.g. character n-gram TF–IDF), not an expansion of S. The current result does not justify building a privacy-preserving retrieval component.

## Reproduction and evidence

```sh
python3 research/semantic_bug_signature.py --collect > research/metrics.json
python3 research/semantic_bug_signature.py > /tmp/semantic-bug-signature-metrics.json
```

The first command refreshes the public snapshot; the second scores the fixed snapshot. Observed run: 34 incidents; no model/usage counter was available because no model was invoked. The scripts and snapshot are the complete local evidence bundle.
