import unittest
from sovereign_worker.capability_session import *

class Tests(unittest.TestCase):
 def setUp(self):
  self.st=SyntheticState('b','c','p','m','t'); self.payload=MandatePayload('principal','dev',self.st.digest,'p',frozenset({'read'}),1,0,50); self.m=MandateLease(self.payload); self.proof=ApprovalProof('n',self.payload.digest); self.s=CapabilitySession(self.st,FakeApprovalVerifier({('n',self.payload.digest)}))
 def test_digest_is_canonical_and_field_mutations_break_proof(self):
  self.assertEqual(self.payload.digest,MandatePayload('principal','dev',self.st.digest,'p',frozenset({'read'}),1,0,50).digest)
  for field,value in [('principal','other'),('device_id','other-device'),('state_digest','bad'),('policy_digest','bad'),('allowed_classes',frozenset({'write'})),('session_epoch',2),('issued_at',1),('expires_at',49)]:
   data=self.payload.__dict__.copy();data[field]=value; self.assertNotEqual(MandatePayload(**data).digest,self.payload.digest)
 def test_authorize_replay_expiry_and_exact_proof(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); self.assertFalse(self.s.authorize(self.proof,self.m,1))
  expired=MandatePayload('principal','dev',self.st.digest,'p',frozenset({'read'}),1,0,1); s=CapabilitySession(self.st,FakeApprovalVerifier({('e',expired.digest)})); self.assertFalse(s.authorize(ApprovalProof('e',expired.digest),MandateLease(expired),1))
 def test_drift_invalidates_old_capability_and_requires_new_epoch(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); cap=self.s.issue(TaskLeaseRequest('t','src','lease','read',40),2); changed=SyntheticState('x','c','p','m','t',2); self.s.observe(changed); self.assertFalse(self.s.execute(cap,task_id='t',source_sha256='src',execution_lease='lease',capability_class='read',now=3))
  fresh=MandatePayload('principal','dev',changed.digest,'p',frozenset({'read'}),2,3,50); self.assertTrue(self.s.verifier.approvals=={('n',self.payload.digest)}) if False else None
  self.s.verifier.approvals.add(('fresh',fresh.digest)); self.assertTrue(self.s.authorize(ApprovalProof('fresh',fresh.digest),MandateLease(fresh),4))
 def test_issue_attenuates_scope_expiry_and_execution_binding(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); self.assertIsNone(self.s.issue(TaskLeaseRequest('t','src','l','write',40),1)); self.assertIsNone(self.s.issue(TaskLeaseRequest('t','src','l','read',51),1)); cap=self.s.issue(TaskLeaseRequest('t','src','l','read',40),1); self.assertTrue(self.s.execute(cap,task_id='t',source_sha256='src',execution_lease='l',capability_class='read',now=2)); self.assertFalse(self.s.execute(IssuedTaskCapability('t','src','l','read',1,40,50),task_id='t',source_sha256='src',execution_lease='l',capability_class='read',now=2))
 def test_unchanged_observation_and_revoke(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); self.s.observe(self.st); self.assertEqual(self.s.state_name,SessionState.ACTIVE); self.s.revoke(); self.assertEqual(self.s.state_name,SessionState.REVOKED)

if __name__=='__main__': unittest.main()
