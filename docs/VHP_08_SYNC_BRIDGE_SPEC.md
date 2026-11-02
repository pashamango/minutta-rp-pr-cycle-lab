# VHP-08 — Gemini–Drive–Linear–GitHub Sync Bridge

**Status:** draft implementation specification  
**Ticket:** MIN-66  
**Artifact:** `vhp-manifest.json`  

## Purpose

VHP-08 defines a portable, one-click submission envelope for a venture package. Gemini may prepare the envelope, Drive may transport or archive it, Linear remains the workflow source of truth, and GitHub remains the immutable source for code and review evidence. The bridge synchronizes references and state; it does not copy secrets or silently mutate a repository.

The normative JSON Schema is `schemas/vhp-manifest.schema.json`. A complete example is `examples/vhp-manifest.json`.

## Design rules

1. **References, not credentials.** A manifest contains URLs, IDs, commit SHAs, paths, and hashes. OAuth tokens, cookies, private keys, and refresh tokens are prohibited.
2. **Git is the handoff boundary.** A submission is actionable only when `sources.github.commitSha` resolves on `sources.github.repoUrl` and every artifact has a path and SHA-256.
3. **Linear is authoritative for workflow.** Drive status is archival/transport state; GitHub status is review/build state. Neither may overwrite a Linear decision.
4. **Idempotent replay.** `submissionId` is the deduplication key. A bridge must safely replay the same manifest and must reject a conflicting manifest with the same ID.
5. **Fail closed.** Missing coordinates, unsupported schema versions, hash mismatches, expired manifests, and ambiguous state transitions stop submission and produce a diagnostic; they do not create a partial release.
6. **Human gate preserved.** A successful preflight can prepare a submission and request review, but cannot mark the Linear issue Done or merge protected branches.

## Source contract

| Source | Required coordinates | Authority |
| --- | --- | --- |
| Drive | `fileId`, `webUrl` | package transport and archive location |
| Linear | `issueId`, `issueUrl` | ticket, assignee, workflow state, acceptance |
| GitHub | `repoUrl`, `branch`, `commitSha` | code, diff, and reproducible checkout |

`artifactPaths` are repository-relative POSIX paths. `artifactSha256` hashes the exact bytes at the referenced commit. The optional Drive file hash is a transport-integrity check and is not a substitute for Git coordinates.

## One-click lifecycle

```text
draft -> preflighted -> submitted -> in_review -> accepted
                         \-> blocked
```

The bridge performs these steps atomically from the manifest’s point of view:

1. Parse and validate the schema, version, timestamps, and allowed URL schemes.
2. Verify that the Git commit is present and that listed artifacts are inside the commit tree.
3. Verify artifact hashes and the manifest hash, if supplied by the transport.
4. Resolve the Linear issue and compare its repository/branch coordinates with GitHub.
5. Create or update one idempotent submission record keyed by `submissionId`.
6. Attach a sanitized receipt to the Linear issue and request the configured review transition.

The bridge must not auto-merge, close the issue, upload arbitrary files, or follow URLs outside the declared source allowlist. A retry after step 5 must return the existing receipt rather than create a second submission.

## Receipt and failure semantics

A receipt should include `submissionId`, result (`accepted` or `blocked`), checked commit, checked artifact hashes, verifier version, and UTC timestamp. Diagnostics must identify the failing field and a remediation, while redacting credentials and access tokens. `blocked` is a valid result and is not evidence of a successful submission.

## Verification

Run the dependency-free validator and tests from a clean checkout:

```bash
python3 tools/validate-vhp-manifest.py examples/vhp-manifest.json
python3 -m unittest tests/test_vhp_manifest.py
```

This implementation validates the portable envelope and its safety invariants locally. It does not claim live access to Drive, Linear, or GitHub; live resolution remains an integration concern for the bridge runtime.
