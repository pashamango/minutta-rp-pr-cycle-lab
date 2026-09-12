import json, tempfile, unittest
from pathlib import Path
from continuation.role_lease import CommanderLease, CommanderStore, LeaseError, ReporterCheckpoint

class CommanderLeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/"state.json"; self.s=CommanderStore(self.path,"role-1")
        self.role=CommanderLease("codex@wolfram.local","scope","mandate","2026-09-12T15:00:00Z","2026-09-12T16:00:00Z",4)
        self.s.create_role(self.role)
    def tearDown(self): self.tmp.cleanup()
    def args(self): return (self.role.principal,self.role.scope,self.role.mandate_digest,"2026-09-12T15:10:00Z")
    def test_monotonic_reporter_bound_settlement_and_restart_replay(self):
        self.s.start_child("A","a"*64,"1"*32,*self.args()); self.assertRaises(LeaseError, self.s.settle_child,"A","a"*64,"1"*32)
        for state in ("EXECUTION_CHECKPOINT","OUTCOME_CANDIDATE"): self.s.advance("A",state,*self.args())
        cp=ReporterCheckpoint("A","a"*64,"1"*32,"role-1","b"*64,"tools/wolfram-agent-reporter","v1")
        self.assertEqual(self.s.accept_reporter_checkpoint(cp,*self.args()),"settled")
        self.assertEqual(CommanderStore(self.path,"role-1").accept_reporter_checkpoint(cp,*self.args()),"already_settled")
        bad=ReporterCheckpoint("A","a"*64,"1"*32,"role-1","c"*64,"tools/wolfram-agent-reporter","v1")
        self.assertRaises(LeaseError, self.s.accept_reporter_checkpoint,bad,*self.args())
    def test_budget_and_bindings_fail_closed(self):
        for i in range(4): self.s.start_child(str(i),str(i)*64,str(i)*32,*self.args())
        self.assertRaises(LeaseError,self.s.start_child,"4","4"*64,"4"*32,*self.args())
        self.assertRaises(LeaseError,self.s.advance,"0","EXECUTION_CHECKPOINT","wrong","scope","mandate","2026-09-12T15:10:00Z")
        self.s.revoke(); self.assertRaises(LeaseError,self.s.resume,*self.args())
    def test_corrupt_state_is_not_reset(self):
        self.path.write_text("{",encoding="utf-8"); self.assertRaises(LeaseError,self.s.resumable_children)
    def test_expired_and_wrong_checkpoint_rejected(self):
        self.s.start_child("A","a"*64,"1"*32,*self.args())
        self.assertRaises(LeaseError,self.s.accept_reporter_checkpoint,ReporterCheckpoint("A","x"*64,"1"*32,"role-1","b"*64,"authority","v1"),*self.args())
        self.assertRaises(LeaseError,self.s.resume,"codex@wolfram.local","scope","mandate","2026-09-12T16:00:00Z")

if __name__ == "__main__": unittest.main()
