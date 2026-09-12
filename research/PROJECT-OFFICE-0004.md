# PROJECT-OFFICE-0004

PROJECT/v1 now requires company identity and durable reviewable evidence. Issue closure remains an ephemeral projection: it cannot accept a gate. `verify_gate_transition` is the verifier-only transition; it validates project/portfolio/company/gate/evidence bindings, rejects worker-granted `NO_PR_REQUIRED`, retains rejected evidence, and consumes exact evidence once on acceptance.

Detective distinguishes closed work with unconsumed evidence (`forgotten-value`) from closed work without evidence (`execution/no-result`). Scientific `NEGATIVE + SUCCESS` is limited to information-gain/falsification gates; blocked, failed, and no-result execution cannot accept.

Deterministic tests cover missing evidence/verifier, exception authority, rejection retention, binding failures, and idempotent replay. Verdict: `PROJECT_ACCEPTANCE_ENFORCED`.
