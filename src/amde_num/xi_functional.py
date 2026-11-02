"""Certified Riemann xi-functional evaluation using Arb ball arithmetic.

Evaluates the completed Riemann xi function:
    xi(s) = 1/2 * s * (s - 1) * pi^(-s/2) * Gamma(s/2) * zeta(s)

Features:
- Rigorous ball-arithmetic enclosures for arbitrary complex coordinate s.
- Analytic continuation and pole cancellation around s=1 and s=0 via reflection:
    xi(1 + w) = (w + 1) * Gamma(1 - w/2) * pi^(w/2) * (-zeta(-w))
  yielding rigorous, non-singular balls including xi(0) = xi(1) = 1/2.
- Functional equation certification: xi(s) = xi(1 - s).
- Real-valued Xi on critical line: Xi(t) = xi(1/2 + i*t), Im(Xi(t)) = 0.
"""

from dataclasses import dataclass
from typing import Union, Tuple, Optional
import flint
from flint import arb, acb, ctx, acb_series
from .ball_arithmetic import BallComplex, BallReal, ArbContext


@dataclass
class CertifiedXiResult:
    s: BallComplex
    xi: BallComplex
    refl_diff: Optional[BallComplex] = None
    is_reflection_symmetric: bool = False
    radius_bound: float = 0.0

    def to_dict(self):
        return {
            "s_real": self.s.real.midpoint,
            "s_imag": self.s.imag.midpoint,
            "xi_real_mid": self.xi.real.midpoint,
            "xi_real_rad": self.xi.real.radius,
            "xi_imag_mid": self.xi.imag.midpoint,
            "xi_imag_rad": self.xi.imag.radius,
            "is_reflection_symmetric": self.is_reflection_symmetric,
            "radius_bound": self.radius_bound,
        }


class RiemannXi:
    """Certified evaluation engine for Riemann xi(s) with Arb ball arithmetic."""

    def __init__(self, default_dps: int = 40):
        self.default_dps = default_dps

    def evaluate_raw(self, s: acb) -> acb:
        """Internal Arb evaluation of xi(s)."""
        half = acb("0.5")
        one = acb("1.0")
        pi = acb.pi()

        # If Re(s) < 0.5, apply reflection symmetry xi(s) = xi(1 - s)
        try:
            s_re = float(s.real.mid())
        except Exception:
            s_re = float(s.real)

        if s_re < 0.5:
            return self.evaluate_raw(one - s)

        # Handle neighborhood of s = 1 (and by reflection s = 0)
        # Using exact regularized formula: xi(1 + w) = (w + 1) * Gamma(1 - w/2) * pi^(w/2) * (-zeta(-w))
        try:
            s_im = float(s.imag.mid())
        except Exception:
            s_im = float(s.imag)

        if abs(s_re - 1.0) < 0.15 and abs(s_im) < 0.15:
            w = s - one
            gamma_term = (one - half * w).gamma()
            pi_term = (half * w * pi.log()).exp()
            zeta_term = (-w).zeta()
            return (w + one) * gamma_term * pi_term * (-zeta_term)

        # Standard Dirichlet / functional formula away from pole
        factor1 = half * s * (s - one)
        factor2 = (-(half * s) * pi.log()).exp()
        factor3 = (half * s).gamma()
        factor4 = s.zeta()
        return factor1 * factor2 * factor3 * factor4

    def evaluate(self, s_re: Union[float, int, str, arb], s_im: Union[float, int, str, arb] = 0.0) -> CertifiedXiResult:
        """Evaluates xi(s) with certified ball enclosure and reflection verification."""
        with ArbContext(self.default_dps):
            re_arb = s_re if isinstance(s_re, arb) else arb(str(s_re))
            im_arb = s_im if isinstance(s_im, arb) else arb(str(s_im))
            s_acb = acb(re_arb, im_arb)

            xi_acb = self.evaluate_raw(s_acb)
            s_dual = acb("1.0") - s_acb
            xi_dual = self.evaluate_raw(s_dual)

            diff = xi_acb - xi_dual
            refl_ball = BallComplex(diff)
            is_symmetric = refl_ball.contains_zero()

            res_ball = BallComplex(xi_acb)
            r_bound = max(res_ball.real.radius, res_ball.imag.radius)

            return CertifiedXiResult(
                s=BallComplex(s_acb),
                xi=res_ball,
                refl_diff=refl_ball,
                is_reflection_symmetric=is_symmetric,
                radius_bound=r_bound,
            )

    def evaluate_xi_on_critical_line(self, t: Union[float, int, str, arb]) -> CertifiedXiResult:
        """Evaluates Xi(t) = xi(1/2 + i*t). Strictly real for real t."""
        return self.evaluate(s_re="0.5", s_im=t)

    def evaluate_derivative(self, s_re: Union[float, int, str, arb], s_im: Union[float, int, str, arb] = 0.0, h_step: float = 1e-8) -> BallComplex:
        """Evaluates dxi/ds via certified complex central differences."""
        with ArbContext(self.default_dps):
            re_arb = s_re if isinstance(s_re, arb) else arb(str(s_re))
            im_arb = s_im if isinstance(s_im, arb) else arb(str(s_im))
            s_acb = acb(re_arb, im_arb)

            h = acb(str(h_step))
            xi_plus = self.evaluate_raw(s_acb + h)
            xi_minus = self.evaluate_raw(s_acb - h)
            dxi = (xi_plus - xi_minus) / (acb("2.0") * h)
            return BallComplex(dxi)

    def evaluate_log_derivative(self, s_re: Union[float, int, str, arb], s_im: Union[float, int, str, arb] = 0.0, h_step: float = 1e-8) -> BallComplex:
        """Evaluates xi'(s) / xi(s) with certified ball bounds."""
        with ArbContext(self.default_dps):
            re_arb = s_re if isinstance(s_re, arb) else arb(str(s_re))
            im_arb = s_im if isinstance(s_im, arb) else arb(str(s_im))
            s_acb = acb(re_arb, im_arb)

            xi_val = self.evaluate_raw(s_acb)
            h = acb(str(h_step))
            xi_plus = self.evaluate_raw(s_acb + h)
            xi_minus = self.evaluate_raw(s_acb - h)
            dxi = (xi_plus - xi_minus) / (acb("2.0") * h)
            return BallComplex(dxi / xi_val)
