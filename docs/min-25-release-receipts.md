# MIN-25 release receipts and learning loop

Status: `CANDIDATE / NOT EXECUTION-AUTHORIZED`

This pilot defines evidence-bearing release decisions. It does not publish, merge,
or schedule anything. The machine-readable examples are in
[`min-25-release-receipts.jsonl`](min-25-release-receipts.jsonl), with one sample
each for `VERIFIED`, `BLOCKED`, and `NO-OP`.

## Decision contract

`VERIFIED` is permitted only when every applicable gate has exact evidence:

| Candidate | Required evidence |
|---|---|
| artifact | immutable artifact link, source/version, and independent scientific or factual review |
| code | repository, PR, merged commit SHA, and post-merge read-back of that SHA |
| paper | public URL and stable identifier (for example DOI or repository ID), read back after publication |
| Nostr | event ID, relay acceptance, and event read-back |

Missing, conflicting, or unverifiable evidence is `BLOCKED`; it is never inferred
from a successful local command, a draft URL, a PR number, or an author assertion.
`NO-OP` means the candidate was intentionally not acted on because the pilot is
not execution-authorized or the candidate is outside scope. No automatic release
is allowed during this pilot.

## Learning loop

After each independent review, append (do not rewrite) one claim unit to the
learning ledger. A claim unit records the candidate, the exact failed or passed
gate, the evidence reference, reviewer identity, confidence, and the next
falsifiable check. Feedback changes the next review checklist; it does not change
the historical receipt or retroactively upgrade a blocked claim.

Recommended sequence:

1. Bind candidate to source version and artifact digest.
2. Run independent scientific/factual review.
3. Verify the applicable publication or merge read-back.
4. Emit exactly one terminal receipt (`VERIFIED`, `BLOCKED`, or `NO-OP`).
5. Extract feedback into a new claim unit and queue human authorization if needed.

The sample receipts are fixtures, not evidence of a real release.
