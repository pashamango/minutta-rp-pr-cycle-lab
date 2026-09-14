import unittest
from sovereign_worker.capability_session import *

class Tests(unittest.TestCase):
 def setUp(self):
  self.st=SyntheticState('b','c','p','m','t'); self.payload=MandatePayload('principal','m',self.st.digest,'p',frozenset({'read'}),1,0,50); self.m=MandateLease(self.payload); self.proof=ApprovalProof('n',self.payload.digest); self.s=CapabilitySession(self.st,FakeApprovalVerifier({('n',self.payload.digest)}))
 def test_every_payload_mutation_rejects_reused_original_proof(self):
  for field,value in {'principal':'other','device_id':'other-device','state_digest':'bad','policy_digest':'bad','allowed_classes':frozenset({'write'}),'session_epoch':2,'issued_at':1,'expires_at':49}.items():
   data=self.payload.__dict__.copy(); data[field]=value; mutated=MandateLease(MandatePayload(**data)); self.assertNotEqual(mutated.mandate_digest,self.payload.digest); self.assertFalse(self.s.authorize(self.proof,mutated,1),field)
 def test_session_capability_binds_all_request_fields_and_rejects_forgery(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); cap=self.s.issue(TaskLeaseRequest('task','src','lease','read',40),2); self.assertIsNotNone(cap)
  for args in [('other-task','src','lease','read'),('task','other-source','lease','read'),('task','src','other-lease','read'),('task','src','lease','write')]: self.assertFalse(self.s.execute(cap,task_id=args[0],source_sha256=args[1],execution_lease=args[2],capability_class=args[3],now=3))
  forged=IssuedTaskCapability('task','src','lease','read',1,40,50); self.assertFalse(self.s.execute(forged,task_id='task',source_sha256='src',execution_lease='lease',capability_class='read',now=3))
 def test_cross_device_policy_epoch_and_expiry_reject(self):
  for field,value in [('device_id','other-device'),('policy_digest','other-policy'),('session_epoch',2)]:
   data=self.payload.__dict__.copy(); data[field]=value; altered=MandateLease(MandatePayload(**data)); self.assertFalse(CapabilitySession(self.st,FakeApprovalVerifier({('x',altered.mandate_digest)})).authorize(ApprovalProof('x',altered.mandate_digest),altered,1))
  expired=MandatePayload('principal','m',self.st.digest,'p',frozenset({'read'}),1,0,1); self.assertFalse(CapabilitySession(self.st,FakeApprovalVerifier({('e',expired.digest)})).authorize(ApprovalProof('e',expired.digest),MandateLease(expired),1)); self.assertTrue(self.s.authorize(self.proof,self.m,1)); self.assertIsNone(self.s.issue(TaskLeaseRequest('t','src','l','read',51),1))
 def test_drift_requires_newer_epoch_and_invalidates_old_proof_and_capability(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); cap=self.s.issue(TaskLeaseRequest('t','src','lease','read',40),2); changed=SyntheticState('x','c','p','m','t',2); self.s.observe(changed); self.assertFalse(self.s.execute(cap,task_id='t',source_sha256='src',execution_lease='lease',capability_class='read',now=3)); self.assertFalse(self.s.authorize(self.proof,self.m,3)); fresh=MandatePayload('principal','m',changed.digest,'p',frozenset({'read'}),2,3,50); fp=ApprovalProof('fresh',fresh.digest); self.s.verifier.approvals.add((fp.nonce,fp.mandate_digest)); self.assertTrue(self.s.authorize(fp,MandateLease(fresh),4)); self.assertFalse(self.s.execute(cap,task_id='t',source_sha256='src',execution_lease='lease',capability_class='read',now=5)); self.assertFalse(self.s.authorize(fp,MandateLease(fresh),5))
 def test_returning_to_old_observation_does_not_restore_authority(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); self.s.observe(SyntheticState('x','c','p','m','t',2)); self.s.observe(self.st); self.assertFalse(self.s.authorize(self.proof,self.m,3))
 def test_unchanged_sleep_wake_and_python_venv_replacement_are_non_triggers(self):
  self.assertTrue(self.s.authorize(self.proof,self.m,1)); self.s.observe(self.st); self.s.observe(self.st); self.assertEqual(self.s.state_name,SessionState.ACTIVE); self.assertIsNotNone(self.s.issue(TaskLeaseRequest('t','src','l','read',40),2))

if __name__=='__main__': unittest.main()
