# FORGEJO-CREDENTIAL-CAPABILITY-0001

Initial evidence skeleton. This report is bound to the immutable mailbox envelope and records only sanitized capability metadata and verification receipts.

- Task: `FORGEJO-CREDENTIAL-CAPABILITY-0001`
- Source issue: `pashamango/minutta-rp-pr-cycle-lab#178`
- Source digest: `87b17c4550e1bd059d62bc8300be3c9c7ba470b55b71fac34ddbc9144c6bdc6c`
- Lease: `b9a2504dd71d454294f220c4eb8450f5`
- Evidence branch: `agent/wolfram/FORGEJO-CREDENTIAL-CAPABILITY-0001`
- Evidence base: `main` at `725294932d46baec8539686b567da77a97430ea1`
- Initial evidence head: `59ad93f6b4813854c8d8083c7b1c1c1231c6a9fa`

Probe status: `USER_PRESENCE_ENROLLMENT_REQUIRED`.

Darwin has no existing Forgejo-capable helper/client/session. The exact local
publication head is present, but publication, PR creation, and independent
Wolfram manifest verification are unavailable. The minimum request is recorded
in `evidence/CAPABILITY_REQUEST-FORGEJO-CREDENTIAL-CAPABILITY-0001.json`.

First broken transition: `SERVE_ROUTE -> authenticated FORGEJO_GIT`.

Wise Broker `BUTTERFLY/v1`: ADOPT the provider-neutral, repo/verb-bound opaque
capability shape for SmartRouter/SecurityManager reuse; falsify with fresh
process probes for Google, Forgejo, and UDS publishers.
