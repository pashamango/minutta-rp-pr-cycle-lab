# Research Scout — Stateless sealed A2A↔MCP task handles

Date: 2026-09-12
Priority: P3 research note (no execution authorization)

## Finding

`aarushitandon0/a2a-mcp-bridge` implements an A2A 1.0 ↔ MCP `2026-07-28` bridge whose bridge process keeps no task database. Instead, each MCP `taskId` is a sealed AES-256-GCM / CBOR envelope containing the remote A2A agent id, task id, context id, and expiry. Any bridge instance holding the seal key can resume the task after process loss. The implementation also fail-closes on unknown protocol states, keeps `AUTH_REQUIRED` structurally distinct from ordinary model-fillable input, and reports validation against the real MCP conformance suite.

Primary source: https://github.com/aarushitandon0/a2a-mcp-bridge

## Decision relevance

This is a useful design pattern for the mailbox/self-heal architecture: crash-resumable task routing does not necessarily require bridge-side replicated task state. A sealed, self-describing continuation handle can move routing state to the message boundary while the authoritative task state remains on the worker.

Potential invariant:

`continuation_handle = AEAD(agent_id, remote_task_id, context_id, expiry, protocol_version)`

The handle is *routing evidence*, not execution authority. Existing lease/mandate/mutation guards must remain authoritative.

## Why this is not a new candidate Issue

The repository already has Issue #96, `P2 CANDIDATE — evaluate a2acode as A2A/ACP bridge for Codex workers`. Creating another bridge-evaluation candidate would duplicate the same decision surface. This note should instead inform #96 or any later mailbox protocol design review.

## Smallest future falsification if #96 is admitted

Compare current mailbox recovery requirements against a sealed-handle prototype on four cases only: process crash, retry/replay, key rotation, and expired/revoked authority. Reject the pattern if an old cryptographically valid handle can cause a new effect after its execution lease has been revoked.

## Risk / caveat

The bridge is a small third-party repository, not an official MCP/A2A reference implementation. The most important unresolved security question for ChitAkasha is revocation: a stateless cryptographic handle can prove what was minted, but not by itself whether execution authority is still live now. Therefore sealed handles should never replace the authority oracle.

## Quota impact

Web/Git research only. No Codex admission, no model step-up, no quota estimate. Luna/Light default remains unchanged per `research/quota-governor-v0.md`.
