import copy
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import muse_bridge as m


def example():
    return {'schema':'muse-telemetry/v1','report_date':'2026-10-13','generated_at':'2026-10-13T20:20:00-07:00',
            'cron_runs':{'total_runs':3,'total_succeeded':2,'total_failed':1,
                         'by_job':{'job-one':{'runs':3,'succeeded':2,'failed':1,'avg_duration_s':12}}},
            'subscription':{'usage_pct_of_weekly_limit':7,'resets_at':'2026-10-20T08:28:00-07:00'},
            'session_context':{'used_pct':33,'available_pct':67},
            'errors_anomalies':{'count':1}, 'perimeter':'Never include anything sensitive'}

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'muse-external'
        self.source=Path(self.tmp.name)/'file.json'
    def write(self,d):self.source.write_text(json.dumps(d))
    def test_parse_real_shape(self):
        p=m.normalize(example());self.assertEqual(p['totals']['runs'],3);self.assertEqual(p['period_status'],'PRELIMINARY')
    def test_nightly_cutoff_not_midnight(self):
        d=example();d['generated_at']='2026-10-13T23:32:00-07:00'
        self.assertEqual(m.normalize(d)['period_status'],'NIGHTLY_CUTOFF')
    def test_reject_incoherent_job(self):
        d=example();d['cron_runs']['by_job']['job-one']['succeeded']=3
        with self.assertRaises(ValueError):m.normalize(d)
    def test_reject_bad_overall_total(self):
        d=example();d['cron_runs']['total_runs']=999
        with self.assertRaises(ValueError):m.normalize(d)
    def test_reject_unsafe_job_label(self):
        d=example();d['cron_runs']['by_job']['secret\\\\line']=d['cron_runs']['by_job'].pop('job-one')
        with self.assertRaises(ValueError):m.normalize(d)
    def test_reject_percent_over_100(self):
        d=example();d['subscription']['usage_pct_of_weekly_limit']=200
        with self.assertRaises(ValueError):m.normalize(d)
    def test_reject_bad_session_complement(self):
        d=example();d['session_context']['available_pct']=45
        with self.assertRaises(ValueError):m.normalize(d)
    def test_no_raw_secrets_in_ledger(self):
        d=example();d['password']='DONOTSTOREME';d['proof_of_work']=[{'ref':'PRIVATE_TOKEN_ABCDEFG'}]
        self.write(d);m.ingest(self.root,self.source)
        raw=(self.root/'muse.jsonl').read_text()
        self.assertNotIn('DONOTSTOREME',raw);self.assertNotIn('PRIVATE_TOKEN_ABCDEFG',raw)
    def test_ingest_idempotent_and_revisions(self):
        self.write(example());r=m.ingest(self.root,self.source)
        self.assertEqual(r['status'],'INGESTED')
        self.assertEqual(m.ingest(self.root,self.source)['status'],'DUPLICATE')
        d=example();d['generated_at']='2026-10-13T23:32:00-07:00'
        self.write(d);self.assertEqual(m.ingest(self.root,self.source)['events'],2)
        self.assertEqual(m.audit(self.root)['events'],2)
    def test_tamper_detection(self):
        self.write(example());m.ingest(self.root,self.source)
        p=self.root/'muse.jsonl';x=p.read_bytes().replace(b'"weekly_usage_pct":7.0',b'"weekly_usage_pct":8.0')
        self.assertNotEqual(p.read_bytes(),x)
        p.write_bytes(x)
        with self.assertRaises(ValueError):m.audit(self.root)
    def test_truncated_record_rejected(self):
        self.write(example());m.ingest(self.root,self.source)
        with (self.root/'muse.jsonl').open('ab') as f:f.write(b'{broken')
        with self.assertRaises(ValueError):m.audit(self.root)
    def test_projection_and_prometheus(self):
        self.write(example());m.ingest(self.root,self.source)
        self.assertEqual(m.project(self.root)['status'],'PROJECTED')
        out=m.prom(self.root)
        self.assertIn('simsim_muse_daily_runs 3',out)
        self.assertIn('simsim_muse_daily_job_runs{job="job-one"} 3',out)
        self.assertIn('simsim_muse_source_testimony 1',out)
    def test_empty_prom_does_not_pretend_zero(self):
        self.assertIn('unknown is not zero',m.prom(self.root))
    def test_testimony_not_remote_truth(self):
        p=m.normalize(example());self.assertEqual(p['confidence'],'EXTERNAL_AGENT_TESTIMONY')
        self.assertNotIn('proof_of_work',p)
    def test_invalid_drive_id(self):
        self.write(example())
        with self.assertRaises(ValueError):m.ingest(self.root,self.source,'../oops')
    def test_permissions(self):
        self.write(example());m.ingest(self.root,self.source)
        self.assertEqual(self.root.stat().st_mode&0o777,0o700)
        self.assertEqual((self.root/'muse.jsonl').stat().st_mode&0o777,0o600)
    def test_real_cli_subprocess(self):
        self.write(example())
        proc=subprocess.run([sys.executable,str(Path(m.__file__).resolve()),'--root',str(self.root),'ingest','--input',str(self.source)],capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['status'],'INGESTED')
        proc2=subprocess.run([sys.executable,str(Path(m.__file__).resolve()),'--root',str(self.root),'verify'],capture_output=True,text=True)
        self.assertEqual(proc2.returncode,0)
        self.assertEqual(json.loads(proc2.stdout)['events'],1)
    def test_oversized_source(self):
        self.source.write_bytes(b'x'*70000)
        with self.assertRaises(ValueError):m.normalize_file(self.source)

if __name__=='__main__':unittest.main()
