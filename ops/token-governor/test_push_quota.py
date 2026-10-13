import datetime as dt
import json
from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import patch
import push_quota
import governor

NOW=dt.datetime(2026,10,13,20,0,tzinfo=dt.timezone.utc)

def sample(offset=0):
    return {'schema':governor.SCHEMA,'provider':'codex','source':'oauth',
            'observed_at':governor.iso(NOW-dt.timedelta(minutes=offset)),
            'collected_at':governor.iso(NOW),
            'weekly_used_pct':18.0,'weekly_reset_at':governor.iso(NOW+dt.timedelta(days=3)),
            'session_used_pct':None,'session_reset_at':None,
            'attribution':'UNATTRIBUTED_CLOUD_WORK'}

class PushTests(TestCase):
    def test_spool_is_deduplicated_and_sanitized(self):
        with tempfile.TemporaryDirectory() as d:
            a=push_quota.spool_sample(sample(5),d)
            b=push_quota.spool_sample(sample(5),d)
            self.assertEqual(a,b)
            self.assertEqual(len(list((Path(d)/'pending').glob('*.json'))),1)

    def test_retry_same_observation_new_collection_time_deduped(self):
        with tempfile.TemporaryDirectory() as d:
            a = sample(5)
            b = dict(a)
            b['collected_at'] = governor.iso(NOW+dt.timedelta(minutes=1))
            push_quota.spool_sample(a, d)
            push_quota.spool_sample(b, d)
            self.assertEqual(len(list((Path(d)/'pending').glob('*.json'))),1)

    def test_ship_success_alert_exit2(self):
        with patch('push_quota.subprocess.run') as run:
            run.return_value=type('Resp',(),{'returncode':2,'stdout':'{"status":"LOW_BUDGET"}'})()
            self.assertEqual(push_quota.ship('user@100.112.18.4','{}'),'ACKED')
            self.assertIn('StrictHostKeyChecking=yes',run.call_args.args[0])

    def test_ship_fails_closed(self):
        with patch('push_quota.subprocess.run') as run:
            run.return_value=type('Resp',(),{'returncode':255,'stdout':'ssh error'})()
            self.assertEqual(push_quota.ship('user@100.112.18.4','{}'),'TRANSPORT_UNAVAILABLE')

    def test_run_queues_on_network_failure(self):
        with tempfile.TemporaryDirectory() as d,patch('push_quota.probe',return_value=sample(3)),patch('push_quota.ship',return_value='TRANSPORT_UNAVAILABLE'):
            result=push_quota.run('user@100.112.18.4',d,now=NOW)
            self.assertEqual(result['status'],'PENDING')
            self.assertEqual(result['pending_count'],1)

    def test_run_delivers_and_archives(self):
        with tempfile.TemporaryDirectory() as d,patch('push_quota.probe',return_value=sample(3)),patch('push_quota.ship',return_value='ACKED'):
            result=push_quota.run('user@100.112.18.4',d,now=NOW)
            self.assertEqual(result['status'],'DELIVERED')
            self.assertEqual(len(list((Path(d)/'sent').glob('*.json'))),1)

    def test_run_old_sample_not_falsely_delivered(self):
        with tempfile.TemporaryDirectory() as d,patch('push_quota.probe',return_value=sample(120)),patch('push_quota.ship') as ship:
            result=push_quota.run('user@100.112.18.4',d,now=NOW)
            self.assertEqual(result['expired_count'],1)
            ship.assert_not_called()

    def test_probe_failure_no_false_success(self):
        with tempfile.TemporaryDirectory() as d,patch('push_quota.probe',return_value=None):
            result=push_quota.run('user@100.112.18.4',d,now=NOW)
            self.assertEqual(result['status'],'PROBE_UNAVAILABLE')
            self.assertEqual(result['delivered_count'],0)

    def test_reject_host_option_injection(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                push_quota.run('-oProxyCommand=user@x',d,now=NOW)