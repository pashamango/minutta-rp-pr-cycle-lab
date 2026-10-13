import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from governor import UTC,SCHEMA,sanitize_codexbar,analyze,ingest,latest_status,record_failure

NOW=dt.datetime(2026,10,9,23,0,tzinfo=UTC)
def stamp(t):return t.isoformat().replace('+00:00','Z')
def sample(used=8,at=NOW,reset=NOW+dt.timedelta(days=7)):
    return {'schema':SCHEMA,'provider':'codex','source':'oauth',
        'observed_at':stamp(at),'collected_at':stamp(at),'weekly_used_pct':used,
        'weekly_reset_at':stamp(reset),'session_used_pct':11,'session_reset_at':stamp(NOW+dt.timedelta(hours=5)),
        'attribution':'UNATTRIBUTED_CLOUD_WORK'}
def prev(used=8):return {'weekly_used_pct':used,'weekly_reset_at':stamp(NOW+dt.timedelta(days=7)),
                           'observed_at':stamp(NOW)}
class PilotTests(unittest.TestCase):
 def test_sanitize_redacts_identity(self):
  src=[{'provider':'codex','source':'oauth','usage':{
       'identity':{'accountEmail':'private@example.com'},'updatedAt':stamp(NOW),
       'primary':{'usedPercent':11},
       'secondary':{'usedPercent':8,'resetsAt':stamp(NOW+dt.timedelta(days=7))}}}]
  result=sanitize_codexbar(src)
  self.assertEqual(result['weekly_used_pct'],8)
  self.assertNotIn('private@example.com',json.dumps(result))
 def test_malicious_source_is_redacted(self):
  raw=[{'provider':'codex','source':'private.email@example.org', 'usage': {
    'updatedAt':stamp(NOW), 'secondary':{'usedPercent':12,'resetsAt':stamp(NOW+dt.timedelta(days=7))}}}]
  clean=sanitize_codexbar(raw)
  self.assertEqual(clean['source'],'unknown')
  self.assertNotIn('private.email',json.dumps(clean))
 def test_db_private_permissions(self):
  import os
  with tempfile.TemporaryDirectory() as d:
   fn=str(Path(d)/'test.sqlite3')
   ingest(sample(),fn,now=NOW)
   self.assertEqual(os.stat(fn).st_mode & 0o777,0o600)
 def test_baseline(self):self.assertEqual(analyze(sample(),now=NOW)['status'],'BASELINE')
 def test_normal(self):
  s=sample(9,NOW+dt.timedelta(hours=1))
  self.assertEqual(analyze(s,prev(),now=NOW+dt.timedelta(hours=1))['status'],'NORMAL')
 def test_spike(self):
  s=sample(19,NOW+dt.timedelta(hours=1))
  o=analyze(s,prev(),now=NOW+dt.timedelta(hours=1))
  self.assertEqual(o['status'],'BURN_SPIKE');self.assertEqual(o['burn_pp_per_hour'],11)
 def test_reset(self):
  s=sample(0,NOW+dt.timedelta(hours=1),NOW+dt.timedelta(days=14))
  self.assertEqual(analyze(s,prev(99),now=NOW+dt.timedelta(hours=1))['status'],'RESET_CHANGED')
 def test_stale(self):
  self.assertEqual(analyze(sample(),now=NOW+dt.timedelta(hours=4))['status'],'STALE')
 def test_low_budget(self):
  self.assertEqual(analyze(sample(85),now=NOW)['status'],'LOW_BUDGET')
 def test_reconciliation(self):
  s=sample(6,NOW+dt.timedelta(hours=1))
  self.assertEqual(analyze(s,prev(),now=NOW+dt.timedelta(hours=1))['status'],'RECONCILIATION')
 def test_interval_too_short(self):
  s=sample(13,NOW+dt.timedelta(minutes=5))
  self.assertEqual(analyze(s,prev(),now=NOW+dt.timedelta(minutes=5))['status'],'INTERVAL_TOO_SHORT')
 def test_no_alert_on_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   fn=str(Path(d)/'test.sqlite3')
   self.assertEqual(ingest(sample(),fn,now=NOW)['status'],'BASELINE')
   self.assertEqual(ingest(sample(),fn,now=NOW)['status'],'DUPLICATE')
 def test_dedupe_spike_alerts(self):
  with tempfile.TemporaryDirectory() as d:
   fn=str(Path(d)/'test.sqlite3')
   ingest(sample(),fn,now=NOW)
   first=ingest(sample(19,NOW+dt.timedelta(hours=1)),fn,now=NOW+dt.timedelta(hours=1))
   second=ingest(sample(32,NOW+dt.timedelta(hours=2)),fn,now=NOW+dt.timedelta(hours=2))
   self.assertIsNotNone(first.get('alert_id'))
   self.assertIsNone(second.get('alert_id'))
 def test_invalid_sample(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):ingest({'schema':SCHEMA,'provider':'codex'},str(Path(d)/'x.db'))
 def test_poll_unavailable_alert_is_durable_and_deduped(self):
  import sqlite3
  with tempfile.TemporaryDirectory() as d:
   fn=str(Path(d)/'test.sqlite3')
   self.assertIsNotNone(record_failure(fn,now=NOW)['alert_id'])
   self.assertIsNone(record_failure(fn,now=NOW+dt.timedelta(hours=1))['alert_id'])
   with sqlite3.connect(fn) as con:
    self.assertEqual(con.execute('SELECT COUNT(*) FROM alerts').fetchone()[0],1)
if __name__=='__main__':unittest.main(verbosity=2)