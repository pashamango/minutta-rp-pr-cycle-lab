# Research Scout — Silent Payments filter vs oracle tradeoff

Date: 2026-09-11
Status: FINDING / NO EXECUTION AUTHORIZED

## Decision-relevant update

Fresh mainnet measurements quantify a long-standing light-client design tradeoff for BIP352 Silent Payments. Across 255,434 unsampled mainnet blocks (709,656 through 965,089), a hypothetical taproot-only compact filter is estimated at ~0.94 GB total (~3.7 KB/block, ~0.4 MB/day), while the shipping BlindBit Oracle v2 complete scanning payload is ~15.08 GB (~59 KB/block, ~8 MB/day). End-to-end, once a filter client also downloads the raw tweak data it still needs, the filter path is ~7.1 GB vs ~15.1 GB for the oracle path: the shipping oracle pays roughly 2.1x bandwidth for zero filter false positives and no full-block downloads during scanning.

Primary evidence:
- Bitcoin Optech #422 (2026-09-11): https://bitcoinops.org/en/newsletters/2026/09/11/
- Measurement repo and reproducible raw series/scripts: https://github.com/bitsagarob/silentpayments-measurements
- BlindBit Oracle v2: https://github.com/setavenger/blindbit-oracle

## Negative / integrity result

The server-assisted path does not eliminate trust by itself. A light client cannot currently know in real time whether the server omitted a tweak; omission could silently lose incoming funds. BlindBit publishes per-block commitments over the sorted tweak set and checkpoints them periodically, making omissions attributable after the fact, but this is not equivalent to trustless completeness. Clients should still fetch/verify the full block on a match.

## Relevance to Pasha's work

This is a useful empirical falsification of a tempting assumption for reverse-semantic/Bloom routing: removing probabilistic filters does not make the system strictly better. It trades false positives and match fetches for materially higher baseline bandwidth plus a completeness/provenance problem.

Generalized design lesson for claim routing:

`coarse probabilistic filter -> exact local verification`

remains attractive when bandwidth/compute is scarce, provided false negatives are structurally excluded. A server-generated exact shortlist can remove false positives, but then requires an independently verifiable completeness commitment. This mirrors the ChitAkasha distinction between proof of a predicate and proof that the source supplied the complete relevant evidence set.

## Scout verdict

NO-OP on implementation. Do not replace Bloom/probabilistic coarse routing with centralized/exact index routing based on elegance alone. Preserve both as swappable strategies and benchmark the real cost surface (bytes, false-positive work, exact-fetch cost, and completeness proof) before architectural commitment.

No Codex allocation requested. Luna/Light default and quota-governor constraints unchanged.