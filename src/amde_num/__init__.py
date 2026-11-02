"""AMDE-NUM: Certified Arbitrary-Precision Ball Arithmetic for Riemann xi.

Rigorous numerical verification suite based on Arb/FLINT ball arithmetic.
Provides certified enclosures for xi(s), ribbon flows, winding numbers, and Li coefficients.
"""

from .ball_arithmetic import ArbContext, BallReal, BallComplex
from .xi_functional import RiemannXi, CertifiedXiResult
from .channel_ribbon import RibbonFlowChannel, GoldenAttractorCheck
from .channel_winding import WindingNumberChannel, CertifiedZeroCount
from .channel_li import LiCoefficientChannel, CertifiedLiCoefficients
from .three_channel_experiment import ThreeChannelExperiment

__all__ = [
    "ArbContext",
    "BallReal",
    "BallComplex",
    "RiemannXi",
    "CertifiedXiResult",
    "RibbonFlowChannel",
    "GoldenAttractorCheck",
    "WindingNumberChannel",
    "CertifiedZeroCount",
    "LiCoefficientChannel",
    "CertifiedLiCoefficients",
    "ThreeChannelExperiment",
]
