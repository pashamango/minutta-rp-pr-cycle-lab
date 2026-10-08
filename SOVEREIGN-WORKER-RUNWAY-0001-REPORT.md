# SOVEREIGN-WORKER-RUNWAY-0001

## Verdict

**REDESIGN.** The policy/router slice is reproducible and fail-closed, but the
actual Gemma loopback request timed out after the client’s observed 60-second
read timeout. This validates routing, not a working end-to-end worker.

## Evidence

- Ollama `0.33.2` responded on `127.0.0.1:11434`; installed models included
  `gemma4:latest` (tools/thinking), `qwen2.5-coder:7b`, and `nomic-embed-text`.
- Current PentAGI supports native Gemini and Ollama providers, but documents
  Gemini through `GEMINI_API_KEY`; Vertex service-account/OAuth is not wired.
- Tests pass 3/3: sensitive marker routes local; public route returns
  `AUTH_REQUEST_REQUIRED` without a credential; private route invokes local.
- The real private request reached loopback Ollama but timed out after 60
  seconds. No output, token count, quota, or external latency is claimed.

## Architecture

Use a sovereign router as policy boundary. Ollama is **NEEDED** for the current
private lane and **USEFUL-OPTIONAL** as a gateway; retain it as local runtime,
with external Gemini routed separately. It is not replaceable by this evidence.
PentAGI should remain the worker harness for later tool/delegation tests, with
the router in front of it.

Private credentials, correspondence, unpublished context, and secret residual
parameters stay local. Public research and synthetic/public-repository work may
use Gemini only after authentication. The marker classifier is conservative,
not a complete privacy solution.

## AUTH_REQUEST

Authorize one Google AI Studio experiment project with billing disabled and the
narrowest current Gemini credential. Store it only in a local Keychain-backed
broker, expose a short-lived request capability to the router, and define
revocation before use. Pasha must perform sign-in, consent, project selection,
and MFA in the trusted browser. No secret goes into Chat, GitHub, the repo,
logs, shell history, or model input.

## Wise Broker pass

The highest-value cheap discovery was tested: the public lane is inert until
auth exists, returning `AUTH_REQUEST_REQUIRED` without network activity or
secret emission. This avoids accidental paid usage despite “free tier” claims.

## Next task

Implement the Keychain-backed broker, then run one synthetic public Gemini request
after explicit AUTH_REQUEST approval and compare observed useful output, latency,
retries, and quota. Separately diagnose local Gemma cold-start/compatibility
latency before calling the local slice production-usable.
