# Research Scout — VikingRAG retrieval-trace reuse

Date: 2026-09-13 05:20 America/Los_Angeles
Status: EVIDENCE ONLY / NO EXECUTION AUTHORIZATION
Decision class: quota-efficiency / semantic-memory architecture

## Finding

Fresh paper: **VikingRAG: Accurate and Token-efficient Retrieval-augmented Generation over Structured Documents** (arXiv:2609.11390, submitted 2026-09-10) proposes a directory-aware semantic/structural retrieval system that turns successful multi-round retrieval traces into reusable **experience edges** and escalates to expensive agentic retrieval only when one-round evidence is insufficient.

Primary source: https://arxiv.org/abs/2609.11390

Author-reported results: the base system matches strong structured-RAG accuracy while using 11.6%–51.9% of comparison token cost; with trace reuse + adaptive escalation, token use drops to 5.1%–32.5% while retaining competitive accuracy. Treat these as paper claims, not locally reproduced measurements.

## Why it matters here

This is directly relevant to the quota governor: the useful primitive is not another model, but **materializing successful search/reasoning routes so later similar tasks do not rediscover the same structure**. It gives a concrete architecture for the current `specialist -> web/Git analysis -> candidate handoff` lane:

`query -> cheap experience-edge lookup -> sufficient? answer : bounded multi-round retrieval -> persist trace edge`

Potential reuse areas if later admitted:
- Research Scout / weekly synthesis: cache source-to-claim and source-to-project routes rather than rereading the same corpus.
- NICLI/mailbox: retain proven navigation paths between issue, evidence, PR and authority records without treating cached paths as authority.
- Reverse Semantic GPS: the trace itself becomes a learned route through semantic space, not merely a nearest-neighbor result.

## Decision impact

**No new candidate Issue created in this run.** The current backlog already contains several fresh P2/P3 quota/memory/retrieval candidates, and this paper does not yet justify adding another implementation lane before those are ranked. Record as a strong architectural input for future consolidation of memory/quota candidates.

The main design implication worth preserving is:

`retrieval trace != truth or authority`

A reused experience edge may propose where to look next, but final evidence, authority and settlement checks must still execute against current state.

## Smallest future falsification (only if Research Market later consolidates/adopts this idea)

Replay a small set of repeated research tasks with and without route/trace reuse. Measure only observable quantities: repeated source fetches, model/tool calls, latency, correctness, stale-route rate, and tokens when actually exposed. Falsify if trace reuse materially increases stale/wrong routing or gives negligible savings on real repeated workloads.

## Compute / quota note

No Codex execution used or authorized by this finding. `research/quota-governor-v0.md` remains controlling: Luna/Light default downstream; never infer missing quota percentages from token reductions reported in a paper.

## Source/repo check

A targeted public search on 2026-09-13 found the paper but no obvious official implementation repository tied to the authors/paper. Therefore treat VikingRAG as a research pattern, not a deployable dependency, until code is independently located and inspected.
