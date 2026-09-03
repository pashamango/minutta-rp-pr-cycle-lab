# COLLATZ-TAIL-0001 recovery report

Issues: #13, #17

## Result

```text
cases: 0
transitions: 0
mismatches: 0
first counterexample or PASS: BLOCKED
```

The requested independent comparison could not be run. The task gives the
centered representation

```text
n = -1/3 + 2^k u
```

and names the coordinate stages `MATCH -> STRIP -> x3 -> RE-CENTER`, but neither
the task nor the current repository defines those stages as machine-checkable
operations that independently produce `k_i` and `n_{i+1}`. Implementing a
coordinate evaluator from the available material would therefore require either
inventing the missing coordinate model or reusing the DIRECT calculation. Both
are expressly forbidden by Issue #13.

Consequently, no transition is claimed as coordinate-verified and no PASS or
counterexample is reported. In particular, this recovery does **not** claim to
have verified

```text
3*n_i + 1 = 2^k_i * n_{i+1}
```

for any coordinate-generated transition.

## Independent recovery checks

The immutable mailbox run for `COLLATZ-TAIL-0001`, lease
`32d5f867461449339baa82dc803826a3`, was inspected. Its captured result was
`BLOCKED`, and its stdout explicitly records that it created no files, branch,
commit, push, or PR. Repository and GitHub state independently confirmed that
there was no prior `agent/wolfram/COLLATZ-TAIL-0001` branch or PR to recover.

The current `main` tree was searched for existing definitions before deciding
that reproduction was blocked. The only matches were unrelated uses of `EXIT`
in mailbox dispatcher tests; there were no Collatz coordinate definitions or
artifacts.

## Reproduction

Runtime:

```text
Python 3.12.0
```

Exact repository search command:

```sh
rg -n 'MATCH|STRIP|RE-CENTER|centered|2-adic|Collatz|Tail Lemma|landmark|EXIT' . --glob '!*.lock'
```

Observed runtime: `real 0.03s` (`user 0.00s`, `sys 0.00s`).

## Exact blocker

Missing machine-checkable, independent definitions for `MATCH`, `STRIP`, and
`RE-CENTER` that map an odd integer's centered 2-adic coordinate to `k_i` and
`n_{i+1}` without evaluating the DIRECT successor formula.

COLLATZ_RECOVERY_BLOCKED: missing machine-checkable, independent definitions for MATCH, STRIP, and RE-CENTER
