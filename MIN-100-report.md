# MIN-100 execution receipt

## Outcome

`BLOCKED` after bounded extraction and provisional type/route passes. No Linear or Forgejo mutations were made.

## Summary

- Extracted the live `pashamango/minutta-rp-pr-cycle-lab` tracker into JSONL and raw responses.
- Captured 450 non-PR issues and 61 pull requests across six pages with `per_page=100`.
- Captured comments only for issues whose metadata reported comments.
- Deduplication is not claimable: the required MIN/PRD corpus and PR-168 `triage-pass1.jsonl` are absent from this isolated worktree.
- Type and route files are provisional keyword/claim heuristics only; they are not executable backlog.

## Evidence / Artifacts

- `evidence/min100-extract/jsonl/issues-full.jsonl` — 450 records.
- `evidence/min100-extract/jsonl/prs-full.jsonl` — 61 records.
- `evidence/min100-extract/ledger/pages.json` and `ledger/summary.json` — page and count ledgers.
- `evidence/min100-extract/passes/` — blocked dedup ledger plus provisional type/route outputs.
- `evidence/min100-extract/SHA256SUMS` — 236-entry manifest; verified with zero mismatches.
- `BLOCKER-MIN-100.md` — explicit blocker and next valid command.

## Checks

- JSONL parse and required-field validation: PASS.
- SHA-256 manifest verification: PASS, 0 mismatches.
- `python3 -m unittest discover -s tests -q`: PASS, 117 tests.

## Limitations

The ticket's expected 441 issues + 45 PRs differs from the live capture (450 + 61). Do not treat provisional routes as new until MIN/PRD and the frozen PR-168 triage corpus are mounted and the dedup pass is rerun. Forgejo publication remains pending valid credentials and dedup completion.
