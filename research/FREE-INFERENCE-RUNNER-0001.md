# FREE-INFERENCE-RUNNER-0001

Verdict: `RUNNER_READY`

This slice is a loopback/local-first SQLite-WAL runner. Jobs are `queued -> completed`; an external job remains `queued` when its capability is `auth_required`, so missing Google authorization does not block local work. Completed jobs return the stored result and receipt on restart or duplicate processing, preventing duplicate semantic execution.

Private or marker-sensitive input is local-only. Public synthetic input may use the narrow provider adapter. The adapter receives a request, not a reusable credential; the worker exposes only sanitized capability metadata. Paid mode is rejected and every job carries a free-only budget envelope.

The local adapter uses Ollama at `127.0.0.1:11434`, model `gemma4:latest`, with `stream:false` and `think:false`, the smallest proven configuration fix from predecessor findings. External activation is represented by `NoAuthExternal` and tested with `StubExternal`; no account, billing, network listener, or secret was changed. Exact live runtime/model latency is reported only when a live receipt is available; deterministic tests use `fake-local`/`stub-v1`.

Operations submits with `Runner(db).submit(job_id, prompt, privacy)` and retrieves with `process(job_id)`. Receipts include task id, route, observed provider/model, latency, retries, exposed usage counters, and result SHA-256. `capability_card()` implements `worker-capability-card/v1` with task/privacy classes, lane availability, bounded capacity, and no private host fields.

Checks: `python -m unittest discover -s tests -v` (4 tests). The restart/idempotency, private/public routing, no-auth queueing, budget guard, receipt hash, and sanitized capability-card cases pass. Smallest next step: separately authorize and implement one external adapter behind the existing capability boundary; no AUTH_REQUEST is made here.
