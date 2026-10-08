# PROJECT-OFFICE-0003

Portable Git state is canonical: Company contains Portfolios; Portfolios contain long-lived Projects; Projects own mission, stage, budget/KPIs, gates, claims, evidence refs, and status. Issues are replaceable work packages. Packets propose gate movement; only a separate verifier may accept them, with reviewable durable evidence required.

Scientific and execution results are independent. `NEGATIVE + SUCCESS` can satisfy a falsification/information gate. `BLOCKED`, `FAILURE`, and `NO_RESULT` cannot move an operational gate; `NO_RESULT` routes to escalation. `NO_PR_REQUIRED` is a worker-ungrantable exception for a transient probe whose immutable receipt is complete evidence.

Forgejo/GitHub is a projection: Company → namespace, Portfolio → board or YAML, Project → repository/`PROJECT.yaml`, Gate → milestone/state, Issue → work package, Claim → typed object, Evidence/PR → acceptance packet. `forgotten_value(project)` is the minimal Detective query for closed work with unconsumed evidence and an unmet gate.

Verdict: `PROJECT_ACCEPTANCE_MODEL_READY`
