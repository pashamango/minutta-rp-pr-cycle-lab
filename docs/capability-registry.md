# DP-07 provider capability adapter registry

This registry is a safe, fixture-backed inventory for the Darwin runtime. It
describes interfaces and policy without asserting that a credential exists.
`last_verified_at` means the fixture entry and its documented API boundary were
reviewed; it does not mean that a live request was made.

## Access states

| State | Meaning |
| --- | --- |
| `SOURCE_READ` | Darwin has an approved, currently usable read path. |
| `READ_BLOCKED` | The source is in scope, but Darwin lacks authorization, transport, or a required local capability. |
| `SUMMARY_ONLY` | Only a user-provided or connector-produced summary is available; raw source reads are not implied. |

The registry intentionally does not infer credentials from an in-Chat
connector. A ChatGPT connector being visible in a conversation is not evidence
that its OAuth grant, API key, scheduler, or transport can be mounted on
Darwin. Cookies are never scraped, quotas are never bypassed, and no external
account is enrolled by this fixture.

## Provider adapter contract

Provider adapters are declarative until a documented vendor API, least-privilege
OAuth scope, and durable authorization path are all present. Each adapter entry
must carry a permission probe, source identity, identity-bound cursor, resource
boundary, rate-budget observation contract, and a source-local revocation test.
`READ_BLOCKED` is an authorization/provenance result, not an empty result: the
runtime must not turn an inaccessible source into `0` activity. Sales has no
generic activity endpoint here; it requires a named connected CRM/API or an
explicitly instrumented interaction receipt.

## Schema and validation

The canonical fixture is [`capability-registry.json`](capability-registry.json).
Run the standard-library validator with:

```sh
python3 tests/validate_capability_registry.py
```

It rejects unknown access states, missing source-of-truth fields, timestamps
without an explicit verification method, credentials in fixture values, and
missing consent separation for additional Gmail accounts.

## Privacy and consent

Privacy classes are `public_metadata`, `private_operational`,
`personal_content`, and `secret_material`. The registry may name an owner or
credential *kind*, but never stores a token, password, cookie, private key,
OAuth code, or raw message content.

The primary Gmail account and any additional Gmail account are separate
consent subjects. Adding another account requires a new, explicit consent
record and does not inherit the primary account's grant.

## Source-of-truth rule

Each provider has one `source_of_truth` value: `canonical_api`,
`local_runtime`, `user_asserted_summary`, or `not_available`. Backups and
restores are metadata-only plans until an approved artifact and restore test
exist. A planned backup is not evidence of recoverability.
