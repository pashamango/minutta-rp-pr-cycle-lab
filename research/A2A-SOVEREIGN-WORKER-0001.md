# A2A-SOVEREIGN-WORKER-0001

## Result

`REDESIGN`. The narrow work boundary is technically useful, but this probe is an in-process reference path, not a production A2A/ACP implementation. It demonstrates safe lifecycle semantics only because the worker exposes an explicit allow-list. Integration should therefore add SSI/mandate/action binding before treating an external worker as sovereign.

## Reproduction

Run `python3 research/A2A-SOVEREIGN-WORKER-0001/probe.py` and `python3 -m unittest -v tests/test_a2a_sovereign_worker.py`. The probe and tests use only Python standard-library objects; no listener, network, credentials, paid inference, shell, browser, or account access is used. Observed runtime: Python 3.12.0; pytest was not installed, so no pytest result is claimed.

Topology: a coordinator creates a JSON-like envelope; a worker owns a private sentinel and accepts only `public.echo` plus cancellation. The coordinator receives card, progress, artifact, state, denial reason, and evidence hash—never the fixture.

Assignment completed with deterministic artifact `{"echo":"public fixture"}`. The evidence binds `task_id` and artifact using SHA-256. Duplicate delivery replays the identical response and does not repeat the semantic side effect. Cancellation leaves the task unambiguously cancelled on a later delivery. `shell.exec` and an added `filesystem` request both fail closed.

The private-state test confirms the sentinel is absent from the complete protocol transcript. The worker capability surface is exactly `dispatch(public.echo)` and `cancel(task_id)`; no generic filesystem, shell, browser, chat-history, credential, or workspace primitive exists.

## Authority and interoperability

The experiment proves transport/interface properties: structured assignment, progress/result/evidence, bounded capability, replay, and cancellation. It does not prove sender identity, mandate validity, subject consent, action binding, delegation depth, revocation, or settlement. Those SSI/LP semantics remain unsolved; A2A authentication alone must not be treated as authorization.

## Wise Broker capability-card pass

The card exposes only task classes (`public.echo`), privacy class (`private-host-never-delegated`), runtime class (`local-deterministic`), and bounded availability/budget. It contains no provider credential, private history, filename, or unrelated host state. This minimal representation is suitable for Market Maker pre-filtering. Keep it separate from identity and mandate material.

## Smallest next experiment

Run the same contract across two disposable loopback processes using an authenticated, replay-resistant envelope and explicit cancel/restart journal, then test SSI mandate/action binding independently. Do not add real LP identity or provider-account integration until those negative tests pass.
