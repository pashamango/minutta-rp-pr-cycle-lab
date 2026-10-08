import unittest
from tools.local_market_scheduler import Host, Job, Scheduler

class SchedulerTests(unittest.TestCase):
    def test_dual_dispatch_completion_and_idempotency(self):
        s=Scheduler(idle_threshold=10); s.observe([Host("darwin","available",last_seen=100),Host("wolfram","available",last_seen=100)])
        s.enqueue(Job("W1","P0","wolfram","a"*64)); s.enqueue(Job("D1","P1","darwin","b"*64)); s.enqueue(Job("N1","P1","either","c"*64))
        first=s.reconcile(now=101); self.assertEqual({d["host"] for d in first},{"darwin","wolfram"}); self.assertEqual(s.reconcile(now=102),[])
        s.complete("wolfram","W1","settled"); self.assertEqual(s.reconcile(now=103)[0]["task_id"],"N1")
        self.assertEqual(len(s.db.execute("select * from events where kind='dispatch'").fetchall()),3)

if __name__ == "__main__": unittest.main()
