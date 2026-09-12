# Research Scout — LiteLLM MCP auth bypass decision note

Date: 2026-09-12
Priority: P2 security relevance; no execution authorized.

## Finding
GitHub Advisory GHSA-7488-6r32-c95q / CVE-2026-59822 documents a high-severity LiteLLM MCP authentication bypass affecting `litellm < 1.84.0`. A fabricated `Authorization: Bearer ...` value could reach MCP tooling through the OAuth2 passthrough fallback without a valid LiteLLM key. Fixed in 1.84.0. Advisory recommends upgrading or blocking `/mcp/` routes if immediate upgrade is impossible.

Primary evidence: https://github.com/advisories/GHSA-7488-6r32-c95q
Fix/release: https://github.com/BerriAI/litellm/releases/tag/v1.84.0

## Local relevance / falsification
A code search of `pashamango/minutta-rp-pr-cycle-lab` for `litellm` returned no matches in the default branch, so there is no evidence from this repository that the current lab stack is directly exposed. This is therefore a router-design guardrail, not a claim of present compromise.

## Decision impact
For any Gemini/NICLI/PentAGI multi-provider router candidate using LiteLLM, require `>=1.84.0` and fail-closed MCP authorization before admission. Do not treat an LLM proxy's OAuth passthrough as the constitutional authority boundary; keep mutation/authorization checks outside the model/proxy path.

## Quota discipline
No Codex execution allocated. Quota counters were not observable and were not estimated. Luna/Light remains the downstream default per `research/quota-governor-v0.md`.
