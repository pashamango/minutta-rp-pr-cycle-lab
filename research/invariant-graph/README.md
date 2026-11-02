# MIN-18: Invariant Graph — 30–50-Source Normalization and Falsification
**Repository:** `https://github.com/pashamango/minutta-rp-pr-cycle-lab.git`  
**Branch:** `minutta/min-18-invariant-graph-3050-source-normalization-and-falsification`  
**Linear Reference:** [MIN-18](https://linear.app/mindrock/issue/MIN-18/invariant-graph-30-50-source-normalization-and-falsification)  
**Builder Agent:** `agy@wolfram`  
**Status:** CANDIDATE / NOT EXECUTION-AUTHORIZED  

---

## Overview

This artifact package completes the normalization and falsification requirements of Linear ticket **MIN-18**.
It processes the first 45 meaningful comments from upstream Issue [#168](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168), maps them into structured claim units, builds a deduplicated graph topology, ranks the top 3 candidate invariants, formalizes three bounded falsification specifications, and catalogs excluded operational telemetry.

## Directory Structure

```
research/invariant-graph/
├── README.md                  # Executive overview
├── claim_schema.json          # Formal JSON Schema for structured claim unit
├── normalized_claims.json     # 45 normalized claim units with exact source-read evidence
├── claim_graph.json           # Machine-readable deduplicated claim graph (nodes, edges, clusters)
├── CLAIM_GRAPH.md             # Human-readable graph report with Mermaid diagrams and tables
├── falsification_specs.json   # Machine-readable bounded falsification specifications
├── FALSIFICATION_SPECS.md     # Detailed specifications for Top 3 candidates (nulls, tests, thresholds)
├── excluded_data.json         # Machine-readable catalog of excluded heartbeat/receipt records
└── EXCLUDED_DATA.md           # Documentation of excluded data and constitutional exclusion policy

tests/
└── test_invariant_graph.py    # Complete test suite validating schema, graph, and invariants
```

## Top 3 Ranked Invariants

1. **Rank 1:** Conserved Evidence Portfolio Simplex & Matched Search-Budget Invariant (`CLAIM-011`, Wang 2025 Biometrika admissible merge).
2. **Rank 2:** Golden Trinity Ratio Permutation-Matched Dirichlet Simplex Invariant (`CLAIM-001`, out-of-sample held-out falsification).
3. **Rank 3:** Durable Dispatch-Boundary Process-Binding Invariant (`CLAIM-003`, leaf PID vs wrapper exit status 137).

## Acceptance Criteria Checklist

- [x] **Structured Claim Units:** 45 claim units created with source URL/ID, exact source-read evidence, epistemic label, assumptions, null test, contradictions, duplicates, applications, versions.
- [x] **Deduplicated Claim Graph:** Connected graph with nodes, directed edges, cluster topologies, and cross-cluster relations.
- [x] **Top 3 Candidate Ranking:** Clustered and ranked with formal scores and domain rationales.
- [x] **Three Bounded Falsification Specs:** Rigorous specs with null hypotheses, test procedures, pass/fail thresholds, and cheapest tests.
- [x] **Documented Excluded Data:** Explicit cataloging of heartbeat records (`GITHUB_RUN_RECEIPT/v1`) with IDs, timestamps, and exclusion rationale.
- [x] **Direct Object Read:** All claims and excluded records verified by direct read of upstream Issue #168.
- [x] **No Giant Mirror:** Compact, normalized, structured epistemic representation.
- [x] **Handoff Gate Protocol:** Full Git coordinates, atomized commit, zero-trust worktree isolation.
