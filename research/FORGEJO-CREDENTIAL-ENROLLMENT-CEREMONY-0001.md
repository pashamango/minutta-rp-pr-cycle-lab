# FORGEJO-CREDENTIAL-ENROLLMENT-CEREMONY-0001

## Publish-before-inspection checkpoint

The checkpoint was published as PR #182 before the permitted Darwin inspection.
The authorized read-only SSH probe reached Darwin (`Darwin-on-MacBookPro3.local`,
macOS `12.7.6`), but no supported Forgejo CLI/client or version was exposed.
The Forgejo launchd service also exposed no safe account listing. The exact
provider login, stable ID, account state, and `chitakasha/gd2` permission are
therefore unresolved. `codex@wolfram.local` is not used as a provider login.

- task: `FORGEJO-CREDENTIAL-ENROLLMENT-CEREMONY-0001`
- source issue: `181`
- source digest: `c65f1df60094cbb754d7c1be5859510f4d1c4c6e51f6452cacbe279b52bf8113`
- lease: `b15d087676c1412e875e5a20ee7e8637`
- base: `main`
- initial head: `d1438eee323834fc99be07dbf571fcec44185845`
- checkpoint PR: `https://github.com/pashamango/minutta-rp-pr-cycle-lab/pull/182`

## Result

`PRINCIPAL_AMBIGUOUS`. No user-presence request is routed. The missing safe
representation is a supported, read-only Forgejo account/repository metadata
surface that returns only login, provider ID, kind/state, and permission; the
installed Forgejo version and supported mechanism must be identified through
the same safe boundary.

The synthetic wrapper in `tools/forgejo_ceremony.py` models a future split
relationship: a Git-publication capability and a separate PR capability can
share the same principal/repository binding while retaining least authority.
It returns only an opaque handle. Wrong principal/repository, escalation,
missing handle, revoked capability, and replay-like inactive use fail closed.
The fixture uses no real secret and does not perform enrollment.

Future ceremony, only after principal resolution: one local user-presence
action releases the secret to a backend-held helper; the agent receives only
the opaque handle. Verify authenticated read, non-force branch push of commit
`83f1dae7ccba09832cac996316323f2829fee7a3`, exact remote head, one PR, and an
independent Wolfram manifest. Revoke both capability artifacts and confirm
fresh-process access fails. Publication remains evidence, not completion.

## Scope guard

No real credential, token, password, key, account, Keychain item, browser
session, or secret-bearing database content is read, created, requested, or
published by this checkpoint.
