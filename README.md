# Minutta RP/PR Cycle Lab

This private repository is a clean rehearsal surface for the Minutta RP/PR
workflow. It contains no household data, secrets, model logs or credentials.

## Purpose

Use this repo to test the full cycle:

1. write a Request for Proposals;
2. let `codex@minutta` produce a narrow implementation;
3. publish a GitHub pull request;
4. record PR acceptance and bonus accrual in the RP/PR Pool;
5. let the Release Committee merge the selected PR to `main`.

## Current RP

- [RP-2026-06-02-self-maintenance-smoke](rps/RP-2026-06-02-self-maintenance-smoke.md)

## Daily Self-Maintenance

Run this metadata-only smoke check once per workday from a repository checkout:

```sh
tools/minutta-self-maintenance-check.sh --repo .
```

## Wolfram mailbox

New ChatGPT sessions should start with the canonical [ChatGPT mailbox runbook](CHATGPT-MAILBOX-RUNBOOK.md). A reusable Issue envelope is available in [the mailbox task template](templates/mailbox-task-v1.md).

## NICLI Dispatcher v0.1 (MIN-74 / MIN-75)

Deterministic control plane, SQLite transactional leases, and shadow admission for Linear candidate tasks. Model is pinned to Gemini 3.8 Flash Medium. See the [NICLI Dispatcher documentation](nicli_dispatcher/README.md) for architecture, gates, and CLI runbooks.

## Safety

- Do not commit tokens, SSH keys, browser cookies, raw household logs or private
  files.
- Keep checks metadata-only.
- Keep PRs small enough to review in one sitting.
