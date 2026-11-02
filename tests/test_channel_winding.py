"""Unit tests for Channel 2 certified zero counting via winding number integrals."""

import unittest
from amde_num.channel_winding import WindingNumberChannel


class TestChannelWinding(unittest.TestCase):
    def setUp(self):
        self.channel = WindingNumberChannel(default_dps=40)

    def test_zero_zeros_in_low_strip(self):
        """Contour [0.1, 0.9] x [5.0, 10.0] has no zeta zeros (gamma_1 ~ 14.13)."""
        res = self.channel.count_zeros_in_box(
            sigma_min=0.1,
            sigma_max=0.9,
            t_min=5.0,
            t_max=10.0,
            steps_per_edge=60,
        )
        self.assertTrue(res.is_certified_integer)
        self.assertEqual(res.proven_zero_count, 0)

    def test_single_zero_enclosure(self):
        """Contour [0.1, 0.9] x [10.0, 18.0] encloses exactly 1 zero (gamma_1 ~ 14.1347)."""
        res = self.channel.count_zeros_in_box(
            sigma_min=0.1,
            sigma_max=0.9,
            t_min=10.0,
            t_max=18.0,
            steps_per_edge=80,
        )
        self.assertTrue(res.is_certified_integer)
        self.assertEqual(res.proven_zero_count, 1)

    def test_two_zeros_enclosure(self):
        """Contour [0.1, 0.9] x [10.0, 24.0] encloses exactly 2 zeros (gamma_1 ~ 14.13, gamma_2 ~ 21.02)."""
        res = self.channel.count_zeros_in_box(
            sigma_min=0.1,
            sigma_max=0.9,
            t_min=10.0,
            t_max=24.0,
            steps_per_edge=90,
        )
        self.assertTrue(res.is_certified_integer)
        self.assertEqual(res.proven_zero_count, 2)


if __name__ == "__main__":
    unittest.main()
