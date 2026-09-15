# Research Scout — 2026-09-15 06:20 PT

Status: FINDING / NO EXECUTION AUTHORIZED
Priority: P3 candidate insight; no Issue created in this run.

## Finding
Bitcoin Optech #422 (2026-09-11) reports a useful measured tradeoff for Silent Payments light clients. BlindBit Oracle v2 drops probabilistic compact filters and streams per-output data (txid, tweak, 8-byte output prefix). Across 255,434 unsampled blocks from Taproot activation through block 965,089, it downloaded about 2.1x the bytes of a taproot-only filter plus tweak data, but eliminated filter false positives and per-match full-block fetches. The remaining correctness problem is omission: a server can omit a tweak and silently cause missed funds. The implementation therefore publishes per-block commitments over sorted tweak sets and checkpoints them to Nostr every six hours, making omissions attributable after the fact; clients should still fetch the full block on a match.

Primary source summary: https://bitcoinops.org/en/newsletters/2026/09/11/

## Decision relevance
This is a concrete counterexample to treating Bloom/compact-filter routing as automatically optimal. For semantic routing or agent discovery, a slightly larger deterministic stream may dominate a smaller probabilistic filter when false-positive follow-up is expensive. But deterministic streaming introduces a different trust failure: omission. The complementary primitive is therefore not merely `filter vs index`; it is `probabilistic coarse routing` versus `deterministic candidate stream + commitment/audit path`.

## Proposed asset/capability
Potential future P3: a tiny benchmark harness comparing (A) Bloom-like semantic candidate filters and (B) deterministic compact candidate streams with Merkle commitments, under configurable candidate density and verification cost.

Expected value: scientific/infrastructure leverage; could give Reverse Semantic GPS an evidence-based routing rule instead of assuming Bloom filters are always best.
Time-to-first-useful-result: day.
Complexity/risk: low/medium; main uncertainty is choosing a representative semantic workload.
Smallest falsification: analytic/synthetic sweep of bytes/query, false-positive follow-up cost, omission-detection overhead, and candidate density; no LLM required.
Compute cost: local CPU / negligible; no Codex allocation requested.
Why now: Bitcoin has supplied a measured real-world analogue with 255k+ blocks and an explicit omission-integrity failure mode.

## Scout decision
Persist finding only. Do not dispatch. A candidate Issue is justified only if Research Market needs a routing benchmark or Reverse Semantic GPS work becomes active.
