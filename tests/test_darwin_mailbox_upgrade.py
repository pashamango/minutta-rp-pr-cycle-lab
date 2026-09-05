import base64
import copy
import json
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

from test_darwin_agent_mailbox import load, ROOT

u = load('darwin-mailbox-upgrade')


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve() / 'mailbox'
        self.plist = self.base.parent / 'LaunchAgents/darwin.plist'
        self.control = self.base / 'state/control'
        self.control.mkdir(parents=True)
        self.plist.parent.mkdir()
        self.old, self.new, self.head = 'a' * 40, 'b' * 40, 'c' * 40
        self.files = {name: (ROOT / name).read_bytes() for name in u.FILES}
        old_files = {name: self.files[name] for name in u.manager.FILES}
        for name, data in old_files.items():
            path = self.base / 'releases' / self.old / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (self.base / 'config').mkdir()
        (self.base / 'config/policy.yaml').write_bytes(old_files['config/darwin-agent-mailbox-policy.yaml'])
        self.manifest = {'merged_commit': self.old, 'files': {k: u.sha(v) for k, v in old_files.items()}}
        (self.control / 'installation.json').write_text(json.dumps(self.manifest))
        activation = {'activated_at': '2026-09-05T01:00:00Z', 'last_existing_issue': 50,
                      'mode': 'normal', 'smoke_verified_at': '2026-09-05T02:00:00Z', 'smoke_task_id': 'ORIGINAL'}
        (self.control / 'activation.json').write_text(json.dumps(activation))
        for number in (55, 56, 57, 58):
            for directory in ('claims', 'runs', 'inbox', 'seen'):
                path = self.base / 'state' / directory / str(number)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('original evidence ' + str(number))
        self.value = {'Label': u.LABEL, 'ProgramArguments': ['/usr/bin/python3', str(self.base / 'releases' / self.old / 'tools/darwin-agent-mailbox')],
            'WorkingDirectory': str(self.base), 'StartInterval': 60, 'RunAtLoad': True,
            'EnvironmentVariables': {'PATH': '/existing/path'}, 'Umask': 63,
            'StandardOutPath': '/dev/null', 'StandardErrorPath': '/dev/null'}
        self.old_plist = plistlib.dumps(self.value, sort_keys=True)
        self.plist.write_bytes(self.old_plist)
        self.before = u.history(self.base)
        self.loaded = True
        self.calls = []
        self.patches = [patch.object(u, 'local_host'), patch.object(u, 'verified', return_value=(self.new, self.files)),
            patch.object(u.manager, 'launch_status', side_effect=lambda: self.loaded),
            patch.object(u, 'launch', side_effect=self.launch),
            patch.object(u.subprocess, 'run', side_effect=self.subprocess)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def launch(self, *args):
        self.calls.append(args)
        self.loaded = args[0] == 'bootstrap'

    def subprocess(self, args, **kwargs):
        # The only subprocess in mocked upgrade is the staged installed offline smoke.
        self.assertEqual(args[-1], 'smoke')
        return type('Result', (), {'stdout': json.dumps(u.smoke(self.base))})()

    def test_upgrade_preserves_all_history_and_original_manifest(self):
        manifest = (self.control / 'installation.json').read_bytes()
        result = u.upgrade(59, self.head, self.base, self.plist)
        self.assertEqual(result['status'], 'upgraded')
        self.assertEqual(u.history(self.base), self.before)
        self.assertEqual((self.control / 'installation.json').read_bytes(), manifest)
        self.assertEqual(plistlib.loads(self.plist.read_bytes())['ProgramArguments'][1],
                         str(self.base / 'releases' / self.new / 'tools/darwin-agent-mailbox'))
        self.assertFalse((self.control / 'disabled.json').exists())
        self.assertEqual(len(self.calls), 2)
        self.assertTrue(all('wolfram' not in str(c) for c in self.calls))

    def test_failed_installed_smoke_restores_whole_old_pointer(self):
        with patch.object(u.subprocess, 'run', side_effect=RuntimeError('smoke failed')):
            with self.assertRaises(RuntimeError):
                u.upgrade(59, self.head, self.base, self.plist)
        self.assertEqual(self.plist.read_bytes(), self.old_plist)
        self.assertEqual(u.history(self.base), self.before)
        self.assertEqual(json.loads((self.control / 'upgrade.json').read_text())['status'], 'rolled-back')
        self.assertFalse((self.control / 'disabled.json').exists())

    def test_failed_recovery_leaves_disable_gate(self):
        def fail(*args):
            if args[0] == 'bootstrap':
                raise RuntimeError('launchd unavailable')
            self.launch(*args)
        with patch.object(u, 'launch', side_effect=fail), self.assertRaises(RuntimeError):
            u.upgrade(59, self.head, self.base, self.plist)
        self.assertTrue((self.control / 'disabled.json').exists())
        self.assertEqual(self.plist.read_bytes(), self.old_plist)
        self.assertEqual(u.history(self.base), self.before)

    def test_rollback_preserves_new_claims_after_upgrade(self):
        u.upgrade(59, self.head, self.base, self.plist)
        (self.base / 'state/claims/FRESH').write_text('new permanent claim')
        after = u.history(self.base)
        result = u.rollback(self.base, self.plist)
        self.assertEqual(result['status'], 'rolled-back')
        self.assertEqual(self.plist.read_bytes(), self.old_plist)
        self.assertEqual(u.history(self.base), after)

    def test_installed_bytes_drift_aborts_before_pointer_changes(self):
        (self.base / 'releases' / self.old / 'tools/darwin-agent-mailbox').write_text('drift')
        with self.assertRaisesRegex(ValueError, 'installed bytes'):
            u.upgrade(59, self.head, self.base, self.plist)
        self.assertEqual(self.plist.read_bytes(), self.old_plist)
        self.assertFalse((self.control / 'upgrade.json').exists())
        self.assertEqual(self.calls, [])

    def test_symlink_and_foreign_launchagent_fail(self):
        self.value['ProgramArguments'][1] = '/foreign/runtime'
        self.plist.write_bytes(plistlib.dumps(self.value))
        with self.assertRaisesRegex(ValueError, 'not owned'):
            u.upgrade(59, self.head, self.base, self.plist)
        self.assertEqual(self.calls, [])

    def test_busy_cycle_never_stops_active_task(self):
        with u.m.locked(self.control / 'cycle.lock') as acquired:
            self.assertTrue(acquired)
            with self.assertRaisesRegex(ValueError, 'busy'):
                u.upgrade(59, self.head, self.base, self.plist)
        self.assertEqual(self.calls, [])

    def test_smoke_no_dispatch_queue_codex_or_mutation(self):
        with patch.object(u.m, 'cycle', side_effect=AssertionError('no cycle')), \
             patch.object(u.m, 'issues', side_effect=AssertionError('no GitHub')):
            result = u.smoke(self.base)
        self.assertEqual(result['historical-execution-count'], 0)
        self.assertEqual(u.history(self.base), self.before)
        self.assertEqual(self.calls, [])

    def test_interrupted_pointer_recovers_using_journal(self):
        # Simulate power loss after atomic pointer switch: gate + journal remain.
        u.upgrade(59, self.head, self.base, self.plist)
        journal = json.loads((self.control / 'upgrade.json').read_text())
        journal['status'] = 'prepared'
        (self.control / 'upgrade.json').write_text(json.dumps(journal))
        (self.control / 'disabled.json').write_bytes(b'{"disabled":true}\n')
        u.rollback(self.base, self.plist)
        self.assertEqual(self.plist.read_bytes(), self.old_plist)
        self.assertEqual(u.history(self.base), self.before)
        self.assertFalse((self.control / 'disabled.json').exists())


class UpgradeIdentityTests(unittest.TestCase):
    def test_actual_pr_branch_head_merge_and_head_ancestry(self):
        head, merged = 'a' * 40, 'b' * 40
        valid = {'number': 59, 'state': 'closed', 'merged': True, 'merge_commit_sha': merged,
            'head': {'sha': head, 'ref': u.BRANCH, 'repo': {'full_name': u.REPO}},
            'base': {'ref': 'main', 'repo': {'full_name': u.REPO}}}
        calls = []
        def api(args):
            calls.append(args[-1])
            return {'status': 'ahead'} if '/compare/' in args[-1] else valid
        self.assertEqual(u.checked(59, head, api), merged)
        self.assertTrue(any(head + '...main' in c for c in calls))
        for field, value in (('number', 60), ('state', 'open'), ('merged', False)):
            bad = dict(valid, **{field: value})
            with self.assertRaises(ValueError):
                u.checked(59, head, lambda args: bad)
        for section, key, value in (('head', 'sha', 'c' * 40), ('head', 'ref', 'other'),
                                   ('base', 'ref', 'develop'), ('head', 'repo', {'full_name': 'evil/repo'})):
            bad = copy.deepcopy(valid)
            bad[section][key] = value
            with self.assertRaises(ValueError):
                u.checked(59, head, lambda args: bad)
        with self.assertRaises(ValueError):
            u.checked(59, head, lambda args: {'status': 'diverged'} if '/compare/' in args[-1] else valid)

if __name__ == '__main__':
    unittest.main()
