import tempfile
import unittest
from pathlib import Path

from continuation.queue import acknowledge, enqueue, pending


class ContinuationQueueTests(unittest.TestCase):
    def test_bound_enqueue_is_idempotent_and_acknowledge_is_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            args = dict(task_id="T1", source_digest="a" * 64, lease_id="b" * 32, run_dir=root / "run")
            first = enqueue(root, **args)
            self.assertEqual(first, enqueue(root, **args))
            self.assertEqual(len(pending(root)), 1)
            acknowledge(root, **{k: args[k] for k in ("task_id", "source_digest", "lease_id")})
            self.assertEqual(pending(root), [])

    def test_binding_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            enqueue(root, task_id="T1", source_digest="a" * 64, lease_id="b" * 32, run_dir=root)
            with self.assertRaises(ValueError):
                enqueue(root, task_id="T2", source_digest="a" * 64, lease_id="b" * 32, run_dir=root)
