# RP-PNP-001 Phase 0: contextual difficulty boundary

This note is an executable specification boundary, not a P vs NP result.

## Claims and non-claims

* `P ⊆ NP` and the status of `P ?= NP` are preserved. A finite benchmark,
  speedup, hint, promise, or changed model does not resolve that question.
* `D_epsilon(x | c, A_set)` is an empirical, preregistered quantity: the
  least observed budget in a declared run plan whose independently validated
  success rate reaches `1 - epsilon`. It is not an asymptotic complexity
  class and its infimum may be unknown or unattained.
* Context construction and hint/preprocessing costs are part of the budget.
  A context can change the task or promise; it does not silently change the
  complexity of the original language.
* A timeout is `TIMEOUT_OR_INTERRUPTED`, never proof of nontermination.
  An agent report is evidence with provenance, not an oracle.

## Phase-0 data model

The prototype uses the following orthogonal axes:

* `C?`--`C4`: justified algorithmic upper-bound rank only;
* `D?`--`D4`: observed difficulty rank under a declared cutoff;
* epistemic state: true, false, unverified, or undecided;
* termination state: machine-proven, observed, timeout/interrupted, or
  unknown.

No axis implies a lower bound, truth, permission, or generic halting result.

## Falsification cases

The tests cover: a validated context-cost accounting example; rejection of an
unvalidated success report; timeout versus eventual completion; and the
standard diagonal contradiction for any claimed total `HALTS(program,input)`
oracle. The diagonal test is a mathematical boundary check, not a performance
benchmark.

## Deferred work

Lean files (`Complexity.lean`, `Difficulty.lean`, `BarberIndexed.lean`,
`MonitorSoundness.lean`, `HaltingBoundary.lean`) require an approved Lean
project/toolchain and clean-room replay. This repository currently has neither;
adding `sorry`, `admit`, or an unsound axiom would violate the proposal.
