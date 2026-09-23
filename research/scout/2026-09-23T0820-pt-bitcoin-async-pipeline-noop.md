# Research Scout — 2026-09-23 08:20 PT

Status: NO-OP / WATCH
Mode: CHAT-ONLY; no execution authorized.

## Lead
Asynchronous Pipeline Consensus: Decoupling Mining from Full-Block Validation (Delving Bitcoin, posted 2026-09-22).
Source: https://delvingbitcoin.org/t/asynchronous-pipeline-consensus-decoupling-mining-from-full-block-validation/2906

## Claim
Proposal decouples mining initiation from full-block validation: miners may start on n+1 after compact-block verification, full block n is delayed, and validity is declared later at n+k. Author reports a simulation with 10 MB blocks / 600 s targeting ~66.7 TPS without changing mining frequency.

## Decision relevance
Conceptually relevant to PoW scaling and to our broader separation of fast speculative routing from delayed authoritative settlement.

## Negative feasibility finding
Not yet strong enough for an Opportunity Card or candidate Issue. At scout time the primary discussion is one day old, has no substantive peer replies in the retrieved evidence, and the headline throughput comes from the proposer’s simulation. The delayed-validity mechanism changes consensus/security semantics enough that implementation interest would be premature without adversarial analysis of invalid-block withholding, reorg incentives, miner coordination, bandwidth assumptions, and compatibility with Bitcoin’s validation model.

## Smallest falsification before promotion
Wait for technical review or an independent model. Promote only if a credible analysis shows that deferred full validation does not create an exploitable period in which miners build significant work on invalid ancestry, or quantifies that risk under realistic adversarial/network assumptions.

## Why now
Fresh protocol-design idea (2026-09-22), but evidence uncertainty currently dominates option value.

No CLAIM, no mailbox work, no runner, no Codex/Work allocation.
