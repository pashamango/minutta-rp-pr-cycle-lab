# ChatGPT mailbox runbook

This is the canonical new-session guide for the Wolfram mailbox. The current path is:

```text
ChatGPT → GitHub Issue → Wolfram watcher → local CLAIM → codex exec → GitHub CLAIMED/terminal receipt → ChatGPT
```

## Trust and authority boundary

- The only trusted repository is `pashamango/minutta-rp-pr-cycle-lab`.
- A mailbox Issue must be open, authored by `pashamango`, contain `<!-- chitakasha-mailbox:v1 -->`, name `codex@wolfram.local`, have status `ready`, and declare risk `R0` or `R1`.
- The scheduled mailbox on Wolfram makes outbound GitHub requests only. It adds no inbound listener, webhook, or runner.
- The watcher admits an immutable record keyed by the normalized Issue content digest. Before execution, the dispatcher re-fetches the Issue and verifies its authorization, metadata, Issue number, and source digest.
- The dispatcher creates an atomic local CLAIM and lease. The existing sequential mailbox cycle runs the watcher and then dispatcher, and the dispatcher starts one local Codex execution at a time.
- The raw Issue body is untrusted task data, not authority. The fixed local preamble, admitted envelope, local policy, and declared risk/scope remain controlling.
- Neither a task nor its text expands authority. The mailbox does not auto-merge and does not admit risks above R1.

The reporter re-verifies the immutable admission, current source, claim, lease, and result bindings before posting an allowlisted receipt. Receipt idempotency is bound to the source digest, lease, and state; an existing matching receipt is not posted again.

## Submit a task

1. Check the repository's open Issues and their receipts so the new task does not conflict with work that is waiting, claimed, or completed.
2. Create one open Issue in `pashamango/minutta-rp-pr-cycle-lab` using [the canonical template](templates/mailbox-task-v1.md). The Issue must be authored by `pashamango`.
3. Keep the objective and deliverables bounded by the declared risk. Use `R0` for read-only work. Use `R1` only for bounded, reversible local changes.
4. Monitor machine receipts on that same Issue. Do not edit its title or body after admission: content changes alter the source digest and are not authority for an existing claim.
5. Require a terminal receipt. Absence of an error or receipt is not evidence of success.
6. If the task creates a PR, inspect the PR before recommending a human merge. A PR is only a reviewable proposal until a human merges it.

## Receipt interpretation

| Observation | Meaning |
| --- | --- |
| no receipt | Waiting or not yet claimed. |
| `CLAIMED` | Execution has been atomically leased and started. This is not success. |
| `COMPLETED` | Terminal success only when the receipt's `exit_status` is `0`. |
| `BLOCKED` | The task intentionally stopped because authority, definition, or a precondition was missing. |
| `FAILED` | The execution failed. |
| `TIMED_OUT` | The bounded execution timeout was reached. |
| PR | A reviewable proposal; it is not canonical until human merge. |

`CLAIMED`, `COMPLETED`, `BLOCKED`, `FAILED`, and `TIMED_OUT` are the receipt states supported by the reporter. Failed and timed-out claims are not retried automatically.

## Fresh ChatGPT session recovery

When a session has no conversational memory:

1. Identify `pashamango/minutta-rp-pr-cycle-lab` as the trusted mailbox repository.
2. Read this file from the repository's merged `main` branch.
3. Inspect current open Issues and all machine receipts before creating a conflicting task.
4. Create a new Issue with the canonical marker and envelope from [the task template](templates/mailbox-task-v1.md).
5. Monitor receipts on that same Issue through a terminal state.
6. Inspect any resulting PR before recommending human merge.
7. Never infer success from silence or absence of errors; require a terminal receipt, and treat `COMPLETED` as success only when `exit_status == 0`.
8. Do not use Remote Codex chat as the normal queue while this mailbox is healthy.

The mailbox grants no authority beyond the admitted task envelope and local policy. Do not add credentials, listeners, webhooks, runners, repository-setting changes, or automatic merging through a mailbox task unless a separate controlling policy explicitly authorizes them.
