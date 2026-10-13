"""Deterministic DP-01 tests. No real CodexBar, SSH, API or background jobs."""
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from unittest import TestCase
from unittest.mock import patch

import event_ledger as e
import run_cycle

NOW=dt.datetime(2026,10,13,21,0,tzinfo=dt.timezone.utc)

def seed_db(path, n=1):
    con=sqlite3.connect(path)
    con.execute('CREATE TABLE observations (observed_at TEXT PRIMARY KEY, weekly_reset_at TEXT NOT NULL, weekly_used_pct REAL NOT NULL, session_used_pct REAL, source TEXT NOT NULL, collected_at TEXT NOT NULL)')
    con.execute('CREATE TABLE alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, kind TEXT NOT NULL, message TEXT NOT NULL, delivery TEXT NOT NULL)')
    for i in range(n):
        t=e.iso(NOW+dt.timedelta(hours=i))
        con.execute('INSERT INTO observations VALUES (?,?,?,?,?,?)',(t,e.iso(NOW+dt.timedelta(days=7)),24.+i,None,'oauth',t))
    con.execute('INSERT INTO alerts(created_at,kind,message,delivery) VALUES (?,?,?,?)',
                (e.iso(NOW),'BURN_SPIKE','private message must not persist','PENDING'))
    con.commit();con.close()

class LedgerTests(TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'ledger';self.db=Path(self.tmp.name)/'governor.sqlite3'
        seed_db(self.db,2)

    def sync(self):return e.reconcile(self.root,str(self.db),now=NOW)

    def test_sync_and_dedupe(self):
        a=self.sync();b=self.sync()
        self.assertEqual(a['appended']['quota.observation'],2)
        self.assertEqual(a['appended']['quota.alert'],1)
        self.assertEqual(b['appended']['quota.observation'],0)
        self.assertEqual(e.audit(self.root)['count'],3)

    def test_append_only_restart(self):
        self.sync();before=e.audit(self.root)['tip'];self.sync()
        self.assertEqual(e.audit(self.root)['tip'],before)

    def test_ordered_arrival_despite_observed_time(self):
        self.sync();a=e.audit(self.root)
        conn=sqlite3.connect(self.db)
        conn.execute('INSERT INTO observations VALUES (?,?,?,?,?,?)',(e.iso(NOW-dt.timedelta(days=1)),e.iso(NOW+dt.timedelta(days=7)),22.,None,'oauth',e.iso(NOW)))
        conn.commit();conn.close()
        self.sync();self.assertEqual(e.audit(self.root)['count'],a['count']+1)

    def test_checksum_tamper_detected_and_blocks_append(self):
        self.sync();p=e.files(self.root)[0]
        original=p.read_bytes();p.write_bytes(original.replace(b'24.0',b'42.0',1))
        with self.assertRaisesRegex(ValueError,'Tampered'):
            e.audit(self.root)
        with self.assertRaises(ValueError):self.sync()

    def test_torn_write_blocks_all_future_writes(self):
        self.sync();p=e.files(self.root)[0]
        with p.open('ab') as f:f.write(b'{"unfinished":')
        with self.assertRaisesRegex(ValueError,'Torn'):
            self.sync()

    def test_sensitive_fields_rejected(self):
        self.sync()
        with self.assertRaises(ValueError):e.valid_payload('quota.observation',{'token':'secret'})
        with self.assertRaises(ValueError):e.valid_payload('quota.alert',{'created_at':e.iso(NOW),'kind':'BURN_SPIKE','delivery':'PENDING','message':'secret'})
        self.assertNotIn(b'private message',e.files(self.root)[0].read_bytes())

    def test_projection_rebuild_from_authoritative_journal(self):
        self.sync();e.project(self.root)
        output=self.root/'ledger.sqlite3'
        conn=sqlite3.connect(output);self.assertEqual(conn.execute('select count(*) from events').fetchone()[0],3)
        conn.close();output.unlink()
        e.project(self.root);self.assertTrue(output.exists());self.assertEqual(output.stat().st_mode & 0o777,0o600)

    def test_checkpoint_detects_truncated_journal(self):
        self.sync();e.checkpoint(self.root)
        path=e.files(self.root)[0]
        lines=path.read_bytes().splitlines(keepends=True)
        path.write_bytes(b''.join(lines[:-1]))
        with self.assertRaisesRegex(ValueError,'Checkpoint'):e.audit(self.root)

    def test_fresh_checkpoint_verification(self):
        self.sync();a=e.checkpoint(self.root)
        self.assertEqual(a['status'],'CHECKPOINT_CREATED')
        self.assertEqual(e.audit(self.root)['count'],3)
        self.assertEqual(e.checkpoint(self.root)['status'],'ALREADY_CHECKPOINTED')

    def test_clock_skew_old_segment_rejected(self):
        self.sync()
        payload={'sampled_at':e.iso(NOW),'load_1m':1.,'load_5m':1.,'load_15m':1.,'disk_free_bytes':1,'disk_total_bytes':10}
        with e.locked(self.root):
            with self.assertRaisesRegex(ValueError,'Clock moved'):
                e.write_event(self.root,e.audit(self.root),'host.health',e.event_id('host.health','yesterday'),payload,recorded_at=NOW-dt.timedelta(days=1))

    def test_missing_governor_db_no_fake_zero(self):
        with self.assertRaises(FileNotFoundError):e.reconcile(self.root,'/path/does/not/exist')
        self.assertFalse((self.root/'journal').exists())

    def test_changed_source_same_identity_fails_closed(self):
        self.sync();tip=e.audit(self.root)['tip']
        con=sqlite3.connect(self.db)
        con.execute('UPDATE observations SET weekly_used_pct=99 WHERE weekly_used_pct=24')
        con.commit();con.close()
        with self.assertRaisesRegex(ValueError,'Conflicting'):self.sync()
        self.assertEqual(e.audit(self.root)['tip'],tip)

    def test_delivery_transition_yields_new_event_without_mutation(self):
        self.sync()
        con=sqlite3.connect(self.db)
        con.execute("UPDATE alerts SET delivery='GITHUB_SENT' WHERE id=1")
        con.commit();con.close()
        a=self.sync();self.assertEqual(a['appended']['quota.alert'],1)
        self.assertEqual(e.audit(self.root)['count'],4)

    def test_no_disk_space_partial_write_fails_closed(self):
        with patch('event_ledger.os.write',side_effect=OSError(28,'No space left on device')):
            with self.assertRaises(OSError):self.sync()
        self.assertEqual(e.audit(self.root)['count'],0)

    def test_readonly_source_governor_unchanged(self):
        before=self.db.read_bytes();self.sync()
        self.assertEqual(before,self.db.read_bytes())

    def test_filesystem_permissions(self):
        self.sync()
        self.assertEqual(self.root.stat().st_mode & 0o777,0o700)
        self.assertEqual(e.files(self.root)[0].stat().st_mode & 0o777,0o600)

    def test_permission_failure_no_fabricated_append(self):
        self.sync();tip=e.audit(self.root)['tip']
        with patch('event_ledger.os.open',side_effect=PermissionError('no access')):
            with self.assertRaises(PermissionError):self.sync()
        self.assertEqual(e.audit(self.root)['tip'],tip)

    def test_project_fails_closed_after_tamper(self):
        self.sync();e.project(self.root)
        p=e.files(self.root)[0];p.write_bytes(b'broken\n')
        with self.assertRaises(ValueError):e.project(self.root)
        self.assertTrue((self.root/'ledger.sqlite3').exists())

    def test_host_health_no_machine_identifiers(self):
        with patch('event_ledger.os.getloadavg',return_value=(1.0,2.0,3.0)):
            report=e.host_health(self.root,now=NOW)
        self.assertEqual(report['total'],1)
        data=e.files(self.root)[0].read_text()
        for private in (str(Path.home()),'pavelcherkashin','100.77.188.3'):
            self.assertNotIn(private,data)

    def test_cycle_partial_if_governor_unreadable(self):
        with patch('run_cycle.e.host_health',return_value={'status':'SYNCED'}),patch('run_cycle.e.project',return_value={'status':'PROJECTED'}),patch('run_cycle.e.checkpoint',return_value={'status':'CHECKPOINT_CREATED'}):
            with patch('run_cycle.e.reconcile',side_effect=FileNotFoundError('db')):
                import io
                from contextlib import redirect_stdout
                out=io.StringIO()
                with redirect_stdout(out): code=run_cycle.main(['--root',str(self.root),'--governor-db','/missing'])
                self.assertEqual(code,3)
                self.assertEqual(json.loads(out.getvalue())['status'],'PARTIAL')