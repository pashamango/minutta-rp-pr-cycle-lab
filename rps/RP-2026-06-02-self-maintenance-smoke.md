# RP-2026-06-02-self-maintenance-smoke

## Contract

| Field | Value |
| --- | --- |
| RP id | `rp-2026-06-02-self-maintenance-smoke` |
| Type | Request for Proposals |
| Owner | RP/PR Pool |
| Agent | `codex@minutta` |
| Target repo | `pashamango/minutta-rp-pr-cycle-lab` |
| Risk | `L1` |
| Publish policy | `direct_pr_allowed` |
| Bonus | `lab-credit: 1` |
| Release Committee | Chair + Codex rehearsal |

## Scope

Create a basic recurring self-maintenance check for the Minutta PR workflow.
The check should be safe to run daily from a repository checkout and should
produce only metadata about local tool readiness.

## Required Changes

- Add `tools/minutta-self-maintenance-check.sh`.
- Add `docs/self-maintenance.md`.
- Update `README.md` with the daily command.

## Acceptance Criteria

1. `tools/minutta-self-maintenance-check.sh --help` exits `0`.
2. `tools/minutta-self-maintenance-check.sh --repo .` exits `0` in a clean
   checkout.
3. The check reports UTC timestamp, repository path, current branch, dirty/clean
   status, `git` availability, `gh` auth presence as yes/no, and `codex`
   availability as yes/no.
4. The check must not print tokens, secrets, environment variables, file
   contents, SSH keys or credential helper output.
5. `docs/self-maintenance.md` explains when to run it and what to do with a
   failing result.
6. The PR body references this RP id and includes command output evidence.

## Merge Rule

PR acceptance is automatic if the acceptance criteria are met. Merge to `main`
is a separate Release Committee decision.
