# Self-Maintenance Check

Run the self-maintenance smoke check once per workday from a repository
checkout before starting RP/PR workflow rehearsal:

```sh
tools/minutta-self-maintenance-check.sh --repo .
```

The check prints metadata only:

- UTC timestamp
- repository path
- current branch
- clean or dirty status
- `git` availability
- `gh` auth presence as `yes` or `no`
- `codex` availability as `yes` or `no`

It must not print tokens, environment variables, file contents, SSH keys,
credential helper output, or other private data.

If the command fails, fix the reported path or git checkout issue, then rerun
the check. If it exits successfully but reports `status=dirty`, review the
working tree before opening a PR. If it reports `gh_auth_present=no` or
`codex_available=no`, restore the missing local tool readiness before using
that tool in the RP/PR workflow.
