# AGENCY_MAILBOX_V1 — implementation-ready migration specification

Status: proposal only. No transport activation, Darwin change, Forgejo mutation, or migration was performed by this task.

## Verified existing capabilities

From the merged mailbox runbook and local implementation: GitHub is the current trusted ingress; outbound-only polling uses `gh`; admission is marker/author/state/agent/risk gated; normalized Issue content is SHA-256 digested; the dispatcher re-fetches and verifies the source; exclusive local CLAIM files and leases precede execution; task outcomes are structured and receipt publication is allowlisted/idempotent; raw task text is untrusted; risks above R1, auto-merge, inbound listeners, and automatic retry are prohibited. The installed target policy also forbids direct main pushes and self-merge.

No current local evidence proves an operational Forgejo `agency.git`, its repository path, signing keys, DID registry, or Darwin service configuration. Those are `MISSING`, not inferred.

## Proposed sovereign model

`agency.git` is the canonical append-only Git repository for signed task envelopes, admission decisions, CLAIM/lease events, execution receipts, QA receipts, and human acceptance records. Forgejo Issues/Discussions and GitHub are interface/transport mirrors only; neither is authoritative. Darwin has no internet-facing listener: consumers pull or receive an explicitly authorized private transport over the existing private path.

### Envelope and provenance

Each immutable task envelope contains `protocol`, `task_id`, `source_digest`, `source_refs`, `objective`, `scope`, `risk`, `executor_did`, `required_host`, `authorization_ref`, `created_at`, `expires_at`, and `artifact_digests`. The canonical bytes are serialized deterministically and signed by an authorized principal. Agent identity is DID-compatible; the DID document/key binding and authorization policy are versioned in the repository. Missing signatures, unknown keys, expired envelopes, source-digest mismatch, or scope/host mismatch fail closed.

Receipts bind `task_id`, envelope digest, lease ID, executor DID, source/artifact digests, timestamps, terminal state, checks, and signature. Stdout is never an outcome. Provenance is a chain: interface event -> canonical envelope -> admission -> claim -> execution -> outcome -> independent QA -> human acceptance.

### Atomic claim and lease

A consumer obtains a single canonical claim by an atomic Git transaction (or Forgejo-backed protected ref with an equivalent compare-and-swap protocol). The claim records `task_id`, envelope digest, consumer DID, lease ID, start, expiry, and nonce. Only one live lease is valid. Renewal is bounded and signed. Expiry creates `LEASE_EXPIRED`, not an automatic retry; a human or policy controller must issue a new task ID or explicit recovery envelope. A receipt with a different digest or lease is rejected.

### QA and acceptance

The executor cannot mark its own work QA-passed. Independent QA verifies the frozen commit, tests, receipts, source bindings, and security boundaries. Human acceptance is a separate signed event. No auto-merge: protected `main` requires human approval, and the mailbox may only create a reviewable branch/PR.

## Migration phases and duplicate prevention

1. Inventory and freeze: export GitHub Issues, comments, inbox, claims, runs, and receipts; hash each export; declare GitHub authoritative during the freeze.
2. Shadow-write: generate canonical envelopes/receipts for new tasks without activating agency execution; compare digests and authorization decisions.
3. Dual-read, single-execute: one designated executor lane owns each task ID; GitHub remains interface, agency records are checked but do not execute duplicates.
4. Cutover: human approval selects agency.git as authority, freezes new GitHub admission, and records the cutover commit and time watermark.
5. Observe and rollback-window: verify signed claims, leases, QA, and human acceptance; retain the old mailbox read-only.
6. Decommission only after the rollback window and explicit human acceptance; never delete historical evidence.

Duplicate prevention uses globally unique task IDs, envelope digest equality, a migration mapping table (`legacy_repo/issue -> agency task`), a single active executor lane, atomic claim compare-and-swap, and a cutover watermark. A task seen on both transports is the same task only if the signed mapping and digest match; otherwise it is quarantined for human review. No transport may independently retry a failed/expired claim.

## Migration test matrix

| Test | Expected result |
|---|---|
| Valid signed envelope | Admit; canonical digest reproducible |
| Unknown/revoked DID key | Reject before claim |
| Wrong host/agent/risk | Reject before claim |
| Body or source changed | Digest mismatch; no claim |
| Concurrent two-consumer claim | Exactly one live claim; loser records conflict |
| Lease expiry | Explicit expired state; no automatic execution |
| Duplicate GitHub/Forgejo delivery | One mapping and one claim |
| Receipt wrong lease/digest | Reject; no publication |
| QA by executor identity | Reject as non-independent |
| Human acceptance absent | Remains reviewable; never auto-merge |
| Darwin listener scan | No internet-facing listener |
| Cutover replay | Old transport cannot create a post-watermark claim |
| Rollback | Old mailbox resumes read-only without deleting receipts |

## Rollback procedure

Stop new agency admission and execution, preserve the agency HEAD and all signed exports, record a signed rollback event, and restore the pre-cutover GitHub mailbox as the sole ingress using its reviewed LaunchAgent. Keep agency consumers disabled; do not delete or rewrite agency records. Reconcile the mapping table and quarantine any post-cutover duplicates. Resume only after human approval, with a new cutover watermark if migration restarts. Darwin remains unchanged and listener-free throughout.

## Open implementation work

Verify the actual Forgejo host/repository, protected branches, signing/DID storage, private transport, backup/restore, and operator authorization in a separate approved task. Then implement schemas, canonicalization, signed ref layout, claim CAS, lease verifier, mirror adapters, independent QA verifier, and migration tooling with deterministic fixtures. None of those changes are activated by this PR.
