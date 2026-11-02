# VHP-01 — Venture Hackathon Package Pitch Specification
**Status:** Canonical / Active  
**Version:** 1.0 (2026-11-02)  
**Ticket:** [MIN-59](https://linear.app/mindrock/issue/MIN-59/vhp-01-pitch-1500-symbols-executive-hook-formal-breakthrough-and)  
**Project:** [VHP-001 — Template Venture Product (Venture Hackathon Package)](https://linear.app/mindrock/project/vhp-001-template-venture-product-venture-hackathon-package-917a269b6636)  
**Repository:** `https://github.com/pashamango/minutta-rp-pr-cycle-lab.git`  
**Branch:** `minutta/min-59-vhp-01-pitch-1500-symbols-executive-hook-formal-breakthrough`  
**Authority:** Principal Pavel Cherkashin (`pavel@mindrock.capital`)

---

## 1. Executive Purpose & Constraints

The **VHP-01 Pitch Protocol** defines the high-impact, 90-second executive presentation standard for verifiable venture products. Pitching formal-methods and mathematically verified technology to investors, hackathon judges, and engineering leaders requires cutting through academic jargon while retaining ironclad proof integrity.

### Non-Negotiable Constraints:
1. **Symbol Cap ($\le$ 1,500 Symbols):** The total pitch document must not exceed 1,500 characters (including letters, numbers, punctuation, markdown syntax, and whitespace).
2. **Three Mandatory Sections:**
   - **Section 1: Executive Hook:** The catastrophic cost of the status quo, tangible market failure, and economic urgency.
   - **Section 2: Formal Breakthrough Statement:** The exact algebraic, logical, or architectural advance that eliminates the failure mode at the root.
   - **Section 3: Verification Receipt:** Immutable audit coordinates (repository, commit, proof engine, zero-sorry receipt, clean replay command).
3. **Machine Verifiability:** Every pitch must validate cleanly via `tools/verify-vhp-pitch` with a corresponding JSON receipt.

---

## 2. Structural Schema

```markdown
# [Project Name]: [One-Line Subtitle]

## 1. Executive Hook
[Problem statement: financial losses, software panics, or security vulnerabilities caused by the status quo. 250-400 chars.]

## 2. Formal Breakthrough
[Mathematical / algorithmic breakthrough: formalization, totalization, verified theorem proving, zero-panic guarantee. 400-600 chars.]

## 3. Verification Receipt
- **Target Engine / Toolchain:** [e.g., Python 3.10+ Wheel Property Engine & AST Auditor]
- **Axiom Audit:** [e.g., 8/8 Carlström wheel properties verified on 7-element domain (1,190 checks)]
- **Repository:** `[canonical git URL]`
- **Commit SHA:** `[Immutable 40/64 hex char commit hash, e.g. 511565cc3c68e51ad616726579b9f613399038cd]`
- **Replay Command:** `[one-line clean execution command]`
```

---

## 3. Verification & Compliance Gate

A pitch is certified under VHP-01 if and only if:
- `tools/verify-vhp-pitch verify <pitch-file>` returns exit code `0`.
- Character count is strictly $\le$ 1,500.
- All three canonical headers are present in order.
- The verification receipt contains valid, non-placeholder coordinates.
