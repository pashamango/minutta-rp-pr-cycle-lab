"""Unit tests for Channel 3 certified Li coefficients and Li's criterion."""

import unittest
from amde_num.channel_li import LiCoefficientChannel


class TestChannelLi(unittest.TestCase):
    def setUp(self):
        self.channel = LiCoefficientChannel(default_dps=50)

    def test_first_li_coefficient(self):
        """lambda_1 = 1 + gamma/2 - 1/2*ln(4*pi) ~ 0.023095708966..."""
        res = self.channel.compute_coefficients(max_n=1)
        lam1 = res.coefficients[0]

        expected_val = 0.023095708966
        self.assertAlmostEqual(lam1.val.midpoint, expected_val, places=8)
        self.assertTrue(lam1.is_strictly_positive)
        self.assertGreater(lam1.lower_bound, 0.0)

    def test_li_criterion_positivity_up_to_order_eight(self):
        """All computed Li coefficients lambda_1 .. lambda_8 must be strictly positive."""
        res = self.channel.compute_coefficients(max_n=8)
        self.assertTrue(res.all_positive)

        for c in res.coefficients:
            self.assertTrue(c.is_strictly_positive, f"lambda_{c.n} failed positivity check")
            self.assertGreater(c.lower_bound, 0.0)


if __name__ == "__main__":
    unittest.main()
