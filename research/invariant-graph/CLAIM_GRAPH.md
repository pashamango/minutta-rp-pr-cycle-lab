# MIN-18 Invariant Claim Graph & Canonical Deduplication

## 1. Overview & Architecture

The **MIN-18 Invariant Graph** represents the structured normalization, canonical deduplication, and topological relationship mapping of 45 substantive claims extracted via direct object reads from GitHub upstream [Issue #168](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168).

### Two-Tier Graph Architecture
To resolve defect MIN-18-QA-01 (where raw comments were chained arbitrarily without canonical invariant definitions), the graph implements a **two-tier epistemic architecture**:
1. **Tier 1: Canonical Invariants (`CANONICAL-01` to `CANONICAL-06`)**:
   Defines the core invariant principles that govern cross-agent research, epistemic accounting, and systems execution.
2. **Tier 2: Source Claim Units (`CLAIM-001` to `CLAIM-045`)**:
   Individual comments extracted verbatim from primary sources, mapped to canonical invariants with explicit duplicate lineage and formal merge rules.

### Strict Typing of Graph Relations
Ambiguous relations such as `refines_or_deduplicates` are completely eliminated. All edges strictly adhere to one of the following formal relations:
- `maps_to_canonical`: Direct projection from a source claim unit to its governing canonical invariant.
- `refines`: Claim A specializes, parameterizes, or sharpens the mathematical/empirical boundary of Claim B.
- `generalizes`: Claim A broadens or abstracts the theoretical domain of Claim B.
- `supports`: Empirical telemetry or formal proof from Claim A corroborates Claim B.
- `contradicts`: Empirical or analytical findings of Claim A constrain or falsify assumptions in Claim B.
- `duplicates`: Claim A restates Claim B with equivalent semantic content under different nomenclature.

---

## 2. Canonical Invariants Registry

| Canonical ID | Anchor Claim | Invariant Title | Domain Cluster | Primary Source URL |
|---|---|---|---|---|
| `CANONICAL-01` | `CLAIM-011` | Conserved Evidence Portfolio Simplex & Matched Search-Budget Invariant | Cluster-1: Epistemic Accounting | [#168#issuecomment-5649859218](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5649859218) |
| `CANONICAL-02` | `CLAIM-019` | Target-Conditioned Redundancy vs. True Value Invariant | Cluster-1: Epistemic Accounting | [#168#issuecomment-5651549808](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5651549808) |
| `CANONICAL-03` | `CLAIM-001` | Golden Trinity Ratio Permutation-Matched Dirichlet Simplex Invariant | Cluster-2: Golden Trinity Dynamics | [#168#issuecomment-5648693413](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5648693413) |
| `CANONICAL-04` | `CLAIM-036` | Teleological Semantics & Asymmetric Cause-Purpose Partitioning Invariant | Cluster-2: Golden Trinity Dynamics | [#168#issuecomment-5655337455](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5655337455) |
| `CANONICAL-05` | `CLAIM-003` | Durable Dispatch-Boundary Process-Binding Invariant | Cluster-3: Membrane & Isolation | [#168#issuecomment-5648743239](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5648743239) |
| `CANONICAL-06` | `CLAIM-018` | Cryptographic Zero-Trust Membrane & Mutual Multi-Pass Invariant | Cluster-3: Membrane & Isolation | [#168#issuecomment-5651293792](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-5651293792) |

---

## 3. Cluster Distribution & Verification

- **Cluster-1: Epistemic Accounting & Anti-Sybil Invariants**: 10 claims (`CLAIM-004`, `CLAIM-007`, `CLAIM-008`, `CLAIM-011`, `CLAIM-012`, `CLAIM-014`, `CLAIM-016`, `CLAIM-019`, `CLAIM-020`, `CLAIM-026`).
- **Cluster-2: Golden Trinity & Ratio Dynamics**: 16 claims (`CLAIM-001`, `CLAIM-002`, `CLAIM-005`, `CLAIM-006`, `CLAIM-010`, `CLAIM-013`, `CLAIM-023`, `CLAIM-024`, `CLAIM-025`, `CLAIM-032`, `CLAIM-034`, `CLAIM-036`, `CLAIM-037`, `CLAIM-039`, `CLAIM-041`, `CLAIM-043`).
- **Cluster-3: Distributed Membrane, Host Isolation & Identity Boundaries**: 19 claims (`CLAIM-003`, `CLAIM-009`, `CLAIM-015`, `CLAIM-017`, `CLAIM-018`, `CLAIM-021`, `CLAIM-022`, `CLAIM-027`, `CLAIM-028`, `CLAIM-029`, `CLAIM-030`, `CLAIM-031`, `CLAIM-033`, `CLAIM-035`, `CLAIM-038`, `CLAIM-040`, `CLAIM-042`, `CLAIM-044`, `CLAIM-045`).

**Total Ingested Claims:** Exactly 45 claims (verified in `normalized_claims.json`, `claim_graph.json`, and `test_invariant_graph.py`).

---

## 4. Top-Level Canonical Invariant Graph

```mermaid
graph TD
    subgraph Cluster1["Cluster-1: Epistemic Accounting & Anti-Sybil (10 claims)"]
        C01["CANONICAL-01<br/>Conserved Evidence Portfolio Simplex<br/>(Anchor: CLAIM-011, Rank 1: 9.8)"]
        C02["CANONICAL-02<br/>Target-Conditioned Redundancy<br/>(Anchor: CLAIM-019)"]
        C02 -->|refines| C01
    end

    subgraph Cluster2["Cluster-2: Golden Trinity & Ratio Dynamics (16 claims)"]
        C03["CANONICAL-03<br/>Golden Trinity Dirichlet Simplex<br/>(Anchor: CLAIM-001, Rank 2: 9.2)"]
        C04["CANONICAL-04<br/>Teleological Semantics Cause-Telos<br/>(Anchor: CLAIM-036)"]
        C04 -->|generalizes| C03
        C03 -.->|supports| C01
    end

    subgraph Cluster3["Cluster-3: Distributed Membrane & Isolation (19 claims)"]
        C05["CANONICAL-05<br/>Durable Dispatch-Boundary Binding<br/>(Anchor: CLAIM-003, Rank 3: 8.9)"]
        C06["CANONICAL-06<br/>Zero-Trust Cryptographic Membrane<br/>(Anchor: CLAIM-018)"]
        C06 -.->|supports| C05
    end
```
