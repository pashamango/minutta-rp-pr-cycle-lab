"""Automated unit test gate for AMDE-NUM."""

import unittest
from tests.test_xi_functional import TestRiemannXiFunctional
from tests.test_channel_ribbon import TestChannelRibbon
from tests.test_channel_winding import TestChannelWinding
from tests.test_channel_li import TestChannelLi


class TestAuditGate(unittest.TestCase):
    def test_full_pipeline_verification(self):
        """Runs and asserts all sub-suites pass."""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromTestCase(TestRiemannXiFunctional))
        suite.addTests(loader.loadTestsFromTestCase(TestChannelRibbon))
        suite.addTests(loader.loadTestsFromTestCase(TestChannelWinding))
        suite.addTests(loader.loadTestsFromTestCase(TestChannelLi))

        runner = unittest.TextTestRunner(verbosity=1)
        res = runner.run(suite)
        self.assertTrue(res.wasSuccessful(), f"Audit gate failures: {len(res.failures)}, errors: {len(res.errors)}")


if __name__ == "__main__":
    unittest.main()
