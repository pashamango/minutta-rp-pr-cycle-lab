import unittest
from datetime import datetime, timezone
from dp05 import Quota, TaskPack, OptimizerPolicy, optimize

NOW = datetime(2026, 11, 2, tzinfo=timezone.utc)

def q(i, amount, used=0, reserved=0, observed=NOW, confidence=1):
    return Quota(i, "provider", amount, "credits", "weekly", observed, "api-observation", confidence, reserved=reserved, used=used)

class DP05Tests(unittest.TestCase):
    def test_overconsumption_and_reserve(self):
        report = optimize([q("over", 5, used=6), q("reserve", 100, reserved=50)], [], OptimizerPolicy(NOW))
        self.assertIn("over: overconsumed by 1 credits", report.overconsumption_alerts)
        self.assertEqual(report.underutilized_quota_ids, ("reserve",))

    def test_stale_and_unknown_never_drive_proposal(self):
        stale = q("stale", 100, observed=datetime(2026, 10, 1, tzinfo=timezone.utc))
        unknown = q("unknown", None)
        pack = TaskPack("p", "work", 2, ("artifact",), {"stale": 1, "unknown": 1}, 10)
        report = optimize([stale, unknown], [pack], OptimizerPolicy(NOW))
        self.assertEqual(report.proposals, ())
        self.assertEqual(report.excluded_quota_ids, ("stale", "unknown"))

    def test_five_hour_concurrent_window_and_no_execution(self):
        quota = q("work", 10)
        packs = [TaskPack("big", "big", 6, ("x",), {"work": 1}, 99), TaskPack("small", "small", 4, ("y",), {"work": 1}, 5)]
        report = optimize([quota], packs, OptimizerPolicy(NOW))
        self.assertEqual([p.id for p in report.proposals], ["small"])
        self.assertEqual(report.execution_policy, "REPORT_ONLY; human approval required")

if __name__ == "__main__":
    unittest.main()
