# GitHub / Forgejo split policy

**Policy ID:** MIN-93  
**Status:** Active operating rule  
**Owner:** Mindrock network  
**Forgejo administration:** Gemini CLI on Darwin

## Rule

Use GitHub only for material that must be visible to the external world:

- public releases and their release documentation;
- inbound pull requests from partners or LPs;
- the public source and evidence required to reproduce a release.

Use the private Forgejo instance over Tailscale for all internal work:

- working notes, findings, and drafts;
- machine-generated backlog and triage output;
- internal review material that is not part of a public release.

The placement test is simple: **if an artifact is needed by the external
world, put it on GitHub; otherwise, put it on Forgejo.** This is a standing
routing rule, not a one-time repository migration.

## Required flow

1. Generate and review internal material in Forgejo.
2. Keep internal drafts out of GitHub, including issue drafts mined from a
   public GitHub PR.
3. Promote only an approved public release (or an explicitly accepted
   partner/LP PR) to GitHub.
4. The public release must link back to the exact source commit and release
   evidence; private working material remains referenced by its Forgejo
   coordinate.

## First application: PR #168

The PR #168 mining output is an internal backlog. Its issue drafts belong in
the Forgejo-side project (`codex-wolfram/pr168-triage`), not as GitHub issues.
See [`pr-168-forgejo-migration-record.md`](pr-168-forgejo-migration-record.md)
for the sealed local export and publication gate.

## Guardrails

- Never mirror internal drafts to GitHub for convenience.
- A local JSONL export is preparation evidence, not proof of Forgejo
  publication.
- Publication requires an authenticated Forgejo session or scoped issue-write
  token owned by the Darwin admin lane.
- If publication access is unavailable, report `BLOCKED` and retain the exact
  artifact hashes; do not claim the migration is complete.
