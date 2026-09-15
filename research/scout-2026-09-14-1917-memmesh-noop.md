# Research Scout — MemMesh 2.0 overlap / NO-OP

Date: 2026-09-14 PT
Verdict: **NO-OP — do not create another memory candidate.**

## Evidence

Primary upstream inspected: `bvalach/memmesh` README on default branch.

MemMesh/SharedMem is a local MCP semantic-memory server using persistent ChromaDB plus local `all-MiniLM-L6-v2`. Its 2.0 surface adds explicit budget-aware retrieval: `memory_brief` first, escalation to `memory_pack` only when broader context is required, entity-targeted retrieval, compact `turn_summary`, and selective durable promotion. It also offers a lightweight lexical backend. Upstream explicitly warns that trusted local clients are required because results may expose indexed contents and absolute paths.

Source: https://github.com/bvalach/memmesh

## Decision relevance

The `brief -> pack only if needed` pattern is directionally useful for scarce-context/quota discipline, but it does **not** justify a new opportunity Issue now. Existing backlog already covers the same option space more directly:

- #193 PAXM local cross-agent memory feasibility — local/provider-neutral memory with explicit provenance/authority guardrails.
- #224 Deterministic retrieval reflex before LLM memory calls — cheaper pre-model narrowing intended specifically to avoid unnecessary semantic/model retrieval.
- #29 KNOWLEDGE-0001 — Git remains canonical durable memory; search indexes are disposable acceleration.

Adding MemMesh as a third/fourth memory implementation candidate would increase comparison/WIP burden without a presently verified capability that dominates those candidates.

## Reusable observation

If Research Market later admits a memory benchmark, add **budgeted progressive retrieval** as an evaluation dimension independent of backend:

`exact/deterministic lookup -> compact semantic brief -> wider pack only on uncertainty`

Measure context bytes/tokens injected, answer/retrieval quality, stale/wrong injection rate, provenance retention, and calls avoided. Do not infer account quota percentages from token counts.

## Guardrail

No install, no Codex allocation, no production indexing change, no new candidate Issue from this Scout pass. Luna/Light remains the downstream default under `research/quota-governor-v0.md`; missing quota counters remain unknown rather than estimated.
