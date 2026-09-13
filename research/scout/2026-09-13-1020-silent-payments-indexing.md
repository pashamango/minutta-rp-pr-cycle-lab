# Research Scout — Silent Payments indexing benchmark

Date: 2026-09-13
Priority: P3 research signal
Execution authority: NONE

## Finding
Bitcoin Optech #422 (2026-09-11) summarizes new measurements by Rob Segers comparing BlindBit Oracle v2 against compact block filters for silent-payment light clients over 255,434 unsampled blocks from Taproot activation through block 965,089.

BlindBit Oracle v2 streams per-output `(txid, tweak, 8-byte output prefix)` records and omits filters entirely. Reported tradeoff: roughly 2.1x the bytes of a Taproot-only compact filter plus raw tweak data, but with no false positives and no per-match full-block fetches. The remaining trust gap is omission: a server can omit a tweak and make a receiver miss funds. The implementation therefore publishes per-block commitments over the sorted tweak set and checkpoints them to Nostr every six hours, making omissions attributable after the fact; clients should still fetch the full block on a match. The implementation has also drifted from the older spec, so a convergence draft is now under discussion.

Primary source summary: https://bitcoinops.org/en/newsletters/2026/09/11/

## Decision relevance
This is a useful falsification of the naive assumption that probabilistic filters are automatically the best privacy/light-client primitive. For this workload, a deterministic streamed index can plausibly trade ~2.1x bandwidth for zero false positives and fewer follow-up fetches.

The stronger reusable pattern for ChitAkasha / semantic routing is:

`server-provided coarse index -> compact commitment -> client-local verification / selective full retrieval`

This suggests a design alternative to Bloom-like semantic routing: for some high-value claim classes, deterministic typed summaries plus commitments may beat probabilistic membership filters when false-positive follow-up is expensive.

## Recommendation
No execution candidate yet. Keep as a design reference for Reverse Semantic GPS / claim routing. If a semantic-filter prototype later shows expensive false-positive retrieval, compare it against a deterministic streamed-prefix index with commitments before optimizing Bloom parameters.

## Quota note
No Codex allocation requested. Public-web/Git research only. Quota governor respected: Luna/Light remains the default downstream model; missing quota counters were not estimated.
