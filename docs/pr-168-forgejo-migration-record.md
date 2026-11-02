# PR #168 Forgejo migration record

**Ticket:** MIN-93  
**Source:** GitHub PR #168 mining pass  
**Destination:** private Forgejo project `codex-wolfram/pr168-triage`  
**Classification:** internal draft backlog

## Prepared payload

The sealed local pass produced **59 named Forgejo draft payloads** from the
available PR #168 issue-comment export. The export contains 965 rows; the
derived ledger contains 965 rows. Receipts and heartbeat comments were
excluded from issue drafts.

| Artifact | SHA-256 | Meaning |
|---|---|---|
| `pr168-comments.jsonl` | `5ec3bc5c15fda1ea8aab7b7f0628268e0f14cd2e37573a0d73371be86bbfe990` | source issue-comment export |
| `pr168-pass2-4-ledger.jsonl` | `d7866ae4eb8656ff2cc6d7b69ab256528b947e95f225ad6657ba7c563c093976` | classified ledger |
| `pr168-forgejo-drafts.jsonl` | `448bf5e66ecc5d9e8c5cab0e1da10b3a14fbed6374f99a5e7f476663b6b55fba` | Forgejo issue payloads |

These hashes identify the prepared handoff; they do not assert that issues
were created remotely.

## Publication gate

**Status: BLOCKED — Forgejo publication not proven.** The earlier pass reached
the Darwin Forgejo endpoint but had no valid signed-in session or scoped
issue-write credential. No GitHub issues were created, and no publication
claim is made here.

Next valid command for the Darwin admin lane: authenticate to the private
Forgejo instance, verify the destination repository, then create the 59 issue
drafts from the hashed JSONL payload and record the resulting Forgejo issue
IDs. Recompute the source hashes before publishing. Do not retry credentials
blindly or store them in this repository.

## Release boundary

Only a separately approved public release remains on GitHub. PR #168-derived
working drafts are not release artifacts and must not be opened as GitHub
issues.
