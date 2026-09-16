# Research Scout — Stateless A2A↔MCP bridge pattern

Date: 2026-09-16
Status: FINDING / NO EXECUTION AUTHORIZED
Priority: P2 observation

## Evidence

Fresh public repository `aarushitandon0/a2a-mcp-bridge` targets A2A 1.0 and MCP 2026-07-28. It projects A2A Agent Card skills as namespaced MCP tools and deliberately keeps the bridge stateless: resumable task information is carried in sealed opaque `taskId` handles held by the MCP client, while authoritative task state remains at the A2A agent.

Source: https://github.com/aarushitandon0/a2a-mcp-bridge

## Decision-relevant update

This is a concrete protocol pattern for reducing duplicated orchestration state: bridge/router instances can be disposable and horizontally replaceable if continuation authority is encoded in sealed handles and the remote agent remains the source of truth.

For NICLI/mailbox/router work, this suggests testing whether some mailbox coordination state can move from persistent intermediary state toward capability-like sealed continuation handles, without weakening authority checks or idempotency.

## Opportunity Card

- Proposed capability: stateless protocol adapter / continuation-handle pattern for A2A↔MCP and potentially mailbox routing.
- Expected value: infrastructure leverage; fewer split-brain/recovery states; easier replacement/scaling of routing processes; interoperability with current A2A/MCP standards.
- Time-to-first-useful-result: day for a paper/design comparison; week for a bounded prototype if later authorized.
- Complexity/risk: medium. Main uncertainty is whether sealed client-held task handles compose safely with our authority leases, replay/idempotency semantics, and audit requirements.
- Smallest falsification: compare the bridge's handle format/threat model against mailbox invariants and identify one state currently held by an intermediary that can or cannot safely become a sealed continuation token. No execution required.
- Compute cost: web/Git reading only for falsification; local/Codex execution explicitly not authorized here.
- Why now: A2A 1.0 + MCP 2026-07-28 are converging operationally, and a working bridge now demonstrates the stateless pattern rather than merely proposing it.

## Scout verdict

Worth preserving as a P2 architectural option, but do not create executable work yet. The key research question is not whether the bridge runs; it is whether `sealed continuation handle + remote source of truth` can simplify mailbox recovery while preserving explicit authority and duplicate-delivery safety.

Quota discipline: no Work/Codex/NICLI/local execution allocated; no quota counters inferred.
