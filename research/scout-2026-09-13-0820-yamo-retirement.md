# Research Scout — YAMO chain retirement as a negative feasibility signal

Date: 2026-09-13
Priority: research evidence only; no execution authorization

## Finding

YAMO Protocol, an open protocol for immutable/verifiable agent reasoning traces anchored to Ethereum Sepolia with optional IPFS bundling, was archived in September 2026. Its core, contracts, CLI, MCP bridge and explorer are deprecated/unmaintained; the organization explicitly says not to start new work on them. GitHub also confirms `yamo-core` is archived, has 0 stars/forks, and its last push was 2026-01-06. The separate `@yamo/memory-mesh` project remains active.

Primary evidence:
- https://github.com/yamo-protocol/ — organization README, September 2026 archive notice
- https://github.com/yamo-protocol/yamo-core — archived repository metadata
- https://github.com/yamo-protocol/yamo-memory-mesh — active semantic-memory subsystem

## Decision relevance

This is a useful negative result for ChitAkasha / agent-proof architecture: a full blockchain/IPFS anchoring layer for reasoning traces appears to have failed to earn enough adoption/maintenance to justify continuing as a standalone protocol, while the lower-cost semantic-memory component survived.

Do **not** infer that verifiable provenance is useless. The narrower conclusion is that `reasoning trace -> blockchain anchor` should not be our default architecture or product wedge without a concrete counterparty that needs on-chain settlement.

Prefer a layered design:

`local append-only audit log -> content hash / commitment -> optional signed receipt -> optional external/on-chain anchor only at settlement boundaries`

This preserves auditability while avoiding latency, operational complexity, privacy leakage, and chain dependence for every internal agent step.

## Opportunity / falsification consequence

No new Issue created. This finding argues *against* spending scarce Codex quota on a blockchain-first audit substrate now.

Smallest future falsification test, only if a real use case appears: take one existing mailbox/claim workflow and compare local signed receipts versus external-chain anchoring on latency, operator complexity, privacy, recovery semantics, and actual verifier demand. Until then: NO-OP.

## Quota / authority note

No Codex execution requested. Luna/Light default and Research Market allocation boundaries remain unchanged; missing quota counters were not estimated.