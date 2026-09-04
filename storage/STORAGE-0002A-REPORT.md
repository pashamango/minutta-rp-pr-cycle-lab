# STORAGE-0002A sanitized cutover report

- new ChitAkasha writes default outside Documents: PASS
- provider-neutral workspace namespace: PASS
- bounded per-task workdir: PASS
- Git worktree root under ChitAkasha-Storage: PASS
- dual-lineage T0 recorded: PASS (private local record; no personal filenames)
- conflict-preserving reconciliation policy: PASS
- Documents modified: NO (metadata-only directory probe)
- mailbox regressions: PASS

## macOS permission target

The scheduled chain is the user LaunchAgent `com.chitakasha.agent-mailbox`,
executing Python.org `Python.app` (`org.python.python`, team `BMM5U3QVKW`), which
runs the mailbox cycle and dispatcher; the dispatcher launches Homebrew Node and
the signed OpenAI Codex executable (`codex`, team `2DC432GLL2`). For the next
migration retry, approve Files and Folders access to Documents for Python.app at
`/Library/Frameworks/Python.framework/Versions/3.12/Resources/Python.app`.
If macOS attributes access to the child responsible process, also approve the
bounded Codex executable path reported locally by the diagnostic command in the
runbook. No permission was granted programmatically.
