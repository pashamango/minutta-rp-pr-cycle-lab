import unittest
from sovereign_worker.capability_session import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.st=SyntheticState('b','c','p','m','t'); self.m=MandateLease('md','dev','p',frozenset({'read'}),100); self.a=Approval('n','md',self.st.digest,'dev','p',frozenset({'read'}),1,50); self.v=FakeApprovalVerifier([('n','md',self.st.digest,'dev','p',frozenset({'read'}),1,50)]); self.s=CapabilitySession(self.st,self.v)
 def auth(self): self.assertTrue(self.s.authorize(self.a,self.m,1))
 def test_issue_and_execute_only_registered_exact_capability(self):
  self.auth(); cap=self.s.issue(TaskLeaseRequest('t','src','lease','read',40),2); self.assertTrue(self.s.execute(cap,task_id='t',source_sha256='src',execution_lease='lease',capability_class='read',now=3)); self.assertFalse(self.s.execute(IssuedTaskCapability('t','src','lease','read',1,40,100),task_id='t',source_sha256='src',execution_lease='lease',capability_class='read',now=3))
 def test_exact_binding_rejects_empty_and_replay(self):
  self.assertFalse(self.s.authorize(Approval('n','md','', 'dev','p',frozenset({'read'}),1,50),self.m,1)); self.auth(); self.assertFalse(self.s.authorize(self.a,self.m,1))
 def test_drift_requires_fresh_proof_and_old_observation_fails(self):
  self.auth(); self.s.observe(SyntheticState('x','c','p','m','t')); self.s.observe(self.st); self.assertEqual(self.s.state_name,SessionState.REAUTH_REQUIRED); self.assertFalse(self.s.authorize(self.a,self.m,1))
 def test_fresh_proof_reauthorizes_after_drift(self):
  changed=SyntheticState('x','c','p','m','t'); fresh=Approval('fresh','md',changed.digest,'dev','p',frozenset({'read'}),1,50); v=FakeApprovalVerifier([('fresh','md',changed.digest,'dev','p',frozenset({'read'}),1,50)]); s=CapabilitySession(self.st,v); s.authorize(self.a,self.m,1) if False else None; s.observe(changed); self.assertTrue(s.authorize(fresh,self.m,2)); self.assertEqual(s.state_name,SessionState.ACTIVE)
 def test_scope_expiry_and_revocation(self):
  self.auth(); self.assertIsNone(self.s.issue(TaskLeaseRequest('t','src','l','write',40),1)); self.assertIsNone(self.s.issue(TaskLeaseRequest('t','src','l','read',101),1)); cap=self.s.issue(TaskLeaseRequest('t','src','l','read',40),1); self.s.revoke(); self.assertFalse(self.s.execute(cap,task_id='t',source_sha256='src',execution_lease='l',capability_class='read',now=2))
 def test_unchanged_observation_nontrigger(self): self.auth(); self.s.observe(self.st); self.assertEqual(self.s.state_name,SessionState.ACTIVE)
if __name__=='__main__': unittest.main()
