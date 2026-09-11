# RUNNER-GEMINI-AUTH-0001

- Exact base SHA: `b6a275d5ca3455b2d7de6dc3d23c50fa171c4235`.
- Provider adapter: added `GeminiExternal` to the existing runner boundary. It accepts public prompts only, uses `gemini-2.5-flash-lite`, sends `maxOutputTokens: 512`, and reports only provider/model/latency/exposed usage counters.
- Auth/capability state: `AUTH_REQUIRED`. No `GEMINI_API_KEY` process credential and no exact `GEMINI_API_KEY` Keychain service entry were observed. No live provider call was made.
- Free-only/billing guard: adapter capability is `free_only: true`; the runner rejects `paid=True` with `billing_enabled_requires_separate_authorization`. No billing or account state was changed.
- Live test: not run because the approved credential boundary is absent. Local/private lane remains usable; public jobs remain queued rather than failing or silently using a paid lane.
- Privacy/credential isolation: the key is read only into process memory, never inserted into the SQLite schema, prompt, result, receipt, capability card, Git diff, stdout, stderr, or fixture. Tests verify fail-closed auth and sanitized behavior.
- Actual provider/model/latency/usage: unavailable because no live call was authorized.
- Final verdict: `AUTH_REQUIRED`
- Integration note for #121: continue the Friday draft through the local Gemma lane; after human auth is installed in the local secret store, rerun the bounded synthetic public probe and inspect its sanitized receipt.

## AUTH_REQUEST/v1

- Provider/screen: Google Gemini API / the already-authorized local secret store.
- Exact action: create or authorize one free-tier Gemini API credential for the intended Google project and store it locally under the adapter's `GEMINI_API_KEY` process-bound secret boundary; do not paste it into chat, GitHub, Git, prompts, or fixtures.
- Why human action is required: this run has no credential and cannot perform account/project selection, consent, or 2FA autonomously.
- Sign-in/2FA/project choice/key creation: may be required by Google; the human must select the intended project and confirm the credential is limited to the Gemini API capability.
- Billing: keep billing disabled and free-only; do not attach a paid billing account or enable paid operation.
- Revocation: revoke/delete the created credential in the selected Google project and remove the local secret-store entry.
- Validation after action: rerun one low-sensitivity public synthetic prompt through `GeminiExternal`, verify a sanitized capability/receipt, and confirm the local/private Gemma route still passes.
