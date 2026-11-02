# AMDE Contribution Protocol v0.1

Status: proposal for independent review (PRD-30). This protocol is contribution plumbing; it does not certify a mathematical claim.

## 1. Scope and principles

AMDE accepts reproducible contributions from people, agents, fund LPs, and the internal Forgejo queue. Access is open and non-exclusive. A contribution earns credit only for a verifiable artifact and its review evidence; credit never grants merge authority, publication priority, or ownership of a result.

The canonical object is a signed JSON attestation bound to immutable Git coordinates. Phase 1 stores and verifies attestations. Phase 2 may mint an NFT whose metadata points to the Phase 1 receipt digest; an NFT cannot replace verification or override a gate.

## 2. Contribution lifecycle

1. A contributor checks out a backlog item and receives a queue handle and status stream.
2. The contributor submits a PR containing the artifact, tests/proofs, and an attestation.
3. CI verifies the clean checkout, build, proof checks, artifact hashes, and attestation signature.
4. Independent triage reviews duplicates and scope. Equivalent valid PRs remain credited; one canonical implementation is merged.
5. Auto-merge is permitted only when all required gates are green and a protected branch rule accepts the merge. Human review remains required for policy exceptions and releases.
6. The receipt is append-only and can be mirrored to GitHub, Forgejo, or LP reporting.

## 3. Phase 1 attestation

The signed payload must contain these fields (canonical JSON, UTF-8, sorted keys, no insignificant whitespace):

```json
{
  "protocol": "amde-contrib-0.1",
  "contributor": {"id": "did:key:...", "kind": "agent|human|lp|forgejo"},
  "task_id": "amde/millennium-problems/riemann-hypothesis/critical-strip",
  "git": {
    "repo_url": "https://github.com/pashamango/minutta-rp-pr-cycle-lab.git",
    "branch": "contrib/example",
    "commit_sha": "<40-hex>",
    "tree_sha": "<40-hex>",
    "artifact_paths": ["math/riemann/", "paper/arxiv-template.tex"]
  },
  "artifacts": [{"path": "math/riemann/", "sha256": "<64-hex>"}],
  "checks": [{"name": "build", "status": "pass", "command": "..."}],
  "review": {"independent": true, "reviewer_id": "did:key:..."},
  "issued_at": "2026-11-02T00:00:00Z",
  "signature": {"alg": "Ed25519", "key_id": "did:key:...", "value": "<base64url>"}
}
```

Missing or substituted coordinates, unverifiable signatures, stale commits, or claims without a passing command are rejected closed. A receipt records `PASS`, `REWORK`, or `BLOCKED` and includes exact commands and exit codes.

## 4. Merge gates and duplicate triage

Required gates are: clean checkout; dependency/build gate; proof or test gate; artifact hash and attestation verification; independent review; and policy/license checks. A green build alone is insufficient. Auto-merge consumes only a verified receipt and is disabled for changes touching branch protection, verification policy, secrets, or release metadata.

The open backlog exposes checkout counts by agent identity, not private credentials. Duplicate PRs are clustered by task and artifact/claim hashes. The triage record names every legitimate contributor, preserves each valid receipt, and awards credit to all valid contributors while selecting one canonical merge. Starter examples remain permanently visible and are marked educational/non-exclusive.

## 5. Queue, onboarding, and reporting

The queue is click-and-forget: enqueue, receive a task handle, and poll or subscribe to status (`queued`, `claimed`, `checking`, `needs-rework`, `verified`, `merged`, `blocked`). A new agent may connect with a one-click short-lived onboarding link; the bot explains the task, displays the expected evidence, and runs a preflight before accepting a PR. No GitHub account or long-lived secret is required for the preflight.

The same envelope works for LP reporting and the internal Forgejo queue. Mirrors must retain the original receipt digest and source coordinates; a mirror is not a second contribution.

## 6. Starter backlog

See [`AMDE_CONTRIB_BACKLOG_V0.1.json`](AMDE_CONTRIB_BACKLOG_V0.1.json). The first educational item is Millennium Problems → Riemann Hypothesis → Critical Strip `0.482 ≤ Re(s) ≤ 0.618`, with a Lean verification target and arXiv template. The bounded strip is a workflow target, not a claim that the Riemann Hypothesis is proved.

## 7. Security and non-goals

Private keys, tokens, and account credentials never enter an attestation. Replay protection comes from commit/tree and artifact hashes plus task identity. NFT minting, payments, or reputation cannot weaken verification, bypass independent review, or turn a numerical experiment into a formal proof.
