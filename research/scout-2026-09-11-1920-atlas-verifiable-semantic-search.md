# Research Scout — Atlas verifiable semantic search

Date: 2026-09-11
Status: research finding only; no execution authorized

## Signal

A new paper, **Atlas: Efficient Verifiable Semantic Search** (Avramov, Lycklama, Viand, Hithnawi; arXiv:2609.11841, submitted 2026-09-10), demonstrates zero-knowledge verification of **HNSW graph-based semantic search** against a committed private index.

Primary source: https://arxiv.org/abs/2609.11841

Reported results in the paper abstract:
- proves that a query was answered according to the specified HNSW search over a committed index without revealing the index beyond the result;
- preserves plaintext-HNSW recall rather than switching to an easier-to-prove cluster index;
- proving time under 1 second on SIFT1M;
- about 2.0 seconds at 100 million vectors;
- shifts database-dependent work into preprocessing, so online proving scales with traversal rather than full database size;
- restructures HNSW into a fixed-size-state procedure and batches traversal-step arguments.

## Decision relevance

This is unusually close to the Reverse Semantic GPS / ChitAkasha direction. Prior thinking separated semantic routing from proof: find a neighborhood, then prove downstream predicates. Atlas suggests the **retrieval route itself can become a verifiable object**.

Potential architecture:

`claim / probe -> semantic embedding/hash -> HNSW neighborhood traversal -> proof of faithful retrieval -> constitutional evaluation -> effect proof`

This could address an important trust gap: a remote or delegated semantic index cannot silently truncate, bias, or substitute candidate neighborhoods without detection, assuming the committed index and proof system are trusted.

## Why this matters more than another embedding model

The strategic novelty is not better semantic similarity. It is converting approximate graph retrieval from an opaque heuristic into a **cryptographically attestable procedure** while retaining HNSW-style recall and scale. That is directly relevant to sovereign agents that need to prove not only the final decision but also that relevant precedent/evidence retrieval followed the declared process.

## Constraints / uncertainties

- Evidence is currently the authors' arXiv report; no independent replication was found in this run.
- Reported proving latency may still be too high for every interactive lookup, especially on local hardware; batching/caching may be necessary.
- The paper proves execution of the declared retrieval algorithm, not semantic truth, embedding quality, corpus completeness, or fairness of the committed index.
- It does not by itself solve provenance of documents/claims inside the index.

## Opportunity assessment

Qualitative option value: **HIGH**, but no new Issue created this run because the daily target of 1–3 candidate opportunities is already satisfied. Preserve for Research Market / next backlog triage rather than generating filler or over-admitting candidates.

Possible future P2 candidate if not superseded:
- **Asset/capability:** bounded comparison of Atlas-style verifiable HNSW against the current Reverse Semantic GPS prototype architecture.
- **Time-to-first-useful-result:** day for paper/code review; week for a toy feasibility test if implementation is available.
- **Complexity/risk:** medium-high; main uncertainty is prover cost and implementation maturity.
- **Smallest falsification:** verify availability/reproducibility of code and reproduce one tiny committed-index query proof locally; stop if proving cost or dependencies are incompatible with local/private constraints.
- **Codex/local-compute cost:** research negligible; feasibility test medium local compute, no expensive model required.

## Quota discipline

No Codex execution requested. No model step-up. This run used web/Git research only, consistent with `research/quota-governor-v0.md`; missing quota counters were not estimated.
