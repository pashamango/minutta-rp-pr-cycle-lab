# P2 — CANDIDATE / NOT EXECUTION-AUTHORIZED

## MCP RFC 8628 device authorization as capabilityd re-auth primitive

Date: 2026-09-15
Status: CANDIDATE / NOT EXECUTION-AUTHORIZED

### Evidence / source
NousResearch/hermes-agent PR #104891 (`feat: authorize MCP servers with device codes`) merged 2026-09-07. It implements RFC 8628 device-code authorization for MCP servers: terminal obtains verification URI + user code; user can authorize on another device; client polls with pending/slow-down/timeout handling; refresh tokens persist profile-scoped; issuer/resource binding is validated; denied/expired/invalid grants do not replace credentials; partial disk writes roll back. The PR explicitly limits initial device authorization to terminal login and does not claim macOS-native authorization behavior.

Source: https://github.com/NousResearch/hermes-agent/pull/104891

### Proposed asset / capability
A bounded capabilityd authentication profile using standard OAuth RFC 8628 device flow for remote re-authorization from phone, while keeping macOS-local mutation authority behind a separate capability boundary. Treat device authorization as proof of principal presence/consent, not as a mechanism for bypassing macOS TCC/security prompts.

### Expected value
Infrastructure leverage: high if compatible. Removes the browser-callback/local-screen dependency for re-authentication and provides a standard refresh/revocation lifecycle. Reusable across MCP-facing local agents and routers. Does not itself solve macOS TCC approval; value is clean separation of principal re-auth from OS-local privilege enforcement.

### Time to first useful result
Day: protocol/design falsification. Week: isolated non-production proof if later authorized by Research Market.

### Complexity / risk
Medium. Main uncertainty: whether the intended capabilityd authorization server/client topology can expose RFC 8628 safely while binding resulting tokens tightly enough to device/session/capability scope. Security risk if a device token is mistaken for authorization to perform arbitrary local mutations.

### Smallest falsification / feasibility test
Without touching production or local runners: write a protocol test matrix comparing capabilityd requirements against RFC 8628 + MCP resource/issuer binding: remote phone approval, token expiry/refresh, reboot invalidation, capability attenuation, revocation, replay resistance, and explicit separation from macOS TCC. Fail the candidate if any required local privilege can only be represented by an over-broad bearer token.

### Compute / quota cost
Web/Git design review: negligible. Later isolated implementation: low local compute / low Codex class, but Research Market alone may authorize execution.

### Why now
A maintained agent implementation has already merged and adversarially tested the exact terminal-without-browser-callback flow. This reduces protocol invention risk and directly matches the previously identified need for remote re-authentication after absence/reboot without requiring the principal to be physically at the Mac.

### Scout decision
Record candidate only. Do not CLAIM, dispatch, install, authenticate, or mutate local infrastructure.