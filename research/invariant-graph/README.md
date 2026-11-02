# MIN-18: Invariant Graph — 30–50-Source Normalization and Falsification

**Status:** CANDIDATE / NOT EXECUTION-AUTHORIZED
**Authority:** MIN-18 Foundry Acceptance Protocol
**Canonical Upstream:** [https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168)
**Verification Suite:** `python3 -m unittest -v tests/test_invariant_graph.py`

---

## 1. Executive Summary

This repository directory contains the formal deliverables for Linear ticket **MIN-18**:
1. **Direct Object Ingestion & Normalization**:
   - Ingested 45 meaningful comments from upstream Issue #168.
   - Every claim is anchored by exact verbatim source-read evidence, verified character-for-character against GitHub REST direct objects.
   - Includes source ID, direct URL, author, timestamp, full body SHA-256 digest, epistemic label, explicit assumptions, quantitative null test, contradictions, applications, and versions.
2. **Canonical Deduplication & Clean Lineage**:
   - Deduplicated into **6 Canonical Invariants** (`CANONICAL-01` to `CANONICAL-06`).
   - Every claim unit includes structured `duplicate_lineage` (`CANONICAL_ORIGIN`, `SEMANTIC_DUPLICATE`, `REFINEMENT`, `EMPIRICAL_INSTANCE`) and an explicit `merge_rule`.
   - Eliminates arbitrary chained duplicate pointers and removes all ambiguous relations (`refines_or_deduplicates`).
   - `CANONICAL-05` strictly governs process-binding and credential boundary identity (`CLAIM-003`, `CLAIM-009`).
   - `CANONICAL-02` strictly governs redundancy vs true value (`CLAIM-040`, `CLAIM-042`, `CLAIM-044`, `CLAIM-045`), rooted at `CLAIM-040`.
   - `CANONICAL-01` governs evidence capital and ancestry algebra (`CLAIM-004`, `007`, `008`, `011`, `012`, `014`, `016`, `019`, `020`, `026`).
   - `CANONICAL-06` cleanly decomposes capability, linear resource, and semilattice sub-trees.
3. **Graph Topology & Strict Cluster Counts**:
   - **Cluster-1: Epistemic Accounting & Anti-Sybil Invariants**: 10 claims.
   - **Cluster-2: Golden Trinity & Ratio Dynamics**: 16 claims.
   - **Cluster-3: Distributed Membrane, Host Isolation & Identity Boundaries**: 19 claims.
   - **Total:** 45 claims (100% consistent across JSON artifacts, markdown reports, and unit tests).
4. **Reproducible Candidate Ranking & Top 3 Falsification Specs**:
   - Formal multi-criteria rubric (IDEIR-v1) with weights: $0.35 \cdot C_1 + 0.30 \cdot C_2 + 0.20 \cdot C_3 + 0.15 \cdot C_4$.
   - Objective score band compliance verified for all 6 canonical invariants:
     - **Rank 1 (9.8):** `CANONICAL-01` (Anchor: `CLAIM-011`) — Conserved Evidence Portfolio Simplex & Matched Search-Budget Invariant.
     - **Rank 2 (9.3):** `CANONICAL-02` (Anchor: `CLAIM-040`) — Target-Conditioned Redundancy vs. True Value Invariant.
     - **Rank 3 (8.9):** `CANONICAL-05` (Anchor: `CLAIM-003`) — Durable Dispatch-Boundary Process-Binding Invariant.
5. **Documented Excluded Data**:
   - 20 sampled automated run receipts (`GITHUB_RUN_RECEIPT/v1`), empty NO-OP cycles, and heartbeat telemetry cataloged with exact source IDs and exclusion rationale.
6. **Direct-Object-Read Verification Suite**:
   - `direct_objects_cache.json` containing 65 direct objects (45 claims + 20 excluded records).
   - Automated unit test suite (`tests/test_invariant_graph.py`) verifying exact evidence matching, source URLs/IDs, SHA-256 digests, acyclic duplicate lineage, semantic fixtures concordance across all 45 claims, strictly typed graph relations, and scoring formula reproducibility.

---

## 2. Directory Layout

- `claim_schema.json`: Formal JSON Schema for normalized claim units.
- `direct_objects_cache.json`: Direct GitHub API comment objects for all 45 claims and 20 excluded records.
- `normalized_claims.json`: 45 structured claim units with exact verbatim evidence and duplicate lineage.
- `claim_graph.json`: Directed graph topology containing canonical invariants, source claims, and typed edges.
- `CLAIM_GRAPH.md`: Architectural documentation and Mermaid visualizations.
- `falsification_specs.json`: Machine-readable specifications for top 3 candidates with scoring breakdown.
- `FALSIFICATION_SPECS.md`: Mathematical formulations, null hypotheses, and protocols for the top 3 invariants.
- `excluded_data.json`: Catalog of 20 excluded automated receipts and heartbeats.
- `EXCLUDED_DATA.md`: Documented exclusion rationale and source IDs.
