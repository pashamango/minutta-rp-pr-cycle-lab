"""DP-01B deterministic, network-free tests (all system probes mocked)."""
import datetime as dt
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import event_ledger as e
import host_adapter as a
import source_attest as f

NOW=dt.datetime(2026,10,13,23,0,tzinfo=dt.timezone.utc)


def base(node='darwin'):
    return {'schema':a.SCHEMA, 'node_role':node, 'sampled_at':'2026-10-13T23:00:00Z',
            'metrics_status':{'cpu':'SOURCE_READ_LOCAL','load':'SOURCE_READ_LOCAL',
                              'swap':'SOURCE_READ_LOCAL','disk':'SOURCE_READ_LOCAL'},
            'services':dict.fromkeys(a.SERVICES,'READ_BLOCKED'),
            'cpu_logical':4,'load_1m':1.,'load_5m':2.,'load_15m':3.,
            'swap_used_bytes':100,'swap_total_bytes':500,
            'disk_free_bytes':1000,'disk_total_bytes':5000}

class HostAdapterTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)/'ledger'

    def test_append_and_dedupe_and_projection(self):
        sample=base()
        self.assertEqual(a.ingest(sample,self.root,expected_node='darwin')['status'],'APPENDED')
        self.assertEqual(a.ingest(sample,self.root)['status'],'DUPLICATE')
        self.assertEqual(e.audit(self.root)['types']['host.snapshot'],1)
        self.assertEqual(e.project(self.root)['events'],1)
        cp=e.checkpoint(self.root)
        self.assertEqual(cp['count'],1)
        self.assertEqual(e.audit(self.root)['count'],1)

    def test_different_roles_same_timestamp_distinct(self):
        a.ingest(base('darwin'),self.root)
        a.ingest(base('wolfram'),self.root)
        self.assertEqual(e.audit(self.root)['count'],2)

    def test_changed_same_identity_fails_closed(self):
        a.ingest(base(),self.root)
        changed=base();changed['disk_free_bytes']=999
        before=e.audit(self.root)['tip']
        with self.assertRaisesRegex(ValueError,'Conflicting'):a.ingest(changed,self.root)
        self.assertEqual(e.audit(self.root)['tip'],before)

    def test_host_role_mismatch(self):
        with self.assertRaises(ValueError):a.ingest(base('wolfram'),self.root,'darwin')
        self.assertFalse(self.root.exists())

    def test_no_identifiers_allowed(self):
        for field in ('email','host','hostname','ip','token','username','ssh_key'):
            p=base();p[field]='secret'
            with self.assertRaises(ValueError):a.validate(p)

    def test_unrecognized_node_and_service(self):
        p=base();p['node_role']='another-machine'
        with self.assertRaises(ValueError):a.validate(p)
        p=base();p['services']['forgejo']='ONLINE_SUPERUSER'
        with self.assertRaises(ValueError):a.validate(p)

    def test_read_blocked_not_zero(self):
        p=base();p['swap_used_bytes']=p['swap_total_bytes']=None
        p['metrics_status']['swap']='READ_BLOCKED'
        a.validate(p)
        with self.assertRaises(ValueError):
            p['metrics_status']['swap']='SOURCE_READ_LOCAL';a.validate(p)

    def test_boolean_nan_and_overcapacity_rejected(self):
        p=base();p['cpu_logical']=True
        with self.assertRaises(ValueError):a.validate(p)
        p=base();p['load_1m']=float('nan')
        with self.assertRaises(ValueError):a.validate(p)
        p=base();p['disk_free_bytes']=5001
        with self.assertRaises(ValueError):a.validate(p)

    def test_malformed_time_rejected(self):
        p=base();p['sampled_at']='yesterday'
        with self.assertRaises(ValueError):a.validate(p)

    def test_no_writes_when_corrupt_journal(self):
        a.ingest(base(),self.root)
        path=e.files(self.root)[0]
        path.write_bytes(path.read_bytes()+b'half')
        with self.assertRaises(ValueError):a.ingest(base('wolfram'),self.root)

    def test_collection_mocked_system(self):
        mem=MagicMock(free=1200,total=3000)
        with patch.object(a.sys,'platform','darwin'),\
             patch.object(a.os,'getloadavg',return_value=(1.25,2.5,3.75)),\
             patch.object(a.os,'cpu_count',return_value=8),\
             patch.object(a.shutil,'disk_usage',return_value=mem),\
             patch.object(a,'swap_usage',return_value=(20,100)),\
             patch.object(a,'tailscale',return_value='BACKEND_RUNNING'),\
             patch.object(a,'tcp_local',side_effect=['TCP_ACCEPTING','TCP_REFUSED']),\
             patch.object(a,'launchd',return_value='LAUNCHD_REGISTERED'):
            snap=a.collect('darwin',NOW)
        self.assertEqual(snap['swap_used_bytes'],20)
        self.assertEqual(snap['services']['ollama'],'TCP_REFUSED')
        self.assertEqual(snap['metrics_status']['swap'],'SOURCE_READ_LOCAL')
        self.assertNotIn('username',json.dumps(snap))

    def test_collection_failed_swap_is_null(self):
        with patch.object(a.sys,'platform','darwin'),\
             patch.object(a,'swap_usage',return_value=None),\
             patch.object(a,'tailscale',return_value='READ_BLOCKED'),\
             patch.object(a,'tcp_local',return_value='READ_BLOCKED'),\
             patch.object(a,'launchd',return_value='READ_BLOCKED'):
            snap=a.collect('wolfram',NOW)
        self.assertIsNone(snap['swap_total_bytes'])
        self.assertEqual(snap['metrics_status']['swap'],'READ_BLOCKED')
        a.validate(snap)

    def test_swap_parser(self):
        fake=MagicMock(returncode=0,stdout='total = 1024.00M used = 64.25M free = 959.75M')
        with patch.object(a,'cmd',return_value=fake):
            self.assertEqual(a.swap_usage(),(67371008,1073741824))

    def test_swap_parser_invalid_fails_closed(self):
        with patch.object(a,'cmd',return_value=MagicMock(returncode=1,stdout='')):
            self.assertIsNone(a.swap_usage())

    def test_tailscale_json_sanitized(self):
        j={'BackendState':'Running','Self':{'HostName':'private-mac','TailscaleIPs':['100.77.188.3']}}
        with patch.object(Path,'is_file',return_value=True),patch.object(a,'cmd',return_value=MagicMock(returncode=0,stdout=json.dumps(j))):
            status=a.tailscale()
        self.assertEqual(status,'BACKEND_RUNNING')
        self.assertNotIn('private-mac',status)

    def test_tailscale_cli_failed_never_claims_down(self):
        with patch.object(Path,'is_file',return_value=True),patch.object(a,'cmd',return_value=None):
            self.assertEqual(a.tailscale(),'READ_BLOCKED')

    def test_launchd_registered_is_not_process_running(self):
        with patch.object(a,'cmd',return_value=MagicMock(returncode=0)):
            self.assertEqual(a.launchd('test'),'LAUNCHD_REGISTERED')

    def test_private_journal_permissions(self):
        a.ingest(base(),self.root)
        self.assertEqual(self.root.stat().st_mode&0o777,0o700)
        self.assertEqual(e.files(self.root)[0].stat().st_mode&0o777,0o600)

class AttestationTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)/'script.py'

    def test_missing_does_not_claim_diff(self):
        r=f.audit_source(self.path)
        self.assertEqual(r['status'],'MISSING')
        self.assertEqual(r['reference'],'UNKNOWN_NOT_PRESENT')

    def test_matching_checksum(self):
        import hashlib
        self.path.write_bytes(b'print(1)\n')
        sha=hashlib.sha256(self.path.read_bytes()).hexdigest()
        out=f.audit_source(self.path,sha)
        self.assertEqual(out['reference'],'MATCH')
        self.assertEqual(out['publication'],'HUMAN_REVIEW_REQUIRED')
        self.assertEqual(out['suspicious_pattern_classes'],0)

    def test_secrets_scanner_no_content_leaks(self):
        self.path.write_bytes(b'GITHUB_TOKEN=github_pat_abcdefghabcdefghabcdefghabc\n')
        out=f.audit_source(self.path)
        self.assertGreater(out['suspicious_pattern_classes'],0)
        self.assertNotIn('github_pat',json.dumps(out))

    def test_reject_symlink(self):
        self.path.symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):f.audit_source(self.path)

    def test_reject_oversize(self):
        self.path.write_bytes(b'1'*(f.MAX_BYTES+1))
        with self.assertRaises(ValueError):f.audit_source(self.path)

    def test_source_changed_after_read_detection(self):
        self.path.write_bytes(b'hi')
        with patch.object(Path,'read_bytes',return_value=b'changed'):
            with self.assertRaises(ValueError):f.audit_source(self.path)

if __name__=='__main__':unittest.main()
