# RUNNER-FREE-INFERENCE-0003
Verdict: `AUTH_REQUIRED`

The runner is a SQLite-WAL, restart-safe bounded queue with idempotent job IDs. It classifies public/private input, fails closed on ambiguous privacy, routes private jobs only to loopback Ollama and public jobs only to a Gemini free-only capability boundary. Provider credentials stay behind the broker; the example contains only a Keychain handle name. `status()` exposes sanitized lane availability, capability metadata, and job counts.

Tests cover useful local output, duplicate/restart replay, deterministic external `AUTH_REQUIRED`, privacy rejection, and billing guard. Live Ollama advertised installed models at `127.0.0.1:11434`; no live Gemma latency/usage is claimed without a bounded inference receipt. No account, billing, listener, scheduler, PentAGI, or paid route was changed.

One minimal AUTH_REQUEST is genuinely required: under Pasha's authenticated Google AI Studio session, select/create one dedicated Free Tier project with billing unlinked, create a current Auth API key, place it directly into the local broker/Keychain path (never Git/chat), revoke it from the project API-key page, then run one public synthetic validation call. No secret is requested here.

The Wise Broker pass is satisfied by the provider-neutral `Capability` contract: provider, privacy_class, free_only, model_class, budget_remaining, availability. Rollback is stopping the runner and reverting this commit; no host service was installed.
