# CEOffice acceptance plan and bounded verification

Specification v1, 2026-09-05. This file distinguishes checks performed on this proposal from future product acceptance. No event-to-phone, passkey, biometric, live approval, deployment or Darwin test ran here.

## Current versus proposed capability

| Capability | Evidence now | Proposed gate |
| --- | --- | --- |
| Sequential mailbox, bound task outcomes, sanitized GitHub receipts | Merged runbook and installed reporter read; #48 execution-finished and task-blocked receipts inspected | Preserve existing semantics; no changes in this PR |
| PR notification use case | #49 is open draft, same author/owner; prior run reports access timeout | Show blocker and draft separately; no claim of phone push |
| Durable event journal/outbox and independent notifier | Design only; no service discovered or deployed by this task | Phase 1 persistence and delivery proof |
| GitHub Mobile / optional own-update email | Documented possible channels; owner's enrollment/settings and display unknown | Owner-assisted end-to-end measurement; no assumed same-actor push |
| Home Screen Web Push / private inbox | Design only | Phase 2 device and connectivity tests |
| Passkeys / exact-action decisions | Design only | Phase 2 authentication and rejection tests |
| Independent witness | Dependency identified, placement unknown | Separately approved deployment in another failure domain |
| Accessible catalog / 2D / optional 3D | Text/diagram specification only | Phase 3 accessibility/performance evidence |
| A2A / MCP event interoperability | No contract implementation or version claim | Separate adapter review if later needed |

## Phased backlog and exit gates

**Phase 1 — prove one event reaches the phone.** First approve a narrowly scoped implementation/enrollment task. Build durable journal/outbox, verifier and notifier as separately bounded work; preserve the executor. Implement receipt/PR reconciliation and a persistent minimal inbox before claiming reliable alerts. Verify crash-before/after-commit, deduplication, redaction and retry isolation. Owner enrolls/checks GitHub Mobile and optionally own-update email. Use a separately authorized synthetic event; record event ID, source receipt, outbox persistence, eligible channel category, submission/provider evidence if exposed, device/app/OS versions, UTC times and owner's observed lock-screen/inbox result. A same-actor GitHub update that does not push is a **failed push-path test**, even if its PR exists. Optional email is an independently measured fallback, not a repair by creating a bot or reviewer request. Exit only with measured delivery on at least one chosen channel; otherwise retain an explicit delivery blocker. This task sends nothing.

**Phase 2 — persistent decision inbox, passkeys and Web Push.** Approve stable HTTPS origin/RP and recovery bootstrap before credentials are enrolled. Implement minimal accessible inbox, verified ingestion, ACLs, exact-action challenge/nonce store, revocation and manual-forge handoff. Separately enroll installed Home Screen app and Web Push. Test app closed, tailnet off, restored connectivity, denial/revocation, stale evidence, provider outage and independent witness. Exit with the matrix evidence below, threat review and a tested recovery path. Native iOS remains deferred; no automatic merge bridge.

**Phase 3 — catalog and scenario UI.** Add evidence-rich solution cards, tunable discovery explanations, accessible 2D graph/list, provenance-labelled estimates and reviewable daily releases. Measure SPEC performance budgets on an agreed phone/network and test assistive technologies. Optional 3D requires equal functionality in list/2D and reduced-motion support; do not delay core decision access for it. Exit with accessibility, performance, content integrity and rollback evidence. Sensor research is not on the login critical path and needs separate consent/scope.

## Acceptance matrix

All rows are **future product tests**, except the narrowly described synthetic checks in the next section. “Automatic evidence” specifies what a future harness/service can record; it does not imply such a service exists. Human read is an explicit acknowledgement and never proof of comprehension.

| ID / scenario | Expected behavior | Expected automatic evidence | Human evidence / what automation cannot establish |
| --- | --- | --- | --- |
| T01 Run completed without PR | Bound TASK_COMPLETED appears in Results; no missing-PR failure when task did not require one | Matching source/lease/outcome receipt, validations, digest entry; no invented PR | Semantic adequacy of result needs review; digest phone display needs observation |
| T02 Blocked draft PR (#48/#49 pattern) | execution_finished + task_blocked + draft; owner action card; no ready-for-review push | Three independent projections, receipt/PR head references | Timeout cause and phone display cannot be inferred |
| T03 Ready PR | New exact head appears Needs decision; actionable hint outside quiet hours | Snapshot head/base/draft=false and outbox key | Owner verifies useful recommendation and actual display |
| T04 Duplicate / out-of-order receipt | One card; late claim does not regress terminal state; conflict quarantined | Unique key, immutable content comparison, same projection for permutations | Does not prove source content is true |
| T05 Changed PR head or base | Old approval intent expires; confirmation fails atomically and new revision shown | Before/after hashes, stale rejection, unchanged action store | Owner must inspect new diff; cannot infer renewed consent |
| T06 Lost / revoked phone | Sessions, credential and subscription revoked; pending nonce invalidated | Revocation lookup and denied read/action/submission | Cannot remotely prove physical deletion of synced credential or cached OS notification |
| T07 Tailnet off, internet on | Generic push may arrive; private content/action unavailable until reconnection | Provider response; later authenticated reconnect/fetch; no offline approval | Owner observes lock screen and connectivity-dependent opening; no delivery guarantee |
| T08 Coordinator down | Separate witness signals stale heartbeat; notifier delivers if its own dependencies survive | Independent witness timestamps, missed interval, its outbox | Silence does not identify power failure; test requires authorized outage simulation; shared failure can defeat alert |
| T09 Provider outage | Persisted inbox survives; bounded retry/dead letter; no task rerun | Attempt count/reasons/deadline; executor invocation count unchanged | No automatic proof of eventual screen display |
| T10 Notification disabled / quiet hours | Disabled channel stays disabled; noncritical hint deferred; critical retained and submitted only if permitted | Policy version, suppression/defer reason, pending inbox entries | OS settings/Focus may not be remotely observable; owner checks actual behavior |
| T11 App closed | Journal/notifier continue; enrolled push can wake handler; inbox reconciles on next open | Provider acceptance and optional authenticated handler ack | No assumption of permanent background execution; owner verifies lock screen |
| T12 Camera denied | Login/inbox/decision unchanged; no sensor request on normal flow | No camera dependency, successful ordinary flow under denied permission | Permission UI and privacy behavior need device inspection |
| T13 Spoofed event / producer | Reject/quarantine; no actionable event or automatic command | Failed principal/binding/digest check; sanitized audit entry | Same-account forge text alone cannot prove machine identity |
| T14 Execution exit 0 only | Result says task outcome unknown; no completion claim | Execution evidence present, outcome absent, reconciliation scheduled | No inference of Definition of Done from silence |
| T15 Provider accepted, no ack | Show provider accepted / client observation unknown; no human-read marker | Provider ID/time only; no fabricated later timestamps | Cannot automatically establish OS display or attention |
| T16 Replay / deadline / cross-origin | Reject consumed nonce, expired intent and foreign origin; atomic no-op | Rejection codes, action count unchanged, current server time | Browser/OS compromise remains outside assertion guarantee |
| T17 Prompt injection / XSS payload | Escaped evidence; no policy mutation, script or source-command execution | Rendering tests, CSP reports, unchanged policy/action store | Reviewer checks misleading prose and social-engineering risk |
| T18 Recovery / all credentials lost | Secondary recovery works and revokes old access; otherwise decisions suspended | Recovery audit, credential/session revocation, challenge invalidation | Owner identity assurance and platform account recovery require human process |
| T19 Delivery retry / expiry | Same originating event; maximum six attempts, resolved/expired hints stop; dead letter visible | Stable outbox key, reason, attempts <=6, zero new task claims | Provider may have displayed an earlier duplicate; no exactly-once display claim |
| T20 Journal crash / reconciliation | Crash before commit not acked; after commit rediscovered/deduped; overlapping scans converge | Durable rows/cursor, recovered count, no double decision | Storage hardware loss/restore assurance requires operational restore test |
| T21 Graph / probabilities / reduced motion | All decisions reachable in list/2D; uncalibrated probability shown unquantified; 3D optional | Bundle/frame/latency metrics, provenance fields, reduced-motion route | Screen reader usability, clarity and calibration relevance need human review |
| T22 Deterministic safety vs interest ranking | LLM low score cannot remove critical event; opt-out leaves banner/coverage warning | Rule precedence, policy version, retained event and reason | OS may suppress attention even for submitted critical hints |

## Checks performed in this specification task

Observed 2026-09-05, using existing tools only:

- Parsed both JSON files with Python standard library. Schema explicitly fixes draft 2020-12, v1 protocol, bounded fields, closed objects, state enums and conditional review/delivery bindings.
- Checked 12 synthetic events against a focused Python evaluator of the keywords used (`type`, `const`, `enum`, required/properties/additionalProperties, arrays, lengths/patterns/date-time, numeric bounds, allOf/anyOf/not/if/then). All passed. This is **not** a standards-certified validator or full metaschema validation.
- Checked computed idempotency keys, unique event IDs/keys, timestamps and related-event references. Eight mutated examples were rejected: invalid severity, bad lease, invalid date, extra raw-content field, missing decision ID, mismatched PR state, missing related event and delivery object on a non-delivery event.
- Ran synthetic reference reductions: duplicate/out-of-order convergence; finished-only leaves outcome unknown; finished plus blocked stays blocked; no-PR completion stays completed; conflicting duplicate rejected. Checked provider-only state does not imply read. Checked five exact-action predicates: valid binding accepts; changed head, reused nonce, revoked access and deadline equality reject. These are specification logic checks, **not tests of an implemented adapter, authenticator or notifier**.
- Reviewed state enums against SPEC and examples, source bindings, citation provenance, privacy language, permitted four-file diff and Git whitespace checks. GitHub issue #48 and PR #49 were read live; no target/network diagnostics were performed.

Validator limitation: `jsonschema` was unavailable in the default Python and the other existing Python executables checked; Node `ajv` and `ajv/dist/2020` were unavailable. Nothing was installed. Therefore full draft-2020-12 metaschema and independent validator conformance remain **not run**, a documented handoff check before implementation. To reproduce with a later separately available validator, call `Draft202012Validator.check_schema(schema)` and validate every array element with `Draft202012Validator(schema, format_checker=FormatChecker())`; schema format checks alone do not validate cryptographic bindings or state machines. The focused check command/evidence stays in the envelope-controlled task work directory, outside this four-file specification PR.

Synthetic values such as repeated hex hashes are placeholders, not verified content digests. Delivery examples with `unverified` evidence demonstrate representable partial evidence and must not be promoted to trusted actionable state. Twelve examples show independent observations, not a claim that all missing intermediate observations exist. `human_read` and `decision_recorded` examples stand for authenticated-client/decision-service records; an implementation must verify those records and exact action binding beyond schema shape.

Minimal portable binding recheck from this document's directory (Python standard library):

```python
import hashlib, json
from pathlib import Path
schema = json.loads(Path('notification-event.schema.json').read_text())
events = json.loads(Path('examples.json').read_text())
fields = ['protocol', 'task_id', 'lease_id', 'source_sha256',
          'event_type', 'source_record_id']
assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
assert len({e['event_id'] for e in events}) == len(events)
for e in events:
    raw = json.dumps([e[k] for k in fields], separators=(',', ':')).encode()
    assert e['idempotency_key'] == 'sha256:' + hashlib.sha256(raw).hexdigest()
```

## Owner choices

No owner answer is required to review/merge this specification. Three choices block their respective **future implementation/enrollment** steps, not this task:

1. **Stable origin/RP and recovery bootstrap:** which controlled HTTPS tailnet hostname and separately held recovery credential will be authoritative? Recommended: one stable private origin, no aliases/wildcards; second passkey before reliance. Exact hostname/owner bootstrap authority is not invented here.
2. **First measured phone channel:** accept an owner-assisted GitHub Mobile test with optional own-update email fallback, or prioritize separate Web Push enrollment if same-actor Mobile cannot deliver? Recommended: measure existing channels first; no new service identity assumed.
3. **Independent witness placement and availability budget:** which separately powered/connected host or service may observe coordinator freshness, and what recurring cost is acceptable? Recommended: reuse an already authorized independent node if one exists; do not pretend the coordinator can witness its own total failure.

All remaining defaults are in SPEC: private content, generic push, no automatic merge, 22:00–08:00 quiet hours, daily 18:00 digest, six bounded delivery attempts, 30-minute idle/12-hour absolute session, 5-minute action challenge, 2D first and no sensors for login. Tuning is versioned/reviewable.

## Completion boundary

This PR delivers four specification files and bounded checks only. Manual human merge is required; merge does not deploy. The executing agent writes a bound task outcome; installed reporter alone publishes EXECUTION_FINISHED and TASK_COMPLETED after process exit and validation. Until those receipts exist for this task, end-to-end mailbox completion is pending, even if the PR is ready. No receipt is forged or inferred here.
