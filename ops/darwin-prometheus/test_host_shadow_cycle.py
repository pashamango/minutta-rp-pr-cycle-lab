"""DP-01B SHADOW-only transport and launchd tests (no macOS required)."""
import datetime as dt
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import plistlib

import event_ledger as e
import host_adapter as a
import host_shadow_cycle as h
import install_host_shadow_launchagent as launch

UTC=dt.timezone.utc


def dummy(at='2026-10-13T22:16:00Z'):
    return {'schema':a.SCHEMA, 'node_role':'darwin','sampled_at':at,
            'metrics_status':{'load':'SOURCE_READ_LOCAL','cpu':'SOURCE_READ_LOCAL',
                              'disk':'SOURCE_READ_LOCAL','swap':'READ_BLOCKED'},
            'services':dict.fromkeys(a.SERVICES,'READ_BLOCKED'),
            'cpu_logical':4,'load_1m':1.0,'load_5m':0.5,'load_15m':0.2,
            'swap_used_bytes':None,'swap_total_bytes':None,
            'disk_free_bytes':1000,'disk_total_bytes':2000}


class ShadowTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.base=Path(self.t.name)
        self.old=self.base/'production'
        self.shadow=self.base/'shadow'
        self.old.mkdir()
        # Snapshot of production directory must remain byte-for-byte untouched.
        self.old.joinpath('sentinel').write_bytes(b'original E1 production ledger')
        self.addCleanup(patch.stopall)
        p=patch.object(h,'PRODUCTION_ROOT',str(self.old));p.start()

    def test_one_realistic_snapshot_in_shadow(self):
        with patch.object(a,'collect',return_value=dummy()):
            out=h.run(str(self.shadow))
        self.assertEqual(out['status'],'VERIFIED')
        self.assertEqual(out['events'],1)
        self.assertEqual(out['production_e1_touched'],False)
        self.assertEqual(e.audit(self.shadow)['types'],{'host.snapshot':1})
        self.assertEqual(self.old.joinpath('sentinel').read_bytes(),b'original E1 production ledger')
        self.assertEqual(list(self.old.iterdir()),[self.old/'sentinel'])

    def test_dedupe(self):
        with patch.object(a,'collect',return_value=dummy()):
            h.run(str(self.shadow))
            out=h.run(str(self.shadow))
        self.assertEqual(out['events'],1)
        self.assertEqual(out['event_status'],'DUPLICATE')

    def test_second_observation(self):
        with patch.object(a,'collect',side_effect=[dummy(),dummy('2026-10-13T23:16:00Z')]):
            h.run(str(self.shadow));o=h.run(str(self.shadow))
        self.assertEqual(o['events'],2)
        self.assertEqual(e.audit(self.shadow)['count'],2)

    def test_production_root_blocked(self):
        with self.assertRaises(ValueError):h.run(str(self.old))
        self.assertEqual(list(self.old.iterdir()),[self.old/'sentinel'])

    def test_production_child_blocked(self):
        with self.assertRaises(ValueError):h.run(str(self.old/'shadow'))
        self.assertEqual(list(self.old.iterdir()),[self.old/'sentinel'])

    def test_production_parent_blocked(self):
        with self.assertRaises(ValueError):h.run(str(self.base))

    def test_symlink_alias_blocked(self):
        alias=self.base/'alias';alias.symlink_to(self.old,target_is_directory=True)
        with self.assertRaises(ValueError):h.run(str(alias))

    def test_failure_does_not_touch_original(self):
        with patch.object(a,'collect',side_effect=RuntimeError('source denied')):
            with self.assertRaises(RuntimeError):h.run(str(self.shadow))
        self.assertEqual(self.old.joinpath('sentinel').read_bytes(),b'original E1 production ledger')

    def test_corruption_prevents_second_write(self):
        with patch.object(a,'collect',return_value=dummy()):h.run(str(self.shadow))
        p=e.files(self.shadow)[0];p.write_bytes(p.read_bytes()+b'bad')
        with patch.object(a,'collect',return_value=dummy('2026-10-13T23:16:00Z')):
            with self.assertRaises(ValueError):h.run(str(self.shadow))
        self.assertEqual(self.old.joinpath('sentinel').read_bytes(),b'original E1 production ledger')

    def test_launchd_label_distinct(self):
        self.assertNotEqual(launch.LABEL,'org.chitakasha.darwin-prometheus-ledger')
        x=launch.plan(home=self.base,python='/bin/python3')
        self.assertEqual(x['StartInterval'],3600)
        self.assertTrue(x['RunAtLoad'])
        self.assertEqual(x['ProgramArguments'][1],str(self.base/'darwin-prometheus-dp01b-shadow'/'host_shadow_cycle.py'))

    def test_installer_is_create_only(self):
        path=self.base/'darwin-prometheus-dp01b-shadow'/'host_shadow_cycle.py';path.parent.mkdir(parents=True);path.touch()
        r=launch.install(home=self.base,python='/bin/python3')
        self.assertEqual(r['status'],'PLIST_CREATED_UNLOADED')
        fp=self.base/'Library'/'LaunchAgents'/(launch.LABEL+'.plist')
        self.assertEqual(fp.stat().st_mode&0o777,0o600)
        self.assertEqual(plistlib.loads(fp.read_bytes())['Label'],launch.LABEL)
        with self.assertRaises(FileExistsError):launch.install(home=self.base,python='/bin/python3')


if __name__=='__main__':unittest.main()