# WheelCore: Crash-Proof Arithmetic for Autonomous Systems

## 1. Executive Hook
Singular arithmetic crashes cost industry billions—from Ariane 5 guidance failures to smart contract drain attacks and autonomous vehicle sensor disengagements caused by division-by-zero panics. Classical software relies on defensive null-checks, fragile exception cascades, and IEEE 754 NaN contamination that silently poisons downstream control loops.

## 2. Formal Breakthrough
WheelCore eliminates arithmetic singularities by formalizing Carlström Wheel Theory ($\mathbb{W}(\mathbb{Q})$) via totalized algebra. Division is totalized ($1/0 = \infty$, $0/0 = \bot$) alongside an involutive reciprocal ($//x = x$) and regularized distributivity ($(x+y)z + 0z = xz + yz$). Singularities become first-class algebraic values with sound propagation, preventing division panics without sacrificing equational reasoning. Validated via 8 Carlström wheel properties on a 7-element representative domain ($0, 1, -1, 2/3, -5/7, \infty, \bot$) spanning 1,190 sample checks.

## 3. Verification Receipt
- **Proof Engine:** Python 3.10+ Wheel Property Engine & AST Auditor
- **Axiom Audit:** 8/8 Carlström wheel properties verified on 7-element domain (1,190 checks)
- **Repository:** `https://github.com/pashamango/minutta-rp-pr-cycle-lab.git`
- **Commit SHA:** `511565cc3c68e51ad616726579b9f613399038cd`
- **Verification Command:** `python3 tools/verify-vhp-pitch verify pitch/vhp-01-reference-pitch.md`
