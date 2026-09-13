import hashlib, json, tempfile, unittest
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
        self.assertRaisesRegex(LeaseError,"issuer-authenticated certificate",self.s.advance,"A","REPORTER_VALIDATED",*self.args())
        cp=ReporterCheckpoint("A","a"*64,"1"*32,"role-1","b"*64,"tools/wolfram-agent-reporter","v1")
        self.assertRaisesRegex(LeaseError,"issuer-authenticated certificate",self.s.accept_reporter_checkpoint,cp,*self.args())
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

    def test_reporter_validation_record_is_the_only_file_adapter(self):
        self.s.start_child("A","a"*64,"1"*32,*self.args())
        for state in ("EXECUTION_CHECKPOINT","OUTCOME_CANDIDATE"): self.s.advance("A",state,*self.args())
        record={"protocol":"chitakasha-reporter-validation/v1","reporter_authority":"wolfram-agent-reporter","reporter_protocol":"chitakasha-reporter-validation/v1","reporter_sha256":"8723f408947bf50962b1b451f44f7d1e33516c9fa6e8adffce76556b1ef0c9ed","task_id":"A","source_sha256":"a"*64,"lease_id":"1"*32,"issue_number":196,"outcome_status":"completed","outcome_sha256":"b"*64,"terminal_receipt_state":"TASK_COMPLETED","receipt_key":"sha256:"+"c"*64,"evidence_validation":[],"validation_timestamp":"2026-09-12T15:10:00Z","validation_timestamp_source":"result.finished_at","remote_state":"posted"}
        record["payload_sha256"]=hashlib.sha256(json.dumps(record,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        path=self.path.parent/"validation-record.json"; path.write_text(json.dumps(record))
        self.assertRaisesRegex(LeaseError,"unkeyed validation records",self.s.accept_validation_record,path,*self.args(),source_issue=196)
        record["remote_state"]="posted"; record["payload_sha256"]="0"*64; path.write_text(json.dumps(record))
        self.assertRaises(LeaseError,self.s.accept_validation_record,path,*self.args(),source_issue=196)

if __name__ == "__main__": unittest.main()
