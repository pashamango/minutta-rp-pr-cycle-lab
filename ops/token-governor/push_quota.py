#!/usr/bin/env python3
"""Wolfram -> Darwin push transport for token-governor (unprivileged, SSH only).

Queues *sanitized* sample files locally; remote ingestion uses governor.py ingest.
No remote listener, secrets, raw CodexBar JSON, or sudo required.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import governor

DEFAULT_SPOOL = '~/.local/share/token-governor/spool'
HOST = re.compile(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+$')


def canonical(sample):
    validated = governor.validate_sample(sample)
    return (json.dumps(validated, sort_keys=True, separators=(',', ':')) + '\n').encode()


def spool_sample(sample, root):
    root = Path(root).expanduser()
    pending = root/'pending'
    pending.mkdir(parents=True, exist_ok=True, mode=0o700)
    raw = canonical(sample)
    digest = hashlib.sha256(raw).hexdigest()
    # Provider update time identifies the quota observation; collected_at may vary on re-poll.
    identity = (sample['provider'] + '|' + sample['observed_at']).encode()
    stable_id = hashlib.sha256(identity).hexdigest()
    timestamp = governor.read_time(sample['observed_at']).strftime('%Y%m%dT%H%M%SZ')
    item = pending / (timestamp + '-' + stable_id + '.json')
    if not item.exists():
        tmp = pending / ('.' + item.name + '.tmp')
        with tmp.open('xb') as fh:
            os.chmod(tmp, 0o600)
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, item)
    return digest


def move_to(root, item, target):
    dest = root/target
    dest.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.replace(item, dest/item.name)


def probe(script):
    try:
        proc = subprocess.run([sys.executable, str(script), 'probe'],
                              capture_output=True, text=True, timeout=90, check=False)
        if proc.returncode != 0:
            return None
        return governor.validate_sample(json.loads(proc.stdout))
    except (OSError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def ship(dest, data, timeout=35):
    cmd=['ssh', '-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
         '-o', 'ForwardAgent=no', '-o', 'ConnectTimeout=10', dest,
         'python3 "$HOME/token-governor/governor.py" ingest']
    try:
        proc = subprocess.run(cmd, input=data, capture_output=True,
                              text=True, timeout=timeout, check=False)
        # ingest exits 2 when it generates a legitimate alert.
        if proc.returncode not in (0, 2):
            return 'TRANSPORT_UNAVAILABLE'
        r = json.loads(proc.stdout)
        if r.get('status') == 'STALE':
            return 'EXPIRED'
        if r.get('status') not in ('BASELINE','LOW_BUDGET','BURN_SPIKE',
                 'DUPLICATE','RESET_CHANGED','RECONCILIATION',
                 'INTERVAL_TOO_SHORT','NORMAL'):
            return 'RECEIPT_INVALID'
        return 'ACKED'
    except (OSError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return 'TRANSPORT_UNAVAILABLE'


def run(dest, root, local_script=None, max_batch=24, now=None):
    if not HOST.fullmatch(dest) or dest.startswith('-'):
        raise ValueError('invalid SSH destination')
    now = now or dt.datetime.now(dt.timezone.utc)
    root = Path(root).expanduser()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    sample = probe(local_script or Path(__file__).with_name('governor.py'))
    new_digest = spool_sample(sample, root) if sample else None
    pending = sorted((root/'pending').glob('*.json')) if (root/'pending').exists() else []
    sent,expired,blocked = 0,0,False
    for item in pending[:max_batch]:
        # Never claim that a stale file was accepted into Darwin's real DB.
        try:
            s=governor.validate_sample(json.loads(item.read_text(encoding='utf8')))
        except (ValueError,OSError,json.JSONDecodeError):
            move_to(root,item,'invalid');continue
        age=(now-governor.read_time(s['observed_at'])).total_seconds()/60
        if age < -5 or age > 80:
            move_to(root,item,'expired');expired += 1
            continue
        result=ship(dest,item.read_text(encoding='utf8'))
        if result == 'ACKED':
            move_to(root,item,'sent');sent += 1
        elif result == 'EXPIRED':
            move_to(root,item,'expired');expired += 1
        else:
            blocked = True
            break
    remaining=len(list((root/'pending').glob('*.json'))) if (root/'pending').exists() else 0
    summary={'schema':'token-governor.push-receipt/v1',
             'status':'DELIVERED' if sample and not blocked and remaining==0 and sent>0
                 else 'PARTIAL' if sent else 'PROBE_UNAVAILABLE' if sample is None else 'PENDING',
             'probe':'FRESH_SAMPLE' if sample else 'UNAVAILABLE',
             'sample_sha256':new_digest,
             'delivered_count':sent,'expired_count':expired,'pending_count':remaining,
             'transport':'OUTBOUND_STRICT_SSH',
             'work_quota_verification':'UNVERIFIED_FOR_WORK'}
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dest',required=True,help='existing trusted Darwin SSH user@TailnetIP')
    p.add_argument('--spool',default=DEFAULT_SPOOL)
    args=p.parse_args()
    os.umask(0o077)
    try:
        result=run(args.dest,args.spool)
        print(json.dumps(result,sort_keys=True))
        return 0 if result['status']=='DELIVERED' else 3
    except (ValueError,OSError) as e:
        print(json.dumps({'schema':'token-governor.push-receipt/v1',
                          'status':'BLOCKED', 'reason':type(e).__name__},sort_keys=True))
        return 3

if __name__=='__main__':sys.exit(main())