# VHP-08 — Gemini–Drive–Linear–GitHub Sync Bridge

**Status:** v1.0 design specification  
**Ticket:** MIN-66  
**Artifact:** `vhp-manifest.json`

## Purpose

VHP-08 defines a provider-neutral handoff between Gemini (the coordinating
agent), Google Drive (human-readable source artifacts), Linear (work state),
and GitHub (versioned code and immutable review coordinates). The bridge is a
reconciliation protocol, not a second source of truth and not an unattended
merge service.

The Git commit is authoritative for code. Linear is authoritative for task
state and approval. Drive is an artifact mirror. GitHub is the review and
transport surface. A manifest binds the four observations by IDs, URLs,
digests, and an explicit approval policy.

## Lifecycle

1. **Prepare:** Gemini collects the Linear issue, Drive files, and GitHub ref
   without changing any provider.
2. **Bind:** it emits a manifest containing the exact commit, tree, artifact
   paths, and SHA-256 values. Missing or conflicting observations fail closed.
3. **Validate:** an independent checker validates the schema, digests, and
   cross-provider coordinates from a clean checkout.
4. **Submit:** a human-approved one-click action may open/update the GitHub
   submission and attach the manifest to the Linear issue. The action is
   idempotent on `submission.idempotency_key`.
5. **Reconcile:** later runs append a new manifest revision; they never rewrite
   an earlier receipt. GitHub merge and Linear `Done` remain human actions.

## Safety and authority boundaries

- Tokens, refresh tokens, cookies, and private Drive URLs must never appear in
  the manifest. Providers receive credentials through their normal secret
  stores.
- The manifest grants no authority. `approval.required` is always `true` for
  submission, and `merge` is always `false`.
- A stale manifest, changed commit, missing artifact, digest mismatch, or
  provider disagreement produces `blocked` and requires a new manifest.
- Drive synchronization is copy/verify only; it does not delete or overwrite
  the source artifact.
- Retries use the idempotency key and may not create a second submission.

## Required coordinates

`source.linear.issue_id`, `source.github.repo`, `source.github.commit_sha`,
`artifacts[].path`, and each artifact's `sha256` are mandatory. A checker must
run the `verification.command` in a fresh clone at the pinned commit.

The JSON Schema and a redacted example are shipped beside this document:
`docs/vhp-manifest.schema.json` and `docs/examples/vhp-manifest.json`.

## State model

`prepared -> validated -> awaiting_approval -> submitted -> reconciled`.
Any validation or provider conflict transitions to `blocked`; a blocked
manifest is not retried automatically. `submitted` means only that the
provider accepted the request, not that a human merged or released it.
