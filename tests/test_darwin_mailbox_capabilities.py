import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_darwin_agent_mailbox import load, issue, m
import test_darwin_agent_mailbox as fixtures

cap = load('darwin-mailbox-capabilities')


def metadata(names=None, **scope_changes):
    names = ['loopback-user-service'] if names is None else names
    scope = {'application': 'example', 'port': 18765, 'operation': 'install',
             'serve_path': '/example/' if 'tailscale-serve-additive' in names else None}
    scope.update(scope_changes)
    return {'risk': 'R1', 'capabilities': json.dumps(names), 'capability_scope': json.dumps(scope)}


def capable(item, names=None):
    values = metadata(names)
    item['body'] = item['body'].replace('risk: R0', '\n'.join(k + ': ' + v for k, v in values.items()))
    return item


class DeclarationTests(unittest.TestCase):
    def test_legacy_has_no_capabilities_or_permission_override(self):
        watcher, dispatcher, _ = m.components()
        parsed, error = watcher.validate(m.REPOSITORY, issue())
        self.assertIsNone(error)
        self.assertEqual(cap.declaration(parsed), {'capabilities': [], 'capability_scope': None})
        self.assertEqual(dispatcher.codex_command('codex', Path('/test')),
                         load('wolfram-agent-dispatcher').codex_command('codex', Path('/test')))
        self.assertIn('Default: no listeners or infrastructure changes.', dispatcher.PREAMBLE)

    def test_single_and_both_allowlisted(self):
        watcher, _, _ = m.components()
        for names in (['loopback-user-service'], ['tailscale-serve-additive'], sorted(cap.ALLOWLIST)):
            parsed, error = watcher.validate(m.REPOSITORY, capable(issue(), names))
            self.assertIsNone(error)
            self.assertEqual(cap.declaration(parsed)['capabilities'], sorted(names))

    def test_unknown_public_funnel_listener_root_self_modification_absent(self):
        for value in ('public', 'funnel', 'lan', 'sudo', 'root', 'ssh', 'listener',
                      'infrastructure', 'mailbox-self-modification', 'tailscale-acl', 'tailscale-auth'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                cap.declaration(metadata([value]))

    def test_invalid_scope_risk_types_and_duplicates(self):
        variants = [dict(metadata(), risk='R0'), dict(metadata(), risk='R2'),
                    dict(metadata(), capabilities='[]'), dict(metadata(), capabilities='"loopback-user-service"'),
                    dict(metadata(), capabilities='["loopback-user-service","loopback-user-service"]'),
                    dict(metadata(), capabilities='[{}]'), metadata(port=80), metadata(port=True),
                    metadata(port=65536), metadata(application='../mailbox'), metadata(application='agent-mailbox'),
                    metadata(application='ssh-helper'), metadata(operation='shell'),
                    metadata(['tailscale-serve-additive'], serve_path='/'),
                    metadata(['tailscale-serve-additive'], serve_path='/../foo'),
                    metadata(serve_path='/unrequested/'),
                    dict(metadata(), capability_scope='{"port":1234,"port":4567}')]
        for value in variants:
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                cap.declaration(value)

    def test_ambiguous_yaml_duplicates_and_outside_declaration_fail(self):
        watcher, _, _ = m.components()
        body = capable(issue())['body']
        variants = [body.replace('capabilities: ["loopback-user-service"]', 'capabilities:\n  - loopback-user-service'),
                    body.replace('risk: R1', 'risk: R1\ncapabilities: []'),
                    issue()['body'] + '\ncapabilities: ["loopback-user-service"]',
                    body + '\n```yaml\nagent: codex@darwin.local\nstatus: ready\nrisk: R1\n```']
        for body in variants:
            self.assertIsNotNone(watcher.validate(m.REPOSITORY, issue(body=body))[1])

    def test_digest_and_envelope_binding(self):
        watcher, _, _ = m.components()
        original = issue()
        changed = capable(copy.deepcopy(original))
        digest = lambda item: hashlib.sha256(watcher.normalized_payload(m.REPOSITORY, item).encode()).hexdigest()
        self.assertNotEqual(digest(original), digest(changed))
        value = metadata()
        envelope = dict(cap.declaration(value), risk='R1')
        cap.bound(envelope, value)
        for change in ({'capabilities': []}, {'risk': 'R0'}, {'capability_scope': dict(envelope['capability_scope'], port=18766)}):
            with self.assertRaises(ValueError):
                cap.bound(dict(envelope, **change), value)

    def test_edited_source_rejected_and_comments_are_not_capabilities(self):
        watcher, _, _ = m.components()
        changed = capable(issue(lastEditedAt='2026-09-05T12:00:00Z'))
        self.assertEqual(watcher.validate(m.REPOSITORY, changed)[1], 'edited-or-unproven-source')
        item = issue(comments=[{'body': 'capabilities: ["loopback-user-service"]'}])
        parsed, _ = watcher.validate(m.REPOSITORY, item)
        self.assertEqual(cap.declaration(parsed)['capabilities'], [])

    def test_static_content_symlink_and_special_files_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'index.html').write_text('hello')
            self.assertEqual(len(cap.tree(root)), 1)
            (root / 'secret').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):
                cap.tree(root)

    def test_unrelated_handler_tcp_and_funnel_drift_rejected(self):
        before = {'TCP': {'443': {'HTTPS': True}}, 'Web': {'darwin.example.ts.net:443': {
            'Handlers': {'/other/': {'Proxy': 'http://127.0.0.1:9000'}}}}}
        after = copy.deepcopy(before)
        target = {'Proxy': 'http://127.0.0.1:18765'}
        after['Web']['darwin.example.ts.net:443']['Handlers']['/example/'] = target
        cap.route_delta(before, after, 'darwin.example.ts.net:443', '/example/', target)
        for mutate in ('handler', 'tcp', 'funnel', 'foreign'):
            wrong = copy.deepcopy(after)
            if mutate == 'handler':
                wrong['Web']['darwin.example.ts.net:443']['Handlers']['/other/'] = target
            elif mutate == 'tcp':
                wrong['TCP']['9999'] = {'TCPForward': 'localhost:22'}
            elif mutate == 'foreign':
                wrong['Web']['foreign:443'] = {'Handlers': {'/': target}}
            else:
                wrong['AllowFunnel'] = {'darwin.example.ts.net:443': True}
            with self.assertRaises(ValueError):
                cap.route_delta(before, wrong, 'darwin.example.ts.net:443', '/example/', target)
        cap.route_delta({}, {'TCP': {'443': {'HTTPS': True}}, 'Web': {'darwin.example.ts.net:443': {
            'Handlers': {'/example/': target}}}}, 'darwin.example.ts.net:443', '/example/', target)

    def test_unsupported_serve_schema_and_funnel_rejected(self):
        for value in ({'AllowFunnel': {'node:443': True}}, {'Foreground': {'x': {}}}, {'Services': {}}):
            with patch.object(cap, 'command', return_value=json.dumps(value)), self.assertRaises(ValueError):
                cap.serve_config()


class CapabilityIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.DarwinTests()
        self.fixture.setUp()
        self.f = self.fixture
        capable(self.f.item)
        original = m.load
        self.module = original('darwin-mailbox-capabilities')
        self.loader = patch.object(m, 'load', side_effect=lambda name: self.module if name == 'darwin-mailbox-capabilities' else original(name))
        self.loader.start()
        self.capture = patch.object(self.module, 'capture', return_value={'unchanged': True})
        self.capture.start()
        self.source = patch.object(m, 'fresh_issue', return_value=self.f.item)
        self.source.start()

    def tearDown(self):
        self.source.stop()
        self.capture.stop()
        self.loader.stop()
        self.f.tearDown()

    def test_broker_bound_success_and_repeat_does_not_reexecute(self):
        checks = dict.fromkeys(('capability-envelope-bound', 'loopback-only', 'rollback-plan-verified'), 'pass')
        with patch.object(self.module, 'apply', return_value=checks) as apply:
            self.assertEqual(self.f.cycle(), {'execution_finished': 1})
            env = json.loads((self.f.run_dir() / 'envelope.json').read_text())
            self.assertEqual(env['capabilities'], ['loopback-user-service'])
            self.assertEqual(apply.call_count, 1)
            self.assertIn('\nTASK_COMPLETED\n', self.f.client.posts[-1])
            self.f.cycle()
            self.assertEqual(apply.call_count, 1)

    def test_broker_failure_cannot_complete_or_retry(self):
        with patch.object(self.module, 'apply', side_effect=ValueError('scope drift')) as apply:
            self.assertEqual(self.f.cycle(), {'execution_failed': 1})
            self.assertFalse(any('\nTASK_COMPLETED\n' in p for p in self.f.client.posts))
            self.f.cycle()
            self.assertEqual(apply.call_count, 1)

    def test_envelope_tampering_prevents_broker(self):
        text = self.f.fake.read_text()
        self.f.fake.write_text(text.replace('path.write_text(json.dumps(value))',
            'path.write_text(json.dumps(value))\np=path.parent/"envelope.json"\ne=json.loads(p.read_text())\ne["capabilities"]=[]\np.chmod(0o600)\np.write_text(json.dumps(e))'))
        with patch.object(self.module, 'apply') as apply:
            self.assertEqual(self.f.cycle(), {'execution_failed': 1})
            apply.assert_not_called()

    def test_scope_drift_before_broker_prevents_completion(self):
        with patch.object(self.module, 'verify_unchanged', side_effect=ValueError('protected runtime changed')), \
             patch.object(self.module, 'apply') as apply:
            self.assertEqual(self.f.cycle(), {'execution_failed': 1})
            apply.assert_not_called()

    def test_capability_added_before_claim_rejected(self):
        original = issue()
        with self.assertRaises(ValueError):
            self.f.cycle(items=[original], fresh=self.f.item)
        self.assertFalse((self.f.base / 'state/claims').exists())

    def test_post_execution_broker_error_retains_log_bounds(self):
        self.f.fake.write_text(self.f.fake.read_text() + '\nsys.stderr.write("x"*2000000)\n')
        with patch.object(self.module, 'apply', side_effect=ValueError('broker refused')):
            self.assertEqual(self.f.cycle(), {'execution_failed': 1})
        self.assertLessEqual((self.f.run_dir() / 'codex.stderr.log').stat().st_size, m.LOG_LIMIT)

    def test_failed_worker_check_cannot_trigger_broker(self):
        self.f.fake.write_text(self.f.fake.read_text().replace('"name":"identity","status":"pass"',
                                                              '"name":"identity","status":"fail"'))
        with patch.object(self.module, 'apply') as apply:
            self.assertEqual(self.f.cycle(), {'execution_failed': 1})
            apply.assert_not_called()

    def test_legacy_worker_mailbox_self_modification_is_detected(self):
        self.f.item = issue()
        self.f.client = fixtures.Client(self.f.item)
        code = self.f.fake.read_text()
        code += '\n(path.parents[4]/"config/policy.yaml").write_text("tampered")\n'
        self.f.fake.write_text(code)
        self.assertEqual(self.f.cycle(), {'execution_failed': 1})
        self.assertFalse(any('TASK_COMPLETED' in p for p in self.f.client.posts))
        self.assertTrue((self.f.base / 'state/claims/DARWIN-TEST-1.json').exists())

    def test_reporter_rejects_envelope_and_admission_tampering(self):
        checks = dict.fromkeys(('capability-envelope-bound', 'loopback-only', 'rollback-plan-verified'), 'pass')
        with patch.object(self.module, 'apply', return_value=checks):
            self.f.cycle()
        watcher, _, reporter = m.components()
        run = self.f.run_dir()
        path = run / 'envelope.json'
        envelope = json.loads(path.read_text())
        envelope['capabilities'] = ['tailscale-serve-additive']
        path.chmod(0o600)
        path.write_text(json.dumps(envelope))
        self.assertEqual(m.publish(run, 'CLAIMED', watcher, reporter, self.f.client), 'writeback_failed')

class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name).resolve()
        self.base = self.home / 'mailbox'
        self.work = self.home / 'run'
        self.work.mkdir()
        (self.home / 'Library/LaunchAgents').mkdir(parents=True)
        (self.work / 'service-content').mkdir()
        (self.work / 'service-content/index.html').write_text('harmless fixture')
        self.running = False
        self.config = {'TCP': {'443': {'HTTPS': True}}, 'Web': {'darwin.example.ts.net:443': {
            'Handlers': {'/existing/': {'Proxy': 'http://127.0.0.1:9000'}}}}}
        self.original_config = copy.deepcopy(self.config)
        self.commands = []
        self.sequence = 0
        self.patches = [patch.object(cap.Path, 'home', return_value=self.home),
            patch.object(cap.sys, 'platform', 'darwin'), patch.object(cap.os, 'getuid', return_value=501),
            patch.object(cap, 'command', side_effect=self.command),
            patch.object(cap.subprocess, 'run', side_effect=self.lsof),
            patch.object(cap.urllib.request, 'build_opener', side_effect=self.opener)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def envelope(self, names=None, operation='install'):
        self.sequence += 1
        values = metadata(names, operation=operation)
        result = dict(cap.declaration(values), task_id='FRESH-' + str(self.sequence),
                      lease_id=format(self.sequence, '032x'), source_sha256='a' * 64, work_dir=str(self.work))
        (self.work / 'capability-request.json').write_text(json.dumps({k: v for k, v in result.items() if k != 'work_dir'}))
        return result

    def command(self, args):
        self.commands.append(args)
        if args[:3] == ['tailscale', 'serve', 'status']:
            return json.dumps(self.config)
        if args[:2] == ['tailscale', 'status']:
            return json.dumps({'BackendState': 'Running', 'Self': {'DNSName': 'darwin.example.ts.net.'}})
        if args == ['tailscale', 'serve', '--help']:
            return '--set-path --https --bg'
        if args[:2] == ['tailscale', 'serve']:
            handlers = self.config['Web']['darwin.example.ts.net:443']['Handlers']
            if args[-1] == 'off':
                handlers.pop('/example/', None)
            else:
                handlers['/example/'] = {'Proxy': args[-1]}
            return ''
        if args[0] == 'launchctl':
            self.running = args[1] == 'bootstrap'
            return ''
        if args[0] == '/usr/sbin/lsof':
            if not self.running:
                raise cap.subprocess.CalledProcessError(1, args)
            return 'p123\nn127.0.0.1:18765\n'
        raise AssertionError(args)

    def lsof(self, args, **kwargs):
        self.assertEqual(args[0], '/usr/sbin/lsof')
        return type('Result', (), {'returncode': 0 if self.running else 1,
                                   'stdout': 'occupied' if self.running else '', 'stderr': ''})()

    def opener(self, *args):
        data = (self.base / 'services/example/content/index.html').read_bytes()
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, limit): return data[:limit]
        class Opener:
            def open(self, *args, **kwargs): return Response()
        return Opener()

    def test_loopback_install_update_remove_only_compiled_commands(self):
        cap.apply(self.envelope(), self.base)
        self.assertTrue(self.running)
        (self.work / 'service-content/index.html').write_text('updated fixture')
        cap.apply(self.envelope(), self.base)
        self.assertEqual((self.base / 'services/example/content/index.html').read_text(), 'updated fixture')
        cap.apply(self.envelope(operation='remove'), self.base)
        self.assertFalse(self.running)
        self.assertFalse((self.base / 'services/example').exists())
        self.assertTrue(all(cmd[:3] == ['tailscale', 'serve', 'status']
                            for cmd in self.commands if cmd[0] == 'tailscale'))
        self.assertTrue(all(cmd[0] in ('launchctl', '/usr/sbin/lsof', 'tailscale') for cmd in self.commands))

    def test_combined_preserves_unrelated_and_removes_only_owned_handler(self):
        names = sorted(cap.ALLOWLIST)
        cap.apply(self.envelope(names), self.base)
        self.assertIn('/example/', self.config['Web']['darwin.example.ts.net:443']['Handlers'])
        cap.apply(self.envelope(names, operation='remove'), self.base)
        self.assertEqual(self.config, self.original_config)
        self.assertFalse(self.running)

    def test_serve_only_targets_existing_owned_loopback(self):
        cap.apply(self.envelope(), self.base)
        cap.apply(self.envelope(['tailscale-serve-additive']), self.base)
        self.assertTrue(self.running)
        cap.apply(self.envelope(['tailscale-serve-additive'], operation='remove'), self.base)
        self.assertTrue(self.running)
        self.assertEqual(self.config, self.original_config)

    def test_unowned_serve_only_fails_before_commands(self):
        with self.assertRaisesRegex(ValueError, 'unowned'):
            cap.apply(self.envelope(['tailscale-serve-additive']), self.base)
        self.assertEqual(self.commands, [])

    def test_loopback_only_cannot_activate_dormant_serve_or_funnel_target(self):
        self.config['Web']['darwin.example.ts.net:443']['Handlers']['/foreign/'] = {
            'Proxy': 'http://127.0.0.1:18765'}
        with self.assertRaisesRegex(ValueError, 'unowned Serve'):
            cap.apply(self.envelope(), self.base)
        self.assertFalse(self.running)
        self.config['AllowFunnel'] = {'darwin.example.ts.net:443': True}
        with self.assertRaisesRegex(ValueError, 'Funnel'):
            cap.apply(self.envelope(), self.base)
        self.assertFalse(self.running)

    def test_route_collision_is_not_replaced(self):
        self.config['Web']['darwin.example.ts.net:443']['Handlers']['/example/'] = {'Proxy': 'http://127.0.0.1:22'}
        before = copy.deepcopy(self.config)
        with self.assertRaisesRegex(ValueError, 'collision'):
            cap.apply(self.envelope(sorted(cap.ALLOWLIST)), self.base)
        self.assertEqual(self.config, before)
        self.assertFalse(self.running)
        self.assertFalse((self.base / 'services/example').exists())

    def test_failed_route_mutation_rolls_back_preview(self):
        original = self.command
        def command(args):
            if args[:2] == ['tailscale', 'serve'] and args[-1].startswith('http:'):
                raise cap.subprocess.CalledProcessError(1, args)
            return original(args)
        with patch.object(cap, 'command', side_effect=command), self.assertRaises(cap.subprocess.CalledProcessError):
            cap.apply(self.envelope(sorted(cap.ALLOWLIST)), self.base)
        self.assertEqual(self.config, self.original_config)
        self.assertFalse(self.running)
        self.assertFalse((self.base / 'services/example').exists())

    def test_failed_update_restores_previous_content_and_service(self):
        cap.apply(self.envelope(), self.base)
        (self.work / 'service-content/index.html').write_text('new fixture')
        original = self.command
        failed = False
        def command(args):
            nonlocal failed
            if args[:2] == ['launchctl', 'bootstrap'] and not failed:
                failed = True
                raise cap.subprocess.CalledProcessError(1, args)
            return original(args)
        with patch.object(cap, 'command', side_effect=command), self.assertRaises(cap.subprocess.CalledProcessError):
            cap.apply(self.envelope(), self.base)
        self.assertTrue(self.running)
        self.assertEqual((self.base / 'services/example/content/index.html').read_text(), 'harmless fixture')

    def test_forged_request_never_runs_commands(self):
        envelope = self.envelope()
        path = self.work / 'capability-request.json'
        request = json.loads(path.read_text())
        request['source_sha256'] = 'b' * 64
        path.write_text(json.dumps(request))
        with self.assertRaisesRegex(ValueError, 'bound'):
            cap.apply(envelope, self.base)
        self.assertEqual(self.commands, [])


if __name__ == '__main__':
    unittest.main()
