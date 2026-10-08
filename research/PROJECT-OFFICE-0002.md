# PROJECT-OFFICE-0002

## State model

The deterministic stages are `IDEA -> RP -> RESEARCH[] -> SYNTHESIS -> IC_DECISION -> FOUNDER_CHARTER -> PROJECT_STATUS`. `project-office/state.schema.json` defines the portable shape; `project-office/validate.py` rejects execution unless synthesis, an IC recommendation, and a founder charter all exist. Founder activation is therefore downstream of IC authority, not a research side effect.

## Produced kit and shadow run

Templates cover neutral RP, independent research, synthesis/investment, Founder Charter, and investor reporting. Fixture `VIMANA-PILOT` is explicitly synthetic and unvalidated. Reports R1 and R2 have separate provenance and materially disagree: R1 explores mathematical formalization while R2 rejects unsupported physical feasibility. Synthesis preserves that disagreement; it does not average it away. The IC recommendation is `RESEARCH_MORE`, and the resulting project is `PARKED`.

The charter contains mandate, budget, KPI, constraints, and stop criteria, while explicitly stating `Founder owns HOW; research is advisory`; no research HOW-plan is copied. The investor report separates external KPI (`>100 LPs interested`) from internal activity and records no external signal.

PentAGI mapping: upstream PentAGI/community is the portfolio company/client; Mindrock research/code/review/inference is investment effort; upstream merge/review/reuse/maintainer pull is an outcome signal. Internal commits/issues alone are not success. “PR-as-SAFE-Note” is only an economic metaphor, not a legal ownership or security claim.

## Deterministic evidence

`pytest -q tests/test_project_office.py` covers valid shadow state, invalid RP-to-execution, preserved conflict/provenance, and IC gating. The validator is dependency-free and also runs directly: `python project-office/validate.py project-office/fixtures/vimana-pilot.json`.

## Wise Broker: minimum portable bundle

Successful. The exact minimum bundle is `README.md` (stage semantics and assignment boundary), `templates/research-proposal.md`, `templates/research-report.md`, and a project state/assignment JSON. A fresh ordinary Chat can produce an IC-admissible research artifact from those files alone; mailbox internals are not required. The full kit adds deterministic validation and downstream templates.

## Verdict

`PIPELINE_READY`

## Smallest next step

Have one fresh non-mailbox agent produce a report from the four-file portable bundle, then compare it against the report schema with a deterministic checker.
