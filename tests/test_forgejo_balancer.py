import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools.local_market_scheduler.forgejo_balancer import ForgejoBalancer, JsonForgejoTransport, SshLauncher
from tools.local_market_scheduler.scheduler import Host, Scheduler


class FakeForgejo:
    def __init__(self, jobs): self.jobs = jobs
    def ready_jobs(self): return self.jobs


class FakeLauncher:
    def __init__(self): self.calls = []
    def launch(self, host, job):
        self.calls.append((host, job.task_id, job.lease_id))
        return {"host": host, "task_id": job.task_id, "lease_id": job.lease_id}


class ForgejoBalancerTests(unittest.TestCase):
    def test_private_two_host_distribution_and_single_lease(self):
        jobs = [
            {"task_id": "F1", "priority": "P0", "host_class": "darwin", "source_digest": "a" * 64},
            {"task_id": "F2", "priority": "P1", "host_class": "wolfram", "source_digest": "b" * 64},
            {"task_id": "F3", "priority": "P1", "host_class": "either", "source_digest": "c" * 64},
        ]
        launcher = FakeLauncher(); scheduler = Scheduler()
        scheduler.observe([Host("darwin", "available"), Host("wolfram", "available")])
        balancer = ForgejoBalancer(FakeForgejo(jobs), launcher, scheduler)
        first = balancer.poll()
        self.assertEqual({x["host"] for x in first}, {"darwin", "wolfram"})
        self.assertEqual(balancer.poll(), [])
        self.assertEqual(len(launcher.calls), 2)

    def test_ssh_launcher_uses_argument_vector_and_no_shell(self):
        calls = []
        def runner(argv, **kwargs):
            calls.append((argv, kwargs)); return SimpleNamespace(stdout="ok\n")
        launcher = SshLauncher({"darwin": "darwin"}, runner)
        from tools.local_market_scheduler.scheduler import Job
        result = launcher.launch("darwin", Job("T", "P0", "darwin", "d" * 64, "e" * 32))
        self.assertEqual(result["host"], "darwin")
        self.assertEqual(calls[0][0][0:4], ["ssh", "-o", "BatchMode=yes", "-o"])
        self.assertNotIn(";", calls[0][0]); self.assertTrue(calls[0][1]["check"])

    def test_json_queue_fixture_and_shape_guard(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "queue.json"
            path.write_text(json.dumps([]))
            self.assertEqual(JsonForgejoTransport(path).ready_jobs(), [])
            path.write_text(json.dumps([{"task_id": "bad"}]))
            with self.assertRaises(ValueError):
                ForgejoBalancer(FakeForgejo(JsonForgejoTransport(path).ready_jobs()), FakeLauncher(), Scheduler()).poll()


if __name__ == "__main__": unittest.main()
