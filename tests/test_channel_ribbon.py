"""Unit tests for Channel 1 Ribbon flow and Golden difference operator."""

import unittest
from amde_num.channel_ribbon import RibbonFlowChannel


class TestChannelRibbon(unittest.TestCase):
    def setUp(self):
        self.channel = RibbonFlowChannel(default_dps=40)

    def test_even_parity(self):
        """F(delta, t) must equal F(-delta, t) within certified ball arithmetic."""
        res = self.channel.run_channel(t_val=20.0, n_levels=3)
        self.assertTrue(res.is_even)
        self.assertTrue(res.even_discrepancy.contains_zero())

    def test_golden_operator_cancellation_and_ratio(self):
        """L_phi F must cancel O(1) and O(delta) terms and converge to 2*F''(0)*delta_(n+1)*delta_(n+2)."""
        res = self.channel.run_channel(t_val=20.0, n_levels=5)
        # Ratio should approach 1.0 as n increases (higher order O(delta^4) terms become negligible)
        ratios = [g.ratio for g in res.golden_checks]

        # Ratios must all be close to 1.0
        for r in ratios:
            self.assertAlmostEqual(r, 1.0, places=2)

        # Monotonic convergence towards 1.0
        err1 = abs(ratios[0] - 1.0)
        err5 = abs(ratios[-1] - 1.0)
        self.assertLess(err5, err1)
        self.assertLess(err5, 1e-4)

    def test_non_golden_geometric_controls(self):
        """Non-golden ratios q=0.6 and q=0.5 must not exhibit algebraic cancellation."""
        res = self.channel.run_channel(t_val=20.0, n_levels=1)
        # For q=0.6 and q=0.5, 1 - q != q^2, so the O(delta^2) cancellation formula fails
        self.assertNotEqual(res.geometric_control_q06, 0.0)
        self.assertNotEqual(res.geometric_control_q05, 0.0)


if __name__ == "__main__":
    unittest.main()
