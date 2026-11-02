# AMDE Interactive HTML/WASM Demos: Architecture & Type Specification

**Standard Reference**: `PRD-29` (amde-demo-interactive-htmlwasm-demos)  
**Parent Initiative**: `PRD-26` / `RP-002`  
**Sub-Issue**: `MIN-90` (WASM pipeline + critical-strip explorer)  
**Builder**: `agy` (Wolfram)  
**Reviewer**: `Muse`  
**Epistemic Standard**: Strict typed claims, zero visual theater, cryptographic receipts  

---

## 1. System Overview

The `amde-demo-wasm` package provides a 100% zero-server, in-browser mathematical computing engine compiled from Rust to `wasm32-unknown-unknown`. It visualizes and interactively validates two foundational components of the AMDE (Arithmetic Markov Dynamical Equations) RP-002 program:

1. **Critical-Strip Explorer**:
   - Analyzes the completed Riemann $\xi(s) = \frac{1}{2} s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)$ function across the critical strip $\operatorname{Re}(s) \in [0, 1]$.
   - Visualizes the nested golden ratio widths:
     $$G_n = \left\{ s \in \mathbb{C} : \left| \operatorname{Re}(s) - \frac{1}{2} \right| \le \delta_n \right\}, \quad \delta_n = \frac{1}{2}\phi^{n+3}$$
   - Explores the golden interval $G_0 = [0.381966, 0.618034]$ and the focus sub-band $[0.482, 0.618]$ around the central critical axis $\sigma = 1/2$.
   - Verifies the functional equation reflection symmetry $\xi(s) = \xi(1-s)$ with certified error bounds.
   - Plots the non-trivial zero crossings on the critical axis ($\gamma_1 \approx 14.135, \gamma_2 \approx 21.022, \dots$).

2. **Geoid Navigator**:
   - Visualizes the categorical 4-phase transformation loop:
     $$\text{FACTORIZE (ISO)} \longrightarrow \text{EVOLVE (APPROX)} \longrightarrow \text{CANONICALIZE (ADJOINT/LOSSY)} \longrightarrow \text{RECONSTRUCT (ISO)}$$
   - Computes prime valuation spectra $(p \mapsto v_p \ln p)$ and logarithmic heights $I(n) = \ln(n)$.
   - Evaluates dynamical operators (Syracuse, Collatz, Golden Contraction) and certifies orbit descent.
   - Truncates valuation vectors along Galois prime channels with quantitative information loss $\Delta I$.
   - Reconstructs natural numbers with exact inverse verification and cryptographic SHA-256 receipts.

---

## 2. Transformation Categories & Morphism Invariants

| Morphism Kind | Epistemic Status | Round-trip Discrepancy | Invariant Change $\Delta I$ | Metric Error $\epsilon$ | Example in Demos |
|:---|:---|:---:|:---:|:---:|:---|
| **`ISO`** | `THEOREM` | $\equiv 0$ | $\Delta I = 0$ | $\epsilon = 0$ | Factorize: $n \leftrightarrow \bigoplus_p \mathbb{N}$; Reconstruct |
| **`APPROXIMATE`** | `LEMMA_TARGET` / `EXPERIMENT` | Continuous | Drift $\Delta I \in \mathbb{R}$ | $\epsilon \le \tau$ | $\xi(s)$ evaluation; Syracuse dynamical step |
| **`ADJOINT`** | `FORMALIZATION` | Unit $\le$ Counit | $\Delta I \ge 0$ | $\epsilon = 0$ | Galois prime retract $\iota_K \circ \pi_K \le \text{id}$ |
| **`LOSSY`** | `FORMALIZATION` | Non-injective | $\Delta I > 0$ | $\epsilon = 0$ | Truncation to top $K$ primes; odd kernel extraction |

---

## 3. Cryptographic Receipt Schema

Every transformation produces a canonical RFC 6234 SHA-256 receipt:

```json
{
  "claim_id": "CLAIM-GEOID-FACT-840",
  "title": "Prime Factorization Isomorphism: N+ <-> (Primes ->0 N)",
  "transformation_kind": "ISO",
  "epistemic_status": "THEOREM",
  "source": "Natural Number n = 840",
  "target": "Valuation Profile [2^3 * 3 * 5 * 7]",
  "input": "n = 840",
  "output": "factors = 2^3 * 3 * 5 * 7",
  "delta_i": 0.0,
  "metric_error": 0.0,
  "tolerance": 0.0,
  "verified": true,
  "notes": "Exact bijective decomposition into prime valuation coordinates, Delta I = 0, epsilon = 0",
  "sha256": "4bdf16d0e7337740a734144210409fbf56a3fac2fc81adee645667fe8655a5a6"
}
```

---

## 4. Zero-Server Deployment & In-Browser Execution

The deployment requires **no backend server, no database, and no Node.js runtime in production**:
- The WASM module compiles to a standalone 108KB binary.
- A base64-encoded fallback inside `pkg/amde_demo_wasm.js` allows the demos to execute directly via `file:///` URLs in standard browsers where cross-origin local `fetch()` is restricted by browser security policies.
- When hosted on any HTTP/HTTPS server (e.g. GitHub Pages, static S3 bucket), the loader automatically selects streaming compilation for peak performance.
