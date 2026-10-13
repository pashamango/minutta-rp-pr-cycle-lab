#!/usr/bin/env python3
"""DP-01B read-only macOS host snapshot adapter (stdlib only).

`collect` works on a host without the ledger; `ingest` runs on Darwin.
All output is schema-allowlisted: no usernames, hostnames, IPs, log lines,
credential-bearing subprocess output, or SSH authority is exported.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys

SCHEMA = 'chitakasha.prometheus.host-snapshot/v1'
ROLES = {'darwin', 'wolfram'}
STATUSES = {'SOURCE_READ_LOCAL', 'READ_BLOCKED', 'NOT_SUPPORTED'}
SERVICES = ('tailscale', 'forgejo', 'ollama', 'governor_push', 'prometheus_ledger')
SERVICE_STATES = {'BACKEND_RUNNING', 'BACKEND_STOPPED', 'TCP_ACCEPTING',
                  'TCP_REFUSED', 'LAUNCHD_REGISTERED', 'NOT_CONFIGURED',
                  'READ_BLOCKED'}
SWAP_RE = re.compile(r'\b(total|used)\s*=\s*(\d+(?:\.\d+)?)\s*([KMGT])\b')


def cmd(args, timeout=4, env=None):
    """Execute fixed literal commands. Raw stderr is never logged or relayed."""
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                              check=False, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return None


def swap_usage():
    p = cmd(['/usr/sbin/sysctl', '-n', 'vm.swapusage'])
    if p is None or p.returncode != 0 or len(p.stdout) > 1024:
        return None
    vals={}
    for name, number, unit in SWAP_RE.findall(p.stdout):
        vals[name]=int(float(number) * (1024 ** ('KMGT'.index(unit)+1)))
    if set(vals) != {'total','used'} or vals['used'] > vals['total']:
        return None
    return vals['used'], vals['total']


def tcp_local(port):
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=1):
            return 'TCP_ACCEPTING'  # NOT proof of application health
    except ConnectionRefusedError:
        return 'TCP_REFUSED'
    except OSError:
        return 'READ_BLOCKED'


def tailscale():
    cli=Path('/Applications/Tailscale.app/Contents/MacOS/Tailscale')
    if not cli.is_file():
        return 'NOT_CONFIGURED'
    p=cmd([str(cli), 'status', '--json'], timeout=5,
          env={**os.environ, 'TAILSCALE_BE_CLI':'1'})
    if p is None or p.returncode != 0 or len(p.stdout)>1_000_000:
        return 'READ_BLOCKED'
    try:
        state=json.loads(p.stdout).get('BackendState')
    except (json.JSONDecodeError, AttributeError):
        return 'READ_BLOCKED'
    return ('BACKEND_RUNNING' if state == 'Running' else
            'BACKEND_STOPPED' if state in ('Stopped','NeedsLogin') else
            'READ_BLOCKED')


def launchd(label):
    p=cmd(['/bin/launchctl','print',f'gui/{os.getuid()}/{label}'])
    # A registered idle StartInterval job can be inactive, yet healthy.
    # Never classify a successful launchctl print as a running process.
    return 'LAUNCHD_REGISTERED' if p is not None and p.returncode == 0 else 'READ_BLOCKED'


def collect(role, now=None):
    if role not in ROLES: raise ValueError('Unknown role')
    now=now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:raise ValueError('Timezone required')
    metrics_status={}; vals={}
    try:
        a=os.getloadavg()
        if len(a)!=3 or not all(isinstance(v,(int,float)) and 0<=v<=100000 for v in a):
            raise ValueError('Invalid load')
        vals.update(zip(('load_1m','load_5m','load_15m'),(round(x,3) for x in a)))
        metrics_status['load']='SOURCE_READ_LOCAL'
    except (AttributeError,OSError,ValueError):
        vals.update({k:None for k in ('load_1m','load_5m','load_15m')})
        metrics_status['load']='READ_BLOCKED'
    cpu=os.cpu_count()
    vals['cpu_logical']=cpu if type(cpu) is int and 0<cpu<4096 else None
    metrics_status['cpu']='SOURCE_READ_LOCAL' if vals['cpu_logical'] is not None else 'READ_BLOCKED'
    try:
        d=shutil.disk_usage(str(Path.home()))
        vals['disk_free_bytes'], vals['disk_total_bytes']=d.free,d.total
        metrics_status['disk']='SOURCE_READ_LOCAL'
    except OSError:
        vals['disk_free_bytes']=vals['disk_total_bytes']=None
        metrics_status['disk']='READ_BLOCKED'
    swap=swap_usage() if sys.platform=='darwin' else None
    vals['swap_used_bytes'], vals['swap_total_bytes']=swap if swap else (None,None)
    metrics_status['swap']=('SOURCE_READ_LOCAL' if swap else
                             'READ_BLOCKED' if sys.platform=='darwin' else 'NOT_SUPPORTED')
    services={
      'tailscale':tailscale() if sys.platform=='darwin' else 'NOT_CONFIGURED',
      'forgejo':tcp_local(3001),
      'ollama':tcp_local(11434),
      'governor_push':launchd('com.chitakasha.token-governor-push') if sys.platform=='darwin' else 'READ_BLOCKED',
      'prometheus_ledger':launchd('org.chitakasha.darwin-prometheus-ledger') if sys.platform=='darwin' else 'READ_BLOCKED'
    }
    sample={'schema':SCHEMA,'node_role':role,'sampled_at':now.astimezone(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
            'metrics_status':metrics_status,'services':services,**vals}
    validate(sample)
    return sample


def validate(sample):
    import event_ledger as e  # available on Darwin only; collect also validates after copying module
    e.valid_payload('host.snapshot',sample)
    return sample


def ingest(sample, root, expected_node=None):
    import event_ledger as e
    validate(sample)
    if expected_node and sample['node_role'] != expected_node:
        raise ValueError('Wrong authenticated peer role')
    root=Path(root).expanduser()
    stable=sample['node_role']+'|'+sample['sampled_at']
    with e.locked(root):
        state=e.audit(root)
        record=e.write_event(root,state,'host.snapshot',e.event_id('host.snapshot',stable),sample)
        response={'status':'APPENDED' if record else 'DUPLICATE','tip':state['tip'],'count':state['count'],'node_role':sample['node_role']}
    # Project and checkpoint are deliberately separate. The existing Darwin
    # hourly ledger agent handles projections/checkpoints. Don't restart it.
    return response


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('collect');a.add_argument('--node',required=True,choices=sorted(ROLES))
    a=s.add_parser('ingest');a.add_argument('--root',default='~/.local/share/darwin-prometheus')
    a.add_argument('--expected-node',choices=sorted(ROLES),default=None)
    args=p.parse_args(argv)
    os.umask(0o077)
    try:
        if args.action=='collect':
            report=collect(args.node)
        else:
            # Bound input to 16KB. Only sanitized schema is accepted.
            raw=sys.stdin.buffer.read(16385)
            if len(raw)>16384: raise ValueError('Oversized input')
            report=ingest(json.loads(raw),args.root,args.expected_node)
        print(json.dumps(report,sort_keys=True,allow_nan=False));return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'READ_BLOCKED','error_type':type(exc).__name__}));return 3

if __name__=='__main__':sys.exit(main())
