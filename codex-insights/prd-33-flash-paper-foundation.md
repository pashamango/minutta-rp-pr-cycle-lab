# PRD-33 insight: flash-money is an event invariant

The smallest useful proof for Flash Paper is not a balance ledger: it is the
absence of a balance. The lifecycle can be tested as `Opened -> Closed`, with
exposure existing only between those events. This narrows the first core's
state space and leaves JSONL/hash-chain persistence as an adapter concern.
