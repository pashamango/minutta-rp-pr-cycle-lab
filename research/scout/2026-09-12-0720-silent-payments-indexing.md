# Research Scout — Silent Payments indexing vs probabilistic filters

Date: 2026-09-12
Status: FINDING_ONLY / NO EXECUTION AUTHORITY
Priority impact: none; no new candidate Issue created because the daily candidate backlog is already above the 1–3 target.

## Decision-relevant update

Bitcoin Optech #422 (2026-09-11) summarizes fresh measurements comparing BlindBit Oracle v2 (BIP352 Silent Payments indexing server) with compact-filter approaches over 255,434 unsampled blocks from Taproot activation through block 965,089.

Primary evidence:
- Bitcoin Optech #422: https://bitcoinops.org/en/newsletters/2026/09/11/
- BlindBit Oracle v2: https://github.com/setavenger/blindbit-oracle
- Measurement repo: https://github.com/bitsagarob/silentpayments-measurements
- Convergence draft: https://github.com/bitsagarob/silentpayments-measurements/blob/master/LIGHT-CLIENT-PROTOCOL-DRAFT.md

Observed tradeoff reported by Optech from the measurement work:
- BlindBit Oracle streams explicit per-output data (txid, tweak, 8-byte output prefix) instead of filters.
- It downloads about 2.1x as many bytes as a taproot-only filter plus the raw tweak data that a filter client still needs, before counting the full-block fetches caused by filter matches.
- In exchange, the Oracle path has no filter false positives and no per-match full-block fetch requirement.
- New integrity problem: a light client cannot currently know immediately if a server omitted a tweak, potentially causing missed funds. The implementation adds per-block commitments over the sorted tweak set and checkpoints them to Nostr every six hours, making omission attributable after the fact; clients should still fetch the full block on a match.
- BlindBit Oracle v2 is a substantial rewrite: PebbleDB, Bitcoin Core REST backend, reworked HTTP/gRPC APIs, and storage modes; it requires an unpruned Bitcoin Core node for spent-output access.

## Why this matters beyond Silent Payments

This is a useful real-world falsification of the intuition that probabilistic filters are automatically the cheapest privacy-preserving routing layer.

There are at least three separable costs:

1. **bandwidth/storage** — explicit indexes can be larger;
2. **false-positive follow-up** — probabilistic filters push cost downstream into extra fetches/verification;
3. **integrity/provenance** — an explicit oracle removes false positives but creates an omission-detection problem, which then needs commitments/checkpoints or independent verification.

For Reverse Semantic GPS / agent routing, the analogous design choice is:

`probabilistic coarse filter -> candidate neighborhood -> exact fetch`

versus

`explicit semantic oracle/index -> exact candidate stream + integrity commitment`.

The fresh Bitcoin result suggests we should not assume Bloom/GCS-like routing is globally cheaper. If false-positive follow-up or expensive exact retrieval dominates, a larger explicit index with compact commitments can win operationally.

## Reusable invariant

Approximate routing and explicit indexing trade different failure modes:

- probabilistic filter: cheap index, controlled false positives, exact source remains authoritative;
- explicit oracle: no filter false positives, but omission becomes the critical adversarial failure mode;
- commitment/checkpoint: makes omission detectable/attributable, but does not by itself guarantee liveness or immediate completeness.

For any semantic routing benchmark, measure **total end-to-end cost**, not index bytes alone:

`index transfer + false-positive follow-up + exact fetch/verification + integrity proof/checkpoint cost`.

## Recommendation

NO-OP for execution now. Preserve this as a benchmark design constraint for the existing Matryoshka/Reverse-GPS candidate (#142) rather than creating another competing Issue.

If #142 is later admitted, add one comparison arm:

- nested probabilistic/binary semantic routing;
- explicit compact candidate index/oracle;
- both measured end-to-end with false-positive follow-up and omission/integrity checks.

This is research-only evidence. It does not authorize implementation, model use, network changes, or Codex allocation.

## Quota discipline

`research/quota-governor-v0.md` reviewed this run: Luna/Light remains default for downstream Codex; no silent model substitution; no missing quota counters estimated; no Codex lane allocated.
