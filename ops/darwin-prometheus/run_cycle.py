#!/usr/bin/env python3
"""Darwin user-level hourly DP-01 cycle: read Governor, append, host sample, replay, seal.

No external API calls or model execution. It does NOT trigger a quota probe.
Local private evidence only. A nonzero exit code means not all steps succeeded.
"""
import argparse
import json
from pathlib import Path
import sys
import sqlite3
import event_ledger as e

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default=e.DEFAULT_ROOT)
    p.add_argument('--governor-db',default=e.DEFAULT_GOVERNOR_DB)
    args=p.parse_args(argv)
    root=Path(args.root).expanduser()
    reports={}
    try:
        reports['quota']=e.reconcile(root,args.governor_db)
    except (OSError,ValueError,sqlite3.Error) as exc:
        reports['quota']={'status':'READ_BLOCKED','error_type':type(exc).__name__}
    try:
        reports['host']=e.host_health(root)
        reports['projection']=e.project(root)
        reports['checkpoint']=e.checkpoint(root)
    except (OSError,ValueError,sqlite3.Error) as exc:
        reports['ledger']={'status':'INVALID','error_type':type(exc).__name__}
    ready=(reports.get('quota',{}).get('status')=='SYNCED'
           and reports.get('projection',{}).get('status')=='PROJECTED'
           and reports.get('checkpoint',{}).get('status') in ('CHECKPOINT_CREATED','ALREADY_CHECKPOINTED'))
    print(json.dumps({'schema':'chitakasha.prometheus.cycle/v1','status':'VERIFIED' if ready else 'PARTIAL',
                      'steps':reports},sort_keys=True))
    return 0 if ready else 3
if __name__=='__main__':sys.exit(main())