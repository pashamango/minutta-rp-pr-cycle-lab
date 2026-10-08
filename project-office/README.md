# Project Office shadow kit

Portable, deterministic semantics for `IDEA -> RP -> RESEARCH[] -> SYNTHESIS -> IC_DECISION -> FOUNDER_CHARTER -> PROJECT_STATUS`.

`state.schema.json` describes the record shape; `validate.py` enforces transitions and the rule that execution requires synthesis, an IC decision, and a founder charter. This is a shadow prototype: it does not schedule founders, allocate LP funds, or publish externally.

An ordinary research agent needs only this README, `templates/research-report.md`, `templates/research-proposal.md`, and the project state/assignment to produce a report. Mailbox knowledge is not required.
