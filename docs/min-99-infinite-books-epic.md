# MIN-99 — Infinite Books: discovery and phased epic

## Outcome

This is a discovery handoff for the proposed reader-local WASM Text Gen book
system. No book source was imported and no runtime was implemented. The local
checkout does not contain the requested “Остров Крым” or Gaza source, nor a
materialized PR-168 triage export. Those inputs remain `SOURCE_NOT_FOUND`.

## Evidence / coordinates

| Item | Result |
|---|---|
| Repository | `https://github.com/pashamango/minutta-rp-pr-cycle-lab.git` |
| Branch | `agent/wolfram/MIN-99-INFINITE-BOOKS-0001` |
| Base commit | `b3fcc54` (`feat: add fail-closed RP factory for MIN-49`) |
| Search scope | tracked files plus local lab/worktree files under the parent checkout |
| Source search | `rg -n -i 'Infinite Books|Остров Крым|Crimea|Gaza|441' ...` |
| PR-168 search | tracked/local filenames and content matching `pr168`, `triage`, `441` |
| Verification | `git status --short --branch`; `git ls-files`; the search command above |

The parent checkout contains unrelated untracked work. It was preserved and is
not part of this handoff.

## Proposed phases

1. **Source intake (blocked):** obtain an authorized repository URL, exact
   branch/commit, licensing/usage decision, and immutable SHA-256 manifest for
   “Остров Крым” and Gaza sources. Do not infer or scrape an unnamed repository.
2. **Corpus and issue mining:** materialize the PR-168 export and its 441-issue
   candidate set; normalize issue IDs, deduplicate, classify by the semantic
   stack/book structure, and retain provenance for every finding.
3. **Narrative IR:** specify typed linguistic IR, sense-addressed JSON,
   semantic atlas, role binding, epistemic query contract, temperature/two-
   channel control, semantic routing keys, and route certificates.
4. **Book constraint model:** specify committed TOC constraints, attribute DAG,
   append-only narrative event log, and causal-clock/partial-order semantics.
5. **Reader-local execution slice:** build a tiny deterministic WASM text-gen
   adapter with explicit capability detection, bounded compute, cancellation,
   reproducible seeds, and no server-side access to reader content.
6. **Safety and provenance gate:** test prompt/data boundaries, content
   addressing versus lazy inference, replayability, source attribution, and
   fail-closed behavior when WASM or model assets are unavailable.
7. **Pilot and release gate:** run one authorized corpus through a minimal
   chapter loop, publish manifests and receipts, and route the final project
   gate to Pavel for acceptance.

## Acceptance gates for the next task

- `SOURCE_FOUND` with repo, branch, commit, license decision, and SHA-256
  manifest for each corpus; otherwise remain blocked.
- A local JSONL issue ledger with stable source coordinates and zero silent
  deduplication.
- A versioned IR/schema fixture plus deterministic replay fixture.
- A WASM capability/compute budget test that passes offline and fails closed.
- A clean checkout command that reproduces every claimed artifact.

## Limitations and blockers

- No authorized source coordinates were supplied for either corpus.
- No 441-issue PR-168 export was present in the inspected checkout.
- No Linear mutation was attempted; ticket remains under Principal control.
- This document is planning evidence, not proof of a working Infinite Books
  implementation.
