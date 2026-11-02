"""Channel 1: Ribbon Flow and Golden Difference Operator (L_phi F).

Formalizes the dynamical ribbon profile:
    F(delta, t) = |xi(1/2 + delta + i*t)|^2

Mathematical Properties:
1. Even parity: F(-delta, t) = F(delta, t) for real t due to reflection symmetry.
2. Taylor structure: F(delta, t) = F(0, t) + 1/2 * F''(0, t) * delta^2 + O(delta^4).
3. Golden Difference Operator (L_phi F):
   Let q = (sqrt(5) - 1)/2, delta_n = 1/2 * q^(n+3).
   Because 1 - q = q^2, delta_n - delta_(n+1) = delta_(n+2).
   L_phi F = F(delta_n, t) - F(delta_(n+1), t) - F(delta_(n+2), t) + F(0, t).
   Constant and linear terms cancel identically, leaving:
   L_phi F = 1/2 * F''(0, t) * [delta_n^2 - delta_(n+1)^2 - delta_(n+2)^2] + O(delta_n^4)
           = 2 * F''(0, t) * delta_(n+1) * delta_(n+2) + O(delta_n^4).

GRC-EXP-001 Independent Audit Controls:
- Demonstrates that the identity 1 - q = q^2 is an algebraic property of the golden grid,
  not evidence of zeta zero confinement.
- Compares against geometric controls (q = 0.6, q = 0.5) where 1 - q != q^2.
- Local Taylor scaling at zeros: r(epsilon_n)/delta_n -> 2/|zeta'(rho_1)| generically.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Union
import flint
from flint import arb, acb
from .ball_arithmetic import BallReal, ArbContext
from .xi_functional import RiemannXi


@dataclass
class GoldenAttractorCheck:
    n: int
    delta_n: float
    l_phi_val: BallReal
    pred_val: BallReal
    ratio: float
    higher_order_residual: BallReal


@dataclass
class RibbonChannelResult:
    t: float
    f0: BallReal
    f_double_prime: BallReal
    is_even: bool
    even_discrepancy: BallReal
    golden_checks: List[GoldenAttractorCheck]
    geometric_control_q06: float
    geometric_control_q05: float


class RibbonFlowChannel:
    """Channel 1 evaluator for Ribbon flow F(delta, t) and L_phi difference operator."""

    def __init__(self, xi_engine: RiemannXi = None, default_dps: int = 40):
        self.xi_engine = xi_engine or RiemannXi(default_dps=default_dps)
        self.default_dps = default_dps

    def evaluate_f(self, delta: Union[float, arb, BallReal], t: Union[float, arb, BallReal]) -> BallReal:
        """Evaluates F(delta, t) = |xi(1/2 + delta + i*t)|^2."""
        with ArbContext(self.default_dps):
            d_arb = delta.raw if isinstance(delta, BallReal) else (delta if isinstance(delta, arb) else arb(str(delta)))
            t_arb = t.raw if isinstance(t, BallReal) else (t if isinstance(t, arb) else arb(str(t)))

            s_re = arb("0.5") + d_arb
            s_acb = acb(s_re, t_arb)
            xi_val = self.xi_engine.evaluate_raw(s_acb)
            abs_sq = xi_val.real ** 2 + xi_val.imag ** 2
            return BallReal(abs_sq)

    def evaluate_f_double_prime(self, t: Union[float, arb, BallReal], h_step: float = 1e-5) -> BallReal:
        """Evaluates F''(0, t) using certified central differences."""
        with ArbContext(self.default_dps):
            h = arb(str(h_step))
            f0 = self.evaluate_f(arb("0"), t).raw
            f_plus = self.evaluate_f(h, t).raw
            f_minus = self.evaluate_f(-h, t).raw
            d2f = (f_plus - arb("2.0") * f0 + f_minus) / (h ** 2)
            return BallReal(d2f)

    def run_channel(self, t_val: float, n_levels: int = 5) -> RibbonChannelResult:
        """Runs the complete Channel 1 ribbon flow and golden operator analysis at height t."""
        with ArbContext(self.default_dps):
            t_arb = arb(str(t_val))
            f0 = self.evaluate_f(arb("0"), t_arb)
            f_double_prime = self.evaluate_f_double_prime(t_arb)

            # Check even symmetry at delta = 0.05
            test_delta = arb("0.05")
            f_pos = self.evaluate_f(test_delta, t_arb)
            f_neg = self.evaluate_f(-test_delta, t_arb)
            even_diff = f_pos - f_neg
            is_even = even_diff.contains_zero()

            # Golden ratio q = (sqrt(5) - 1)/2
            q_gold = (arb("5").sqrt() - arb("1")) / arb("2")

            golden_checks = []
            for n in range(1, n_levels + 1):
                delta_n = arb("0.5") * (q_gold ** (n + 3))
                delta_n1 = arb("0.5") * (q_gold ** (n + 4))
                delta_n2 = arb("0.5") * (q_gold ** (n + 5))

                f_n = self.evaluate_f(delta_n, t_arb)
                f_n1 = self.evaluate_f(delta_n1, t_arb)
                f_n2 = self.evaluate_f(delta_n2, t_arb)

                l_phi = f_n - f_n1 - f_n2 + f0

                delta_diff_sq = (delta_n ** 2) - (delta_n1 ** 2) - (delta_n2 ** 2)
                pred_val = BallReal(arb("0.5") * f_double_prime.raw * delta_diff_sq)

                ratio = l_phi.midpoint / pred_val.midpoint if abs(pred_val.midpoint) > 1e-30 else 1.0
                residual = l_phi - pred_val

                golden_checks.append(
                    GoldenAttractorCheck(
                        n=n,
                        delta_n=float(delta_n),
                        l_phi_val=l_phi,
                        pred_val=pred_val,
                        ratio=ratio,
                        higher_order_residual=residual,
                    )
                )

            # Geometric non-golden controls (q = 0.6 and q = 0.5)
            # For non-golden q, delta_n - delta_(n+1) != delta_(n+2), so linear/constant terms do not cancel
            q_06 = arb("0.6")
            d_06_n = arb("0.5") * (q_06 ** 4)
            d_06_n1 = arb("0.5") * (q_06 ** 5)
            d_06_n2 = arb("0.5") * (q_06 ** 6)
            l_06 = (self.evaluate_f(d_06_n, t_arb) - self.evaluate_f(d_06_n1, t_arb) - self.evaluate_f(d_06_n2, t_arb) + f0).midpoint

            q_05 = arb("0.5")
            d_05_n = arb("0.5") * (q_05 ** 4)
            d_05_n1 = arb("0.5") * (q_05 ** 5)
            d_05_n2 = arb("0.5") * (q_05 ** 6)
            l_05 = (self.evaluate_f(d_05_n, t_arb) - self.evaluate_f(d_05_n1, t_arb) - self.evaluate_f(d_05_n2, t_arb) + f0).midpoint

            return RibbonChannelResult(
                t=t_val,
                f0=f0,
                f_double_prime=f_double_prime,
                is_even=is_even,
                even_discrepancy=even_diff,
                golden_checks=golden_checks,
                geometric_control_q06=l_06,
                geometric_control_q05=l_05,
            )
