# Research Scout — Silent Payments retrieval tradeoff

Date: 2026-09-15
Priority: P3
Status: CANDIDATE / NOT EXECUTION-AUTHORIZED

## Evidence
Bitcoin Optech #422 (2026-09-11) summarizes Rob Segers' BlindBit Oracle v2 benchmark over 255,434 unsampled blocks from Taproot activation through block 965,089. The server drops compact filters and streams per-output `(txid, tweak, 8-byte output prefix)` data. Reported bandwidth is ~2.1x a Taproot-only filter plus raw tweak data, before counting full-block downloads caused by filter matches. The stream has no false positives and avoids per-match block fetches. A key integrity limitation remains: a light client cannot directly detect an omitted tweak; the implementation publishes per-block commitments over sorted tweak sets and checkpoints them to Nostr every six hours, making omissions attributable after the fact.

Primary summary: https://bitcoinops.org/en/newsletters/2026/09/11/

## Decision-relevant finding
Probabilistic filters are not automatically the cheapest end-to-end retrieval primitive. A more verbose exact candidate stream can win when false positives trigger expensive downstream fetches. Conversely, removing false positives introduces a source-completeness/provenance problem: the server can omit a relevant item unless the response set is committed/audited.

This maps directly to reverse semantic routing: compare `coarse probabilistic region -> expensive object fetch` against `larger exact/near-exact candidate stream -> no false-positive fetch`, while separately measuring omission detectability.

## Opportunity Card
- Proposed asset/capability: a tiny benchmark/spec for semantic routing that compares Bloom/LSH-style coarse filters with exact-prefix/candidate streaming under realistic downstream verification costs, including an explicit completeness-commitment dimension.
- Expected value: scientific/infrastructure leverage. Could falsify the assumption that Bloom-like coarse routing is optimal for claim retrieval and sharpen Reverse Semantic GPS protocol choices.
- Time-to-first-useful-result: day for a bounded synthetic benchmark/spec; no execution authorized here.
- Complexity/risk: low–medium. Main uncertainty is whether realistic semantic candidate distributions make downstream fetch cost large enough to reverse the bandwidth tradeoff.
- Smallest falsification: analytically sweep false-positive rate, candidate-stream bytes/item, object-fetch bytes, match prevalence, and omission-proof overhead; identify the break-even surface before implementing anything.
- Compute cost class: low/local; no Codex required for the falsification model.
- Why now: fresh Bitcoin benchmark provides a concrete real-system counterexample to treating probabilistic filters as an obvious default.

## Scout disposition
Preserve as P3 candidate only. Do not CLAIM, dispatch, or allocate Codex/NICLI/local runner work. Research Market may later decide whether the break-even analysis deserves execution.
