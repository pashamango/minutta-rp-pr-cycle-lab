# Research Scout — Elements range-proof cache key boundary failure

`RESEARCH_SCOUT_ITERATION/v1`

- local_timestamp: 2026-09-12 04:20 America/Los_Angeles
- topic: security-critical cache-key construction; implications for semantic/KV/proof caches
- source/evidence:
  - ElementsProject/elements release `elements-23.3.4` (2026-09-09): https://github.com/ElementsProject/elements/releases/tag/elements-23.3.4
  - ElementsProject/elements PR #1600, merged 2026-09-08: https://github.com/ElementsProject/elements/pull/1600
  - PR #1600 explicitly replaces raw `CSHA256` concatenation in range-proof/surjection-proof cache hashers with `CHashWriter`, which length-prefixes every field so distinct argument tuples with byte-identical raw concatenations cannot share the same cache key. It also preserves per-process salted midstates, distinct domain separators (`r` / `s`), adds `-norangeproofcache`, and tests field-boundary collisions, script sensitivity, domain separation, determinism, and `vTags` sensitivity.
- finding: **A cache may be cryptographically hashed and still be unsound if the structured preimage is ambiguously serialized.** The failure class is not a SHA collision; it is a tuple-boundary collision before hashing. For any security- or authority-relevant cache in ChitAkasha/NICLI/PentAGI/semantic routing, a cache hit must bind the complete decision-relevant input tuple using canonical unambiguous encoding plus domain separation. A runtime kill-switch/bypass is also a valuable incident-control primitive.
- confidence: high for the engineering lesson; primary fix and release are public. This note does not assert an independent full root-cause reconstruction of the wider Liquid incident beyond what PR #1600 and the release establish.
- relevance:
  - semantic caches: never key only on concatenated embeddings/claim fragments when issuer, policy version, principal, model, namespace, or authorization state changes semantics;
  - KV/reuse caches: principal/session/authority identity must be in the canonical key or enforced before lookup; semantic similarity cannot substitute for exact authorization binding;
  - proof caches: proof/verifier parameters, script/predicate, tags/domain, and policy version must be explicitly framed; cached validity must not be reused across structurally distinct tuples;
  - mailbox/idempotency: task/source/lease/action binding should use canonical framed serialization rather than informal string concatenation;
  - incident handling: a reversible `disable-cache` path is worth preserving for critical caches even if normal operation expects the cache always on.
- outcome: SURVIVED
- candidate_handoff: none. This is a cross-cutting negative-feasibility/security constraint, not a request for new execution. When existing cache/router/KV candidates are implemented, require canonical framed keys, explicit domain separation, adversarial field-boundary collision tests, and a bypass/kill-switch before production use.

## Decision impact

Do **not** treat `hash(all relevant fields)` as sufficient unless `all relevant fields` are serialized canonically and unambiguously. For structured cache keys prefer a typed/framed representation (for example length-prefixed fields or canonical CBOR/JSON with a fixed schema), include semantic/security domain/version identifiers, and test adversarial pairs where different tuples have identical raw concatenation.

Quota discipline: web/Git research only; no Codex lane allocated, no model step-up, no missing quota counters estimated.