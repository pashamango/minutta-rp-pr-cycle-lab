# SOVEREIGN-WORKER-RUNWAY-0002

## Verdict

**AUTH_REQUIRED.** The private lane is now reproducibly useful with the
smallest tested Gemma fix. The external lane remains fail-closed because no
provider credential is authorized in this run.

## Durable evidence

- Ollama `0.33.2` was reachable at `127.0.0.1:11434`; installed completion
  models included `gemma4:latest` and `dolphin-llama3:latest`.
- Required regression fixture: Gemma with default thinking and
  `num_predict=32` returned HTTP success in `17.992s`, but an empty visible
  response with `done_reason=length` and `eval_count=32`.
- Smallest promising change: the same Gemma prompt with `think:false` and
  `num_predict=64` returned a useful sentence in `15.277s`, with
  `done_reason=stop`, `prompt_eval_count=20`, and `eval_count=30`.
- A same-path Dolphin control returned useful text in `29.955s` with
  `done_reason=stop` and `eval_count=28`; it is slower on this host, so it is
  not selected as the default.
- Router tests pass 4/4. Sensitive text routes `local-private`; public text
  returns `AUTH_REQUEST_REQUIRED` without reading, emitting, or placing a
  credential in model context. Retry metadata is explicit (`retry_count: 0`)
  and no token counters are invented.

## Component decisions

- **Ollama: KEEP-RUNTIME.** Loopback transport and Gemma completion work after
  disabling thinking for the bounded slice.
- **PentAGI: OPTIONAL.** It adds orchestration friction and is not needed to
  prove the router boundary; place it behind this router for later tool tests.

## AUTH_REQUEST

Pasha should sign in to Google AI Studio, select one project/account with
billing disabled, and approve a minimal free-tier Gemini test. The credential
must be held by a local Keychain-backed broker, exposed only as a short-lived
request capability, and revocable after the test. Do not paste or commit a
secret. Immediately afterward run one synthetic public-repository prompt and
record provider, model, latency, retry metadata, and observable usage.

## Wise Broker pass and next step

The adjacent high-value opportunity is the already-tested conservative router:
it increases useful local work without human per-request routing. The
simplest next step is to add the approved short-lived external capability to
that same boundary and run one low-sensitivity comparison; this increases
compute without increasing routing burden.
