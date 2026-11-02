"""Unit tests for certified Riemann xi functional evaluation."""

import unittest
import math
from amde_num.xi_functional import RiemannXi
from amde_num.ball_arithmetic import ArbContext


class TestRiemannXiFunctional(unittest.TestCase):
    def setUp(self):
        self.engine = RiemannXi(default_dps=45)

    def test_values_at_zero_and_one(self):
        """xi(0) and xi(1) must rigorously equal 1/2."""
        res_0 = self.engine.evaluate(s_re=0.0, s_im=0.0)
        res_1 = self.engine.evaluate(s_re=1.0, s_im=0.0)

        # Enclosures must contain 0.5
        self.assertTrue(res_0.xi.real.contains_point(0.5))
        self.assertTrue(res_1.xi.real.contains_point(0.5))
        self.assertTrue(res_0.xi.imag.contains_point(0.0))
        self.assertTrue(res_1.xi.imag.contains_point(0.0))

        # Precision must be better than 1e-35
        self.assertLess(res_0.radius_bound, 1e-35)
        self.assertLess(res_1.radius_bound, 1e-35)

    def test_value_at_s_equals_two(self):
        """xi(2) = 1/2 * 2 * 1 * pi^(-1) * Gamma(1) * zeta(2) = pi / 6."""
        res_2 = self.engine.evaluate(s_re=2.0, s_im=0.0)
        expected_mid = math.pi / 6.0
        self.assertAlmostEqual(res_2.xi.real.midpoint, expected_mid, places=10)
        self.assertLess(res_2.radius_bound, 1e-35)

    def test_reflection_symmetry(self):
        """Verify xi(s) = xi(1 - s) for diverse points."""
        test_points = [
            (0.75, 5.0),
            (2.5, 10.0),
            (-0.3, 14.0),
            (0.5, 20.0),
        ]
        for re, im in test_points:
            res = self.engine.evaluate(s_re=re, s_im=im)
            self.assertTrue(res.is_reflection_symmetric, f"Reflection symmetry failed at {re}+{im}j")
            self.assertTrue(res.refl_diff.contains_zero())

    def test_known_zeta_zeros(self):
        """Check certified zeros of Riemann xi: xi(1/2 + i*gamma_k) must enclose 0."""
        known_zeros = [
            "14.1347251417346937904572519835624702707842571156992",
            "21.0220396387715549926284795938969027773343405240837",
            "25.0108575801456887632137909925628218186595496725579966724965",
        ]
        for gamma in known_zeros:
            res = self.engine.evaluate_xi_on_critical_line(t=gamma)
            self.assertTrue(res.xi.contains_point(0.0, 0.0), f"Zero not enclosed at gamma={gamma}")
            self.assertLess(abs(res.xi.real.midpoint), 1e-12)
            self.assertLess(abs(res.xi.imag.midpoint), 1e-12)


if __name__ == "__main__":
    unittest.main()
