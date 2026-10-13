#!/usr/bin/env python3
"""DP-01B shadow-only host snapshot cycle for Darwin, never touches DP-01 E1 journal.

No AI, credentials, sudo, external requests, or producer rewiring. Uses
host_adapter read-only collection and independently versioned Event Ledger root.
"""
import argparse
import json
import os
from pathlib import Path
import sqlite3

import event_ledger as e
import host_adapter as a

SHADOW_ROOT = '~/.local/share/darwin-prometheus-dp01b-shadow'
PRODUCTION_ROOT = e.DEFAULT_ROOT


def guarded_root(root):
    """Stop if shadow aliases or nests under the protected DP-01 E1 journal."""
    shadow = Path(root).expanduser().resolve()
    production = Path(PRODUCTION_ROOT).expanduser().resolve()
    if shadow == production or shadow in production.parents or production in shadow.parents:
        raise ValueError('Shadow root overlaps production E1 root')
    if not shadow.is_absolute():
        raise ValueError('Expected absolute resolved root')
    return shadow


def run(root=SHADOW_ROOT, now=None):
    target = guarded_root(root)
    before = e.audit(target) if target.exists() else None
    sample = a.collect('darwin', now=now)
    status = a.ingest(sample, target, expected_node='darwin')
    verified = e.audit(target)
    projected = e.project(target)
    checkpoint = e.checkpoint(target)
    check_again = e.audit(target)
    if (verified['tip'] != check_again['tip'] or
            verified['count'] != projected['events'] or
            checkpoint['tip'] != verified['tip']):
        raise ValueError('Shadow journal projection/checkpoint mismatch')
    return {
        'schema':'chitakasha.prometheus.host-shadow-receipt/v1',
        'status':'VERIFIED',
        'mode':'SHADOW_ONLY',
        'source':'SOURCE_READ_LOCAL',
        'event_status':status['status'],
        'events':verified['count'],
        'chain_tip':verified['tip'],
        'checkpoint_status':checkpoint['status'],
        'previous_chain_tip':before['tip'] if before else None,
        'node_role':'darwin',
        'production_e1_touched':False,
        'service_metadata':{key: sample['services'][key] for key in a.SERVICES},
        'metric_status':sample['metrics_status'],
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',default=SHADOW_ROOT)
    args=parser.parse_args(argv)
    os.umask(0o077)
    try:
        out=run(args.root)
        print(json.dumps(out,sort_keys=True,allow_nan=False))
        return 0
    except (OSError,ValueError,TypeError,KeyError,sqlite3.Error,RuntimeError) as exc:
        print(json.dumps({'schema':'chitakasha.prometheus.host-shadow-receipt/v1',
                          'status':'BLOCKED','error_type':type(exc).__name__,
                          'production_e1_touched':False},sort_keys=True))
        return 3

if __name__=='__main__':sys.exit(main())