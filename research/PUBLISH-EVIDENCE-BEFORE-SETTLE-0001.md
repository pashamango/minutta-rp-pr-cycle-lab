# PUBLISH-EVIDENCE-BEFORE-SETTLE-0001

Verdict: `PRIMITIVE_READY`

The repository now has a small `EvidencePublisher` state boundary:

`execution records -> canonical manifest + Git blob -> independent reporter decision`

The manifest is keyed by the exact `(task_id, source_digest, lease_id)` triplet. It is written before `settle()` is callable, and its canonical SHA-256 is the stable publication identity. Repeating the call or resuming after a crash reads the same journal and does not repeat semantic execution. A failed write produces an explicit retryable journal state.

The reporter can return `completed` or `blocked`, but publication never supplies that decision. The regression fixture models #130 (`exit_status=0`, three artifacts, seven checks, `TASK_BLOCKED`): all three artifact references remain in the durable manifest. A comment-shaped reference is retained as data only; it is not continuation authority.

Prometheus continuation example: after `TASK_BLOCKED`, load `evidence/published/<task_id>/<lease_id>/publication.json`, inspect its three `artifact_refs`, and enqueue a continuation keyed by the same triplet. The underlying scheduler execution is not rerun.

Wise Broker pass: `EVIDENCE_PUBLISHED` is a safe scheduler handoff event. The smallest rule is: release/reconcile host capacity only after a valid publication journal exists; process exit alone does not release semantic work. This is bookkeeping, not completion, and can be integrated at the scheduler's existing `complete()` boundary after publication.

Smallest safe integration point for #126/#127: call `EvidencePublisher.publish()` immediately after execution records are closed and before invoking the installed reporter; feed only the reporter's independent status to `Scheduler.complete()`. Do not infer completion from exit status, artifact count, or publication itself.
