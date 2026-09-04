import importlib.util
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

TOOL = Path(__file__).parents[1] / "storage/tools/documents_resumable.py"
spec = importlib.util.spec_from_file_location("worker", TOOL)
worker = importlib.util.module_from_spec(spec); spec.loader.exec_module(worker)


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); root = Path(self.tmp.name)
        self.source=root/"source"; self.ns=root/"cas"; self.state=root/"state"; self.t0=root/"t0.json"
        self.source.mkdir(); self.ns.mkdir(); self.t0.write_text("{}")
        (self.source/"a").mkdir(); (self.source/"a/x.txt").write_bytes(b"same")
        (self.source/"b.txt").write_bytes(b"same")

    def tearDown(self): self.tmp.cleanup()

    def command(self, actions=0):
        return [sys.executable,str(TOOL),"--state",str(self.state),"run","--source",str(self.source),
                "--namespace",str(self.ns),"--t0",str(self.t0),"--allow-test-source","--once",
                "--timeout","2","--retries","2","--max-actions",str(actions)]

    def test_resumed_traversal_and_idempotent_verified_files(self):
        self.assertEqual(subprocess.run(self.command(1)).returncode,0)
        db=worker.connect(self.state); self.assertEqual(db.execute("select count(*) from dirs where status='done'").fetchone()[0],1); db.close()
        self.assertEqual(subprocess.run(self.command()).returncode,0)
        db=worker.connect(self.state); before=dict(db.execute("select path,attempts from entries where kind='file'")); db.close()
        self.assertEqual(subprocess.run(self.command()).returncode,0)
        db=worker.connect(self.state); after=dict(db.execute("select path,attempts from entries where kind='file'")); db.close()
        self.assertEqual(before,after); self.assertTrue(all(v==1 for v in after.values()))

    def test_lock_exclusivity(self):
        self.state.mkdir(); lock=(self.state/"worker.lock").open("a+")
        import fcntl
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try: self.assertEqual(subprocess.run(self.command(1)).returncode,73)
        finally: lock.close()

    def test_atomic_status_recovery(self):
        db=worker.connect(self.state); worker.initialize(db,self.source,self.ns,self.t0)
        worker.write_status(db,self.state); first=(self.state/"status.json").read_bytes()
        (self.state/".tmp-interrupted").write_bytes(b"bad")
        worker.write_status(db,self.state); self.assertEqual(first,(self.state/"status.json").read_bytes()); db.close()

    def test_bounded_retry(self):
        missing=self.source/"gone"; missing.write_bytes(b"x")
        db=worker.connect(self.state); worker.initialize(db,self.source,self.ns,self.t0); worker.enumerate_one(db,self.source); missing.unlink()
        for _ in range(4): worker.process_one(db,self.source,self.ns,1,2)
        row=db.execute("select attempts,status from entries where path=?",(b"gone",)).fetchone()
        self.assertEqual((row[0],row[1]),(2,"blocked")); db.close()

    def test_no_source_mutation_and_synthetic_convergence(self):
        before={p.relative_to(self.source): (p.read_bytes() if p.is_file() else None) for p in self.source.rglob("*")}
        self.assertEqual(subprocess.run(self.command()).returncode,0)
        after={p.relative_to(self.source): (p.read_bytes() if p.is_file() else None) for p in self.source.rglob("*")}
        self.assertEqual(before,after)
        db=worker.connect(self.state); status=worker.aggregates(db,self.state/"worker.lock")
        self.assertEqual(status["phase"],"converging"); self.assertEqual(status["files_verified"],2)
        self.assertGreater(status["deduplicated_bytes"],0); db.close()


if __name__ == "__main__": unittest.main()
