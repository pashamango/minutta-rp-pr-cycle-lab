# MIN-49: bounded RP factory

The factory is intentionally local and fixture-backed. `build` records an anomaly,
source receipt, owner, cost/risk/confidence fields and creates a replayable fixture
plus a private issue draft. `run` is `BLOCKED` unless `--authorize-forgejo` is
explicitly supplied; an authorized command is bounded to 30 seconds and its exit
code is recorded. Every outcome has a canonical SHA-256 digest.

Only a `PASSED` outcome can create `github-pr-proposal.json`. That bundle separates
public output from private evidence and states that protected `main` requires human
review. No command in this package contacts Forgejo, Linear or GitHub.

Example:

```sh
python -m rp_factory.cycle build anomaly.json run/min-49
python -m rp_factory.cycle run run/min-49 --authorize-forgejo --command true
python -m rp_factory.cycle publish run/min-49
```
