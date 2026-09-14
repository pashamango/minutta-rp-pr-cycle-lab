# Research Scout — AAuth Protocol comparison

Date: 2026-09-13 PT
Status: RECORDED / NO NEW EXECUTION CANDIDATE

## Decision-relevant update

The AAuth Protocol editor draft dated 2026-09-08 defines agent-to-resource authorization using key-bound agent identity, HTTP Message Signatures, resource requirements, person/organization authorization, optional person-server governance, and federated authorization. It explicitly distinguishes itself from A2A task transport, MCP tool/context exchange, and portable authorization envelopes.

Primary evidence:
- https://dickhardt.github.io/AAuth/draft-hardt-oauth-aauth-protocol.html
- Submitted lineage tracked as `draft-hardt-oauth-aauth-protocol-10`; the 2026-09-08 editor copy is newer and still an individual Internet-Draft, not an adopted IETF standard/RFC.

## Why it matters

AAuth sharpens a boundary already emerging in ChitAkasha infrastructure:

`agent identity/key possession -> resource-specific authorization -> signed request -> effect`

This is complementary to, not a replacement for:
- A2A/ACP interoperability;
- portable authorization/mandate envelopes;
- mailbox task/source/lease binding;
- the local Sovereign Capability Session / Proof-of-Presence architecture.

The useful design distinction is that an agent's authenticated identity is insufficient by itself: resource access is separately authorized and key-bound, reducing bearer-token style delegation ambiguity.

## Comparison to current project state

Existing project memory/work already covers the decision this evidence would otherwise motivate:
- Issue #223: `Sovereign Capability Session / Proof of Presence` separates durable machine trust, temporary principal mandate, and derived task capability.
- Issue #229: `CAPABILITY-SESSION-AUTHORITY-GATE-0001` explicitly separates passive observation from authenticated authority and binds derived capabilities to exact task/source/lease/class/epoch.
- Issue #100: `Sovereign SSI / Agent Conscience lifecycle protocol` distinguishes CAN/MAY/WILL and lifecycle authority from mere key identity.

AAuth therefore does **not** justify a new candidate Issue now. Creating one would duplicate active architecture rather than increase option value.

## Negative/constraint finding

Do not treat AAuth as a mature standards commitment yet. It is an active individual Internet-Draft with `Workgroup: TBD` / no RFC status. Adoption should wait for either:
1. a concrete interoperability need with an external resource provider implementing it; or
2. evidence that its key-bound request semantics close a gap not already covered by the existing capability-session work.

## Cheapest future falsification

When/if #229 produces a stable synthetic authority model, map one synthetic resource request onto AAuth's key-bound signed-request semantics and test whether AAuth adds any invariant that the local model lacks. If none, keep it as an interoperability adapter only.

## Quota discipline

No Codex execution allocated. Public web/Git research only. Luna/Light default remains unchanged; no quota counters were estimated.
