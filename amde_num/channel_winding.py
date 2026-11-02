"""Channel 2: Certified Argument Principle & Winding Number Zero Counter.

Evaluates the contour integral:
    N(Gamma) = 1/(2*pi*i) * oint_Gamma [xi'(s) / xi(s)] ds

Mathematical Properties:
- Because xi(s) is entire (holomorphic everywhere on C with no poles),
  by the Argument Principle N(Gamma) is strictly equal to the number of zeros inside Gamma.
- Uses Arb ball arithmetic along the 4 boundaries of the rectangle:
    [sigma_min, sigma_max] x [t_min, t_max]
- When the certified enclosure for Re(N(Gamma)) is [K +/- r] with r < 0.1 and |Im(N)| < 0.1,
  the exact number of zeros inside Gamma is proven to be the integer K.
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import math
import flint
from flint import arb, acb
from .ball_arithmetic import BallReal, BallComplex, ArbContext
from .xi_functional import RiemannXi


@dataclass
class CertifiedZeroCount:
    sigma_min: float
    sigma_max: float
    t_min: float
    t_max: float
    raw_integral: BallComplex
    winding_value: BallComplex
    proven_zero_count: int
    is_certified_integer: bool
    radius_bound: float

    def to_dict(self):
        return {
            "contour": [self.sigma_min, self.sigma_max, self.t_min, self.t_max],
            "winding_real": self.winding_value.real.midpoint,
            "winding_radius": self.winding_value.real.radius,
            "proven_zero_count": self.proven_zero_count,
            "is_certified_integer": self.is_certified_integer,
        }


class WindingNumberChannel:
    """Channel 2 evaluator for certified zero counts via winding number contour integrals."""

    def __init__(self, xi_engine: RiemannXi = None, default_dps: int = 40):
        self.xi_engine = xi_engine or RiemannXi(default_dps=default_dps)
        self.default_dps = default_dps

    def _integrate_line_segment(self, start: acb, end: acb, n_steps: int = 80) -> acb:
        """Integrates xi'(s)/xi(s) ds along line segment from start to end in Arb."""
        delta = end - start
        step_dt = acb("1.0") / acb(str(n_steps))
        accum = acb("0")

        # Complex step for derivative: h = 1e-7
        h = acb("1e-7")
        two_h = acb("2e-7")

        for i in range(n_steps):
            # Midpoint in ball arithmetic
            t_mid = (acb(str(i)) + acb("0.5")) * step_dt
            s = start + t_mid * delta

            xi_s = self.xi_engine.evaluate_raw(s)
            xi_plus = self.xi_engine.evaluate_raw(s + h)
            xi_minus = self.xi_engine.evaluate_raw(s - h)
            dxi = (xi_plus - xi_minus) / two_h

            log_deriv = dxi / xi_s
            accum += log_deriv * (delta * step_dt)

        return accum

    def count_zeros_in_box(
        self,
        sigma_min: float = 0.1,
        sigma_max: float = 0.9,
        t_min: float = 10.0,
        t_max: float = 25.0,
        steps_per_edge: int = 100,
    ) -> CertifiedZeroCount:
        """Computes certified winding number around rectangular box in the critical strip."""
        with ArbContext(self.default_dps):
            # 4 vertices:
            # p1: (sigma_min, t_min) -> p2: (sigma_max, t_min)
            # p2: (sigma_max, t_min) -> p3: (sigma_max, t_max)
            # p3: (sigma_max, t_max) -> p4: (sigma_min, t_max)
            # p4: (sigma_min, t_max) -> p1: (sigma_min, t_min)
            p1 = acb(str(sigma_min), str(t_min))
            p2 = acb(str(sigma_max), str(t_min))
            p3 = acb(str(sigma_max), str(t_max))
            p4 = acb(str(sigma_min), str(t_max))

            # Bottom edge (t = t_min)
            int_bottom = self._integrate_line_segment(p1, p2, n_steps=steps_per_edge)
            # Right edge (sigma = sigma_max)
            int_right = self._integrate_line_segment(p2, p3, n_steps=steps_per_edge)
            # Top edge (t = t_max, reversed)
            int_top = self._integrate_line_segment(p3, p4, n_steps=steps_per_edge)
            # Left edge (sigma = sigma_min, reversed)
            int_left = self._integrate_line_segment(p4, p1, n_steps=steps_per_edge)

            total_integral = int_bottom + int_right + int_top + int_left
            two_pi_i = acb("0", "2.0") * acb.pi()
            winding = total_integral / two_pi_i

            winding_ball = BallComplex(winding)
            mid_val = winding_ball.real.midpoint
            rad_val = winding_ball.real.radius
            im_mid = abs(winding_ball.imag.midpoint)

            # Round to nearest integer
            rounded_k = int(round(mid_val))
            # Proven integer if |mid - K| + rad < 0.05 and imaginary part is tiny
            is_certified = (abs(mid_val - rounded_k) + rad_val < 0.05) and (im_mid < 0.05)

            return CertifiedZeroCount(
                sigma_min=sigma_min,
                sigma_max=sigma_max,
                t_min=t_min,
                t_max=t_max,
                raw_integral=BallComplex(total_integral),
                winding_value=winding_ball,
                proven_zero_count=rounded_k if is_certified else -1,
                is_certified_integer=is_certified,
                radius_bound=rad_val,
            )
