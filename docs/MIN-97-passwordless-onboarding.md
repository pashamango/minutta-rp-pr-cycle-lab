# MIN-97 Passwordless agent onboarding

Status: implementation design / blocked for live provisioning evidence

This document is the contract for onboarding a new agent without putting a
password in chat, a human clipboard, a command line, or an audit log. It does
not grant permission to install a service, change Forgejo, or change Tailscale.

## Phase 1 contract

The controller runs on the Darwin Forgejo host and creates the Forgejo account
with the minimum repository scopes. It then writes a sealed record to the
agent's existing SDVM mailbox. The record contains an opaque bootstrap handle,
the Forgejo username, the Forgejo origin, `issued_at`, `expires_at` (15 minutes
maximum), and a one-time secret encrypted for the agent inbox. The plaintext
secret is never a comment, issue body, process argument, environment dump, or
ledger field.

The first-run client must:

1. read exactly one unconsumed record addressed to its tailnet identity;
2. reject a missing, expired, duplicated, wrong-audience, or already-consumed record;
3. authenticate over the private Forgejo URL using the secret in memory only;
4. exchange it immediately for a narrowly scoped API token;
5. delete/consume the bootstrap record and append a ledger receipt containing
   only the handle, agent identity, scopes, timestamps, token fingerprint, and
   result (`consumed` or `rejected`); and
6. use the API token from a protected local credential store, never stdout.

The controller must make the consume operation idempotent and atomic. A retry
may reconcile an existing receipt, but must not mint a second token or replay
the bootstrap credential. Clock skew is handled by a bounded tolerance in the
controller; the client never extends the TTL.

### Required ledger fields (redacted)

```json
{
  "event": "forgejo.bootstrap.consumed",
  "handle_sha256": "<sha256>",
  "agent_tailnet_identity": "<stable identity>",
  "forgejo_username": "<username>",
  "scopes": ["repo:read", "repo:write"],
  "issued_at": "<UTC>",
  "consumed_at": "<UTC>",
  "token_fingerprint": "<sha256>",
  "result": "consumed"
}
```

No field may contain the bootstrap password, API token, Authorization header,
or a reversible encoding of either secret.

## Phase 2 design spike

Selected mechanism: a tailnet-only Caddy authentication gateway in front of
Forgejo, using Tailscale LocalAPI `whois` on the proxy host to resolve the
connecting node identity. The proxy passes a verified, allowlisted identity
header to Forgejo over a private loopback/upstream connection. Forgejo is
configured with `ENABLE_REVERSE_PROXY_AUTHENTICATION`; the proxy strips any
client-supplied identity header before adding its own. Direct Forgejo access
and non-tailnet requests are denied.

The spike must confirm, on the actual Darwin installation, the LocalAPI
endpoint and permissions, the exact Caddy auth-handler configuration, header
trust boundary, Forgejo auto-provision behavior, identity-to-user mapping,
revocation latency after a tailnet ACL removal, and audit-log correlation.

Estimated work: 2--4 engineering days for a test-only gateway and mapping
adapter, plus 1 day for security review and anonymous/direct-path negative
tests. Production rollout remains a separate approval-gated task.

## Acceptance evidence and current limitation

The required Phase 1 evidence is a fresh test agent receiving a Forgejo token
in under five minutes, plus a matching redacted ledger receipt. The required
Phase 2 evidence is this mechanism choice and estimate, followed by the live
spike checks above. This checkout provides the mailbox primitives and contract,
but no authorized Darwin Forgejo admin CLI, test account, or proxy deployment.
Therefore live Phase 1 provisioning is **BLOCKED / NOT PROVEN** here; no
password or token was requested, copied, tested, or published.

Independent verification:

```sh
python3 -m unittest discover -s tests -v
git diff --check
```
