# VHP-02 — Scientific Paper Specification & arXiv Submission Protocol
**Status:** Canonical / Active  
**Version:** 1.0 (2026-11-02)  
**Ticket:** [MIN-60](https://linear.app/mindrock/issue/MIN-60/vhp-02-scientific-paper-arxiv-style-conditional-theorems-countermodels)  
**Project:** [VHP-001 — Template Venture Product (Venture Hackathon Package)](https://linear.app/mindrock/project/vhp-001-template-venture-product-venture-hackathon-package-917a269b6636)  
**Repository:** `https://github.com/pashamango/minutta-rp-pr-cycle-lab.git`  
**Branch:** `minutta/min-60-vhp-02-scientific-paper-arxiv-style-conditional-theorems`  
**Authority:** Principal Pavel Cherkashin (`pavel@mindrock.capital`)

---

## 1. Executive Summary & Purpose

The **VHP-02 Scientific Paper Protocol** establishes the canonical, peer-review-grade, arXiv-ready scientific publication standard for all ventures developed within the Venture Hackathon Package (VHP-001) ecosystem.

In classical scientific preprints, claims often blur the boundary between established theorems, conditional hypotheses, and unproved conjectures. Furthermore, boundary failures and domain limits are frequently obscured or omitted.

VHP-02 enforces three non-negotiable structural disciplines:
1. **The Axiom Ledger:** Every foundational axiom, algebraic postulate, and conjectural premise must be enumerated in an explicit, immutable ledger. No implicit axioms, unreviewed assumptions, or `sorry`/`admit` escape hatches are permitted.
2. **Conditional Theorems:** Claims whose truth depends on specific premises must explicitly cite their minimal supporting axiom subset in the theorem header and statement.
3. **Countermodels & Boundary Falsification:** Naive classical generalizations must be constructively refuted with explicit, step-by-step witnesses (e.g. singular valuation tables and falsification proofs).
4. **Machine-Readable Traceability:** Every formal statement in the paper maps to an entry in `claims_traceability_matrix.json`, pointing to an immutable code artifact, verification command, and replay receipt.

---

## 2. Directory & Artifact Layout

```text
worktrees/MIN-60-VHP-PAPER-0001/
├── docs/
│   └── VHP_02_SCIENTIFIC_PAPER_SPEC.md      <- Canonical specification (this document)
├── paper/
│   ├── vhp-02-arxiv-template.tex            <- Universal arXiv LaTeX template
│   ├── vhp-02-reference-paper.tex           <- Concrete reference paper (Carlström Wheel Theory)
│   └── artifacts/
│       ├── axiom_ledger.json                <- Machine-readable 8-axiom ledger
│       ├── countermodels.json               <- 4 constructive falsification witnesses
│       ├── claims_traceability_matrix.json   <- Bi-directional claim-to-artifact mapping
│       └── vhp_paper_verification_receipt.json <- Cryptographic verification receipt
├── tools/
│   └── verify-vhp-paper                     <- Standalone Python verification suite
├── tests/
│   └── test_vhp_paper.py                    <- Automated unit test suite (100% pass)
└── codex-insights/
    └── 2026-11-02-min60-vhp-paper-arxiv-style.md <- Codex insight handoff record
```

---

## 3. The Axiom Ledger Protocol

The Axiom Ledger (`paper/artifacts/axiom_ledger.json`) classifies all assertions into three disjoint categories:

| Category | Definition | Kernel / Audit Obligation |
|---|---|---|
| **FOUNDATIONAL** | Logical rules of inference and equality axioms of the proof assistant kernel. | Lean 4 / Coq / HOL Kernel checked. |
| **DOMAIN_ALGEBRAIC** | Postulates defining the algebraic structure (e.g., commutativity, associativity, involution of reciprocal, regularized distributivity). | Formally stated and audited for mutual independence and consistency. |
| **CONJECTURAL** | High-level conjectures or empirical assumptions. | Explicitly declared; any theorem relying on them is marked `Conditional Theorem`. |

### Reference Wheel Ledger ($\W(\Q)$)
In the reference paper (`vhp-02-reference-paper.tex`), 8 axioms are formalized:
- `AXM-W01`: Addition Commutativity ($\forall x, y: x + y = y + x$)
- `AXM-W02`: Addition Associativity ($\forall x, y, z: (x + y) + z = x + (y + z)$)
- `AXM-W03`: Multiplication Commutativity ($\forall x, y: x \cdot y = y \cdot x$)
- `AXM-W04`: Multiplication Associativity ($\forall x, y, z: (x \cdot y) \cdot z = x \cdot (y \cdot z)$)
- `AXM-W05`: Reciprocal Involution ($\forall x: /(/x) = x$)
- `AXM-W06`: Product Reciprocal ($\forall x, y: /(x \cdot y) = /x \cdot /y$)
- `AXM-W07`: Regularized Distributivity ($(x + y)z + 0z = xz + yz$)
- `AXM-W08`: Negation Regularization ($x - x = 0x$)

---

## 4. Conditional Theorems Discipline

Every formal deduction is presented within a structured `claimbox` environment in LaTeX:

```latex
\begin{claimbox}{Conditional Theorem \ref{thm:recip-invol}: Involutive Totality of Reciprocals}
\begin{conditionaltheorem}[Dependent on Axiom AXM-W05]
\label{thm:recip-invol}
For all elements $x \in \W(\Q)$, including the singular values $\inft$ and $\bott$, the double reciprocal operation is an unconditional identity:
\begin{equation}
/(/x) = x.
\end{equation}
\end{conditionaltheorem}
\end{claimbox}
```

Rules:
1. **Header Attribution:** The brackets immediately following `\begin{conditionaltheorem}` must cite the exact Axiom IDs from the ledger.
2. **Proof Boundary:** The proof must demonstrate step-by-step derivation without invoking unlisted axioms.

---

## 5. Countermodels & Boundary Falsification Standards

Discovering where an algebraic or empirical property breaks is a primary scientific deliverable. Countermodels are typeset in a distinct `counterbox` and catalogued in `paper/artifacts/countermodels.json`.

Four canonical countermodels are verified:
1. **CM-01 (Zero Annihilation Falsified):**
   - Property: $\forall x, 0 \cdot x = 0$.
   - Witness: $x = \inft \equiv (1, 0)$.
   - Evaluation: $0 \cdot \inft = (0, 1) \cdot (1, 0) = (0, 0) = \bott \neq 0$.
2. **CM-02 (Additive Inverse Falsified):**
   - Property: $\forall x, x - x = 0$.
   - Witness: $x = \inft \equiv (1, 0)$.
   - Evaluation: $\inft - \inft = (1, 0) + (-1, 0) = (0, 0) = \bott \neq 0$.
3. **CM-03 (Classical Distributivity Falsified):**
   - Property: $\forall x, y, z: (x+y)z = xz + yz$.
   - Witness: $x = 1, y = 1, z = \inft$.
   - Evaluation: LHS $= (1+1)\inft = 2\inft = \inft$; RHS $= 1\inft + 1\inft = \inft + \inft = \bott$. Since $\inft \neq \bott$, classical distributivity fails. Regularization $(x+y)z + 0z = xz + yz$ restores equality by regularizing both sides to $\bott$.
4. **CM-04 (Universal Multiplicative Inverse Falsified):**
   - Property: $\forall x, x \cdot (/x) = 1$.
   - Witness: $x = 0$.
   - Evaluation: $0 \cdot (/0) = 0 \cdot \inft = \bott \neq 1$.

---

## 6. End-to-End Verification Tooling

The verification suite `tools/verify-vhp-paper` executes without network or third-party dependencies:

```bash
python3 tools/verify-vhp-paper verify
```

The tool executes 5 independent stages:
1. **LaTeX Syntax & Environment Integrity:** Validates balanced environments, macro consistency, and presence of mandatory structural sections.
2. **Axiom Ledger Validation:** Asserts presence, categorization, 64-character SHA256 integrity, and zero unreviewed axioms.
3. **Symbolic Countermodels Engine:** Implements exact projective fraction-pair arithmetic and evaluates each witness step-by-step.
4. **Claims Traceability Verification:** Checks 100% bidirectional correspondence between LaTeX `\label{...}` references, JSON entries, and artifact files.
5. **Cryptographic Receipt Emission:** Records an immutable audit log to `paper/artifacts/vhp_paper_verification_receipt.json`.

---

## 7. Independent Verification & Clean Replay

In accordance with Section 6 of AGENTS.md, any independent verifier (including QA agent Codex or Principal Pavel Cherkashin) can reproduce the verification in an isolated environment:

```bash
# 1. Clean checkout from remote origin
git clone --branch minutta/min-60-vhp-02-scientific-paper-arxiv-style-conditional-theorems \
  https://github.com/pashamango/minutta-rp-pr-cycle-lab.git verify-box
cd verify-box

# 2. Run the paper and claims verification suite
python3 tools/verify-vhp-paper verify

# 3. Run regression unit tests
python3 -m unittest tests/test_vhp_paper.py
```
