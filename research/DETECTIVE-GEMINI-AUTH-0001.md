# DETECTIVE-GEMINI-AUTH-0001

Date: 2026-09-12  
Task lease: `94e9c2d55f0b4c18aa070d1263dbcedd`  
Source issue: `145`  
Source digest: `55774ea50e2857b8abf30adf1873ec696700601fcc9acb63fc4cd213ebab0423`

## Historical search and provenance

The task-local search covered mailbox run state, the prior Gemini-auth worktree, and project-local Gemini references. The only directly bound auth execution found was `RUNNER-GEMINI-AUTH-0001`, whose sanitized outcome records `AUTH_REQUIRED`, no credential, and no live provider call. Its report identifies predecessor PR #123 and commit `84a66b2d35d780b6dcf0eee5f8bc944a45619728` as the pre-auth state. No post-#123 success receipt, branch, or run artifact was found.

The exact approved Keychain lookup (`service=GEMINI_API_KEY`, `account=codex@wolfram.local`) returned item-not-found (security exit 44). The lookup did not request or print the secret value.

## Current capability state

`provider=google-gemini`; `model=gemini-2.5-flash-lite`; `credential_source=keychain`; `free_only=true`; `billing_guard=paid-operation-rejected-without-separate-authorization`; `credential_present=false`; `live_call=not-run`.

The first missing transition is: an authorized human must install the existing intended Gemini credential in the approved Keychain item. No replacement credential was created, no billing was enabled, and no provider request was sent.

## Durability and privacy

Because the approved item is absent, restart availability cannot be demonstrated as a positive capability. The negative result was repeated as a fresh `security` process lookup with the same service/account and remained absent. The predecessor adapter’s recorded isolation contract remains applicable: the reusable credential is process-memory-only, never placed in prompts, SQLite, receipts, stdout/stderr, fixtures, or Git; local/private routing is independent.

## Provider-neutral Wisdom Broker receipt

The smallest shared object is a sanitized capability receipt, with provider-specific secret mechanics excluded:

```json
{
  "schema": "provider-capability-receipt/v1",
  "capability": "external-free-inference",
  "provider": "google-gemini",
  "model": "gemini-2.5-flash-lite",
  "status": "auth_missing",
  "credential_source_class": "keychain",
  "free_only": true,
  "billing_guard": "enforced",
  "usage": null
}
```

NICLI and PentAGI can consume `status`, capability, model, free-only, billing-guard, and optional usage fields without knowing Keychain or provider internals. This representation was tested cheaply as a JSON/schema-by-inspection artifact; no semantic provider call was made.

## Candidate gate movements

- `NICLI-v0 / GEMINI_DURABLE_ACCESS`: `AUTH_MISSING` — not a PASS candidate.
- `PENTAGI / P4_EXTERNAL_FREE_PROVIDER_CAPABILITY`: `AUTH_MISSING` for auth/capability only; this does not settle routing, integration, or quality gates.

Smallest next action: an authorized human installs the intended free-only Gemini credential in the approved Keychain item, then admits a fresh bounded run for one synthetic public probe and restart verification. Do not paste the key into task data or create a replacement.

## Final verdict

`AUTH_MISSING`
