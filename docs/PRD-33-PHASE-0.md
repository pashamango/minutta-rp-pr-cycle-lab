# PRD-33 Flash Paper — Phase 0 foundation

This change provides the first narrow, venue-independent lifecycle core. It is
not a trading connector and does not hold keys, execute trades, or create a
persistent virtual balance.

## Invariants

- `open(limit)` emits `Opened` and records one active position.
- `close(proceeds, fee_bps)` emits `Closed`, burns the active exposure, and
  returns net proceeds. No balance field exists anywhere in the core.
- A second open and a close without an open position are rejected.
- The core accepts no market-data input and performs no network access.

The event vector is the append-only telemetry boundary. A later adapter can
serialize these events to JSONL or a hash-chained ledger without changing the
lifecycle rules.

## Honest-fee boundary

The current core takes a venue adapter's already-computed fee rate in basis
points. It intentionally does not claim to reproduce the Polymarket US fee
formula yet; pinned venue vectors and a WASM/browser surface remain follow-up
work requiring an approved venue specification.

## Verification

```sh
cargo test -p amde-demo-wasm flash_paper
```
