# AMDE-NUM: Arb Ball-Arithmetic Specification for $\xi(s)$

**Linear Ticket**: `MIN-88`  
**PRD Specification**: [`PRD-28 (amde-num-certified-numerics-arb-three-channel-experiment)`](https://linear.app/mindrock/issue/PRD-28/amde-num-certified-numerics-arb-three-channel-experiment)  
**Author**: `agy@wolfram`  
**Reviewer**: `Muse`  
**Status**: Canonical / Active  

---

## 1. Problem Statement & Motivation

Ordinary IEEE 754 floating-point numbers (`float64`) are intrinsically incapable of certifying proof claims in analytic number theory:
1. **Unbounded Roundoff Error**: Standard float approximations cannot distinguish between an actual zero and numerical roundoff noise ($|\hat{f}(x)| < 10^{-15}$ may merely reflect precision limits).
2. **Catastrophic Cancellation**: Computing difference operators like $L_\phi F$ or higher-order derivatives suffers from catastrophic cancellation when subtracting nearly equal floating-point values.
3. **Poles and Removable Singularities**: The Riemann zeta function $\zeta(s)$ has a simple pole at $s = 1$, causing naive evaluation of $\xi(s) = \frac{1}{2} s (s-1) \pi^{-s/2} \Gamma(s/2) \zeta(s)$ to encounter division by zero or NaN.

To satisfy the acceptance criteria of **PRD-28 / RP-002**, numerical evaluations must be **rigorously certified** using arbitrary-precision ball arithmetic (Arb/FLINT), providing proven interval enclosures $[m \pm r]$ where $m$ is the midpoint and $r$ is an absolute upper bound on the error radius.

---

## 2. Mathematical Definition & Analytic Regularization

### 2.1 The Riemann $\xi$-Functional
The completed Riemann $\xi$ function is an entire function on $\mathbb{C}$ defined by:
$$\xi(s) = \frac{1}{2} s (s - 1) \pi^{-s/2} \Gamma(s/2) \zeta(s)$$

It satisfies the exact functional equation:
$$\xi(s) = \xi(1 - s)$$

On the critical line $s = 1/2 + it$, the function $\Xi(t) = \xi(1/2 + it)$ is strictly real-valued for all $t \in \mathbb{R}$.

### 2.2 Pole Cancellation and Regularization around $s = 1$ and $s = 0$
Direct evaluation of $(s-1)\zeta(s)$ near $s=1$ is regularized analytically using reflection symmetry:
$$\xi(s) = \xi(1 - s)$$
Setting $w = s - 1$ (so $s = 1 + w$ and $1 - s = -w$):
$$\xi(1 + w) = \xi(-w) = \frac{1}{2} (-w) (-w - 1) \pi^{w/2} \Gamma(-w/2) \zeta(-w)$$

Using the recurrence relation $z \Gamma(z) = \Gamma(z + 1)$:
$$\left( -\frac{w}{2} \right) \Gamma\left( -\frac{w}{2} \right) = \Gamma\left( 1 - \frac{w}{2} \right)$$
$$\implies (-w) \Gamma\left( -\frac{w}{2} \right) = 2 \Gamma\left( 1 - \frac{w}{2} \right)$$

Substituting back:
$$\xi(1 + w) = (w + 1) \cdot \Gamma\left( 1 - \frac{w}{2} \right) \cdot \pi^{w/2} \cdot \left( -\zeta(-w) \right)$$

Since $\Gamma(1) = 1$ and $\zeta(0) = -1/2$, as $w \to 0$:
$$\xi(1) = (1) \cdot (1) \cdot (1) \cdot \left( -(-1/2) \right) = \frac{1}{2}$$

This exact formula is holomorphic in the entire disc $|w| < 1$, completely eliminating the pole at $s=1$ and producing certified balls of arbitrary precision with zero numerical cancellation.

---

## 3. Ball Arithmetic Implementation (Arb/FLINT)

The harness wraps the C library FLINT 3.x / Arb via `python-flint 0.9.0`:
* Real balls: `flint.arb` represented as $[m \pm r]$.
* Complex balls: `flint.acb` represented as $[m_{re} \pm r_{re}] + i [m_{im} \pm r_{im}]$.
* Formal power series: `flint.acb_series` for Taylor expansions and high-order derivatives.

### Certified Operators:
1. `RiemannXi.evaluate(s_re, s_im)`: Evaluates $\xi(s)$ and returns certified `BallComplex`.
2. `RiemannXi.evaluate_xi_on_critical_line(t)`: Evaluates $\Xi(t)$, asserting $\text{Im}(\Xi(t)) = 0$.
3. `RiemannXi.evaluate_derivative(s)`: Certified $d\xi/ds$.
4. `RiemannXi.evaluate_log_derivative(s)`: Certified $\frac{\xi'(s)}{\xi(s)}$.

---

## 4. Acceptance Criteria & Audit Verification

| Test Gate | Acceptance Benchmark | Status |
|---|---|---|
| **A1: Removable Singularities** | $\xi(0) \in [0.5 \pm 10^{-35}]$, $\xi(1) \in [0.5 \pm 10^{-35}]$ | **PASS** |
| **A2: Exact Values** | $\xi(2) \in [\pi/6 \pm 10^{-35}]$ | **PASS** |
| **A3: Functional Symmetry** | $0 \in \xi(s) - \xi(1-s)$ across all test coordinates | **PASS** |
| **A4: Non-trivial Zeros** | $0 \in \xi(1/2 + i \gamma_k)$ for $\gamma_1, \gamma_2, \gamma_3$ | **PASS** |
| **A5: Precision Scalability** | Configurable up to 100+ decimal digits | **PASS** |
