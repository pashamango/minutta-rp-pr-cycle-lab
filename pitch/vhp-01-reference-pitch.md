# WheelCore: Crash-Proof Arithmetic for Autonomous Systems

## 1. Executive Hook
Singular arithmetic crashes cost industry billions—from Ariane 5 guidance failures to smart contract drain attacks and autonomous vehicle sensor disengagements caused by division-by-zero panics. Classical software relies on defensive null-checks, fragile exception cascades, and IEEE 754 NaN contamination that silently poisons downstream control loops.

## 2. Formal Breakthrough
WheelCore eliminates arithmetic singularity at the foundation by formalizing Carlström Wheel Theory ($\mathbb{W}(\mathbb{Q})$) in Lean 4. Division is totalized ($1/0 = \infty$, $0/0 = \bot$) alongside an involutive reciprocal ($//x = x$) and regularized distributivity ($(x+y)z + 0z = xz + yz$). Singularities become first-class algebraic values with strictly sound propagation, mathematically preventing division panics without sacrificing equational reasoning. Built with 0 sorry and 0 unreviewed axioms.

## 3. Verification Receipt
- **Proof Engine:** Lean 4 v4.15.0 & Python 3.10+ Wheel Verifier
- **Axiom Audit:** 0 unreviewed axioms | 0 sorry | 0 admit
- **Repository:** `https://github.com/pashamango/minutta-rp-pr-cycle-lab.git`
- **Commit SHA:** `6095350f2b0d3edad7179e519ee4d5775ab3ce91`
- **Verification Command:** `python3 tools/verify-vhp-pitch verify pitch/vhp-01-reference-pitch.md`
