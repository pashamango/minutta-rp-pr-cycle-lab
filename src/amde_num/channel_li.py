"""Channel 3: Certified Finite Li Coefficients (lambda_1 .. lambda_N).

Formalizes Keiper-Li coefficients:
    lambda_n = 1/(n-1)! * d^n/ds^n [s^(n-1) * ln xi(s)] |_{s=1}
             = sum_rho [1 - (1 - 1/rho)^n]

Li's Criterion (1997):
    The Riemann Hypothesis is equivalent to the statement that lambda_n > 0 for all integers n >= 1.

Arb Ball-Arithmetic Implementation:
- Let w = s - 1. We expand around w = 0 using acb_series.
- By reflection symmetry:
    xi(1 + w) = (w + 1) * Gamma(1 - w/2) * pi^(w/2) * (-zeta(-w))
- Compute ln xi(1 + w) as a formal power series in Arb.
- For each order n:
    g(w) = (1 + w)^(n-1) * ln xi(1 + w)
    lambda_n = n * [w^n] g(w)
- Validates rigorous positivity: lower bound of lambda_n > 0.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import flint
from flint import arb, acb, acb_series, ctx
from .ball_arithmetic import BallReal, ArbContext


@dataclass
class SingleLiCoefficient:
    n: int
    val: BallReal
    is_strictly_positive: bool
    lower_bound: float
    upper_bound: float

    def to_dict(self):
        return {
            "n": self.n,
            "midpoint": self.val.midpoint,
            "radius": self.val.radius,
            "is_strictly_positive": self.is_strictly_positive,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
        }


@dataclass
class CertifiedLiCoefficients:
    max_order: int
    coefficients: List[SingleLiCoefficient]
    all_positive: bool


class LiCoefficientChannel:
    """Channel 3 evaluator for certified Li coefficients using Arb power series."""

    def __init__(self, default_dps: int = 50):
        self.default_dps = default_dps

    def compute_coefficients(self, max_n: int = 15) -> CertifiedLiCoefficients:
        """Computes certified Li coefficients lambda_1 through lambda_max_n."""
        with ArbContext(self.default_dps, cap=max_n + 5):
            # Formal parameter w
            # Set series cap
            cap_len = max_n + 5
            ctx.cap = cap_len
            w = acb_series([0, 1])
            half = acb("0.5")
            one = acb("1.0")
            pi = acb.pi()

            # Regularized xi(1 + w) series:
            # xi(1+w) = (w + 1) * Gamma(1 - w/2) * exp(w/2 * ln pi) * (-zeta(-w))
            poly_term = w + one
            gamma_term = (one - half * w).gamma()
            pi_term = (half * w * pi.log()).exp()
            zeta_term = (-w).zeta()

            xi_series = poly_term * gamma_term * pi_term * (-zeta_term)

            # ln xi(1 + w)
            # Normalize by xi(1) = 0.5 to keep series constant term 1, then add ln(0.5)
            norm_xi = xi_series / half
            ln_xi = norm_xi.log() + half.log()

            results = []
            all_pos = True

            for n in range(1, max_n + 1):
                poly_factor = (one + w) ** (n - 1)
                g_series = poly_factor * ln_xi
                coeff_n = g_series[n]  # [w^n]
                lam_n = acb(str(n)) * coeff_n

                # Li coefficients are mathematically real
                lam_real = BallReal(lam_n.real)
                is_pos = lam_real.is_positive()
                if not is_pos:
                    all_pos = False

                results.append(
                    SingleLiCoefficient(
                        n=n,
                        val=lam_real,
                        is_strictly_positive=is_pos,
                        lower_bound=lam_real.midpoint - lam_real.radius,
                        upper_bound=lam_real.midpoint + lam_real.radius,
                    )
                )

            return CertifiedLiCoefficients(
                max_order=max_n,
                coefficients=results,
                all_positive=all_pos,
            )
