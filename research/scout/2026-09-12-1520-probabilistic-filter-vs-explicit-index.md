# Research Scout — probabilistic filter vs explicit index trade-off

`RESEARCH_SCOUT_ITERATION/v1`

- local_timestamp: 2026-09-12 15:20 America/Los_Angeles
- topic: probabilistic/Bloom-like routing vs explicit per-item index, using Silent Payments light-client benchmarks as a real-world analogue
- source/evidence:
  - Bitcoin Optech Newsletter #422 (2026-09-11): https://bitcoinops.org/en/newsletters/2026/09/11/
  - Rob Segers / BlindBit Oracle v2 benchmark summarized there; comparison covers 255,434 unsampled blocks from Taproot activation through block 965,089.
- finding: BlindBit Oracle v2 drops compact filters and streams per-output `(txid, tweak, 8-byte output prefix)` data. In the reported benchmark it downloads about **2.1x** the bytes of a taproot-only compact filter plus raw tweak data, before accounting for full blocks that filter clients must fetch on matches. The explicit stream eliminates filter false positives and per-match block fetches, but creates a different integrity risk: a server can omit a tweak and silently cause a receiver to miss funds. The implementation therefore publishes per-block commitments over sorted tweak sets and checkpoints them to Nostr, making omission attributable after the fact; clients are still advised to fetch the full block on a match.
- confidence: high for the architectural trade-off; quantitative break-even is workload-dependent and the newsletter does not establish a universal winner.
- relevance: direct caution for Reverse Semantic GPS / semantic Bloom routing. A coarse probabilistic filter is not automatically inferior because it has false positives: replacing it with an explicit candidate stream can increase bandwidth materially and transfer failure from `false-positive extra work` to `indexer omission / provenance integrity`. For semantic/agent routing, preserve a cheap probabilistic region filter as the default unless measured downstream candidate-fetch cost dominates; if a centralized/derived explicit index is introduced, bind it to verifiable commitments or another omission-detection mechanism.
- outcome: SURVIVED — Bloom/probabilistic coarse routing remains a strong default; the evidence weakens any blanket plan to replace it with a no-false-positive semantic index.
- candidate_handoff: none. This is a design constraint for existing semantic-routing candidates, not a new execution opportunity.

## Decision rule carried forward

Prefer:

`cheap probabilistic region filter -> exact/local verification`

until measurements show:

`false-positive downstream cost > explicit-index bandwidth + index-integrity/provenance cost`.

If an explicit derived index is used, require omission-detection / commitment semantics; correctness of returned entries is insufficient if missing entries are economically or semantically dangerous.

## Quota discipline

Web/Git research only. No Codex execution allocated. Per `research/quota-governor-v0.md`, Luna/Light remains the downstream default and missing quota counters were not estimated.
