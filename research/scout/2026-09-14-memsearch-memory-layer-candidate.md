# P2 CANDIDATE / NOT EXECUTION-AUTHORIZED — MemSearch cross-agent memory layer

Date: 2026-09-14
Scout status: evidence captured; no CLAIM; no execution authorized.

## Finding
`zilliztech/memsearch` is a materially mature local-first persistent memory layer aimed explicitly at Codex/Claude Code/DSH-style agents. As of 2026-09-14/15 GitHub metadata shows ~2.6k stars, 249 forks, MIT license, and active maintenance; v0.4.20 was prepared 2026-09-12. Its architecture keeps Markdown as source of truth and treats Milvus as a rebuildable shadow index, with hybrid dense+BM25 retrieval, RRF reranking, progressive retrieval, deduplication, live sync, and SHA-256 skip of unchanged content. Recent commits harden session capture/summarizer lifecycle and prompt-hook compatibility.

Primary evidence:
- https://github.com/zilliztech/memsearch
- https://github.com/zilliztech/memsearch/commit/f863056e0b113d44e860dd6abf5bb892781e29ca (v0.4.20 preparation, 2026-09-12)
- https://github.com/zilliztech/memsearch/commit/15ad962364c0dc5a552af78a7ef6bf1575487ec9 (prompt-hook compatibility, 2026-09-12)

## Opportunity Card
- Proposed asset/capability: bounded adapter/benchmark for a shared, local-first memory substrate across Codex/NICLI/mailbox agents, preserving Git/Markdown auditability while using semantic retrieval as a derived cache.
- Expected value: infrastructure leverage HIGH if it reduces repeated context reconstruction and token/quota burn; strategic optionality HIGH because Markdown remains portable and index can be rebuilt.
- Time-to-first-useful-result: day (isolated benchmark), week (safe adapter if positive).
- Complexity/risk: MEDIUM. Main uncertainties: Milvus footprint/operational burden, retrieval precision on actual mailbox/research artifacts, contamination/authority boundaries between agents, and whether token savings exceed indexing overhead.
- Smallest falsification test: on an isolated copy of 50–200 non-secret research/mailbox Markdown artifacts, compare baseline exact/manual retrieval vs MemSearch for 20 known historical questions. Measure recall@k, wrong-context rate, retrieval latency, prompt tokens injected, index size, and rebuildability. No writes to canonical memory; no external service.
- Codex/local-compute cost: Codex LOW if Research Market admits; local compute LOW–MEDIUM. Luna/Light remains default; no model step-up implied.
- Why now: project is actively maintained and explicitly supports Codex-style agents; current architecture directly matches the desired pattern `human-readable source of truth -> disposable semantic shadow index`.
- Option-value score: HIGH, because falsification is cheap and a positive result could reduce repeated context/token cost across many workflows.

## Decision boundary
Do not install into canonical Wolfram/Darwin/NICLI infrastructure yet. Research Market may create an executable successor only after checking active WIP and quota. A positive test must preserve per-agent authority boundaries and demonstrate that semantic recall does not silently broaden access to artifacts.

## Quota discipline
Per `research/quota-governor-v0.md`: no quota counters inferred; no scarce Codex execution allocated; Luna/Light default unchanged.