# FORGEJO-TAILSCALE-RECOVERY-0002

Status: `FORGEJO_LOCAL_RECOVERED_TAILNET_BLOCKED`

This report is bound to task `FORGEJO-TAILSCALE-RECOVERY-0002`, source Issue #175, source digest `0c532583192a5f7150fe89d5cf40a6560cbcb734197f187182edbaeacd63d559`, and lease `abd57a370bf346cd83e124d2662bfc88`.

The required pre-mutation evidence checkpoint records the exact GitHub base and initial head. Darwin inspection and any existing-service recovery remain pending until this branch is published and its PR is open.

## Checkpoint

- Base branch: `main`
- Initial head: `725294932d46baec8539686b567da77a97430ea1`
- Task branch: `agent/wolfram/FORGEJO-TAILSCALE-RECOVERY-0002`
- Scope: preserve predecessor evidence, localize the bounded transition, and publish existing manifests only.

## Verified evidence

- Predecessor artifact: not found in bounded Darwin/mailbox task, run, worktree, or lab locations; no artifact was copied or modified.
- Existing Darwin publication branch resolves `83f1dae7ccba09832cac996316323f2829fee7a3`.
- Forgejo LaunchAgent: running, PID 1436, last exit code 0.
- Listener: `127.0.0.1:3001`, PID 1436; local HTTP returned 200.
- Tailscale app: installed, version 1.102.3; app CLI reports Darwin connected at `100.112.18.4`.
- DNS: `darwin-on-macbookpro3-4.tail94aa6c.ts.net` resolved to `100.112.18.4`.
- Existing Serve state: tailnet-only `/forgejo -> http://127.0.0.1:3001`; `/gd2.git`, `/ceoffice/`, `/delegation`, and `/ceoffice/api/` were preserved and not changed. Funnel was not enabled.

## Transition result

`LAUNCHAGENT -> PROCESS -> LISTENER -> LOCAL_HTTP -> TAILSCALE_STATE -> DNS -> SERVE_ROUTE` passed. The first broken transition is `SERVE_ROUTE -> FORGEJO_GIT`: HTTPS Forgejo `ls-remote` from Wolfram returned HTTP 403 Forbidden. Darwin’s publication checkout has only a local bare-repository remote, which is not an authorized Forgejo transport and was not used.

No service mutation was necessary or performed. No restart, reload, Serve change, credential access, force-push, direct bare-repository write, merge, or artifact-byte change occurred.

## Blocker analysis

The missing capability is normal authenticated Git transport to the existing private Forgejo repository (`chitakasha/gd2`) through the restored tailnet route. HTTP reachability and Forgejo page access do not establish Git authorization. Retry is safe after the existing Forgejo Git credential/authorization is restored; do not repeat GD2 research or alter the publication manifests. Pasha is not required for diagnosis, but an authorized credential/session owner is required to restore the missing Git capability. `BUTTERFLY/v1`: ADOPT — the evidence demonstrates that supervisor/process state is weaker than listener and HTTP readiness.
