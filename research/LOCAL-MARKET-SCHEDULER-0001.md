# LOCAL-MARKET-SCHEDULER-0001

Verdict: `WOLFRAM_READY_DARWIN_BOOTSTRAP_REQUIRED`

This branch contains a deterministic scheduler core with SQLite event journaling,
priority/host matching, one active job per host, durable immutable lease keys,
restart-safe enqueue semantics, idle events, and injected Forgejo runner
contracts. The test proves dual synthetic decisions, duplicate polling safety,
completion-driven refill, and durable dispatch events without model inference.

The Wolfram checkout cannot verify a Darwin runner daemon, its `darwin` label,
or a Forgejo dispatch/completion receipt. Therefore no dual-host claim is made.
Minimal continuation: on the existing Darwin account, install/configure the
approved Forgejo runner with label `darwin`, run the workflow fixture, and return
the sanitized runner/job IDs and artifact hashes. Do not broaden SSH or expose
credentials. A deliberate failure must be reported as `BLOCKER_ANALYSIS/v1`.

Rollback: remove the user-level scheduler service and revert this task branch;
no production service, listener, repository setting, or merge was changed here.
