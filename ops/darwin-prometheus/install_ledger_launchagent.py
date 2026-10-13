#!/usr/bin/env python3
"""Generate unprivileged hourly Darwin Event Ledger LaunchAgent; no sudo/install performed."""
import argparse
import os
from pathlib import Path
import plistlib
import sys

LABEL='org.chitakasha.darwin-prometheus-ledger'
def main():
    if sys.platform!='darwin':raise SystemExit('Only macOS launchd supported')
    p=argparse.ArgumentParser()
    p.add_argument('--replace',action='store_true')
    args=p.parse_args()
    home=Path.home()
    script=home/'darwin-prometheus'/'run_cycle.py'
    if not script.is_file():raise SystemExit('Install run_cycle.py first')
    path=home/'Library'/'LaunchAgents'/(LABEL+'.plist')
    path.parent.mkdir(parents=True,exist_ok=True)
    logs=home/'Library'/'Logs';logs.mkdir(parents=True,exist_ok=True)
    if path.exists() and not args.replace:raise SystemExit('Existing agent: stop/backup before --replace')
    data={'Label':LABEL,'ProgramArguments':[sys.executable,str(script)],
          'StartInterval':3600,'RunAtLoad':True,
          'StandardOutPath':str(logs/'darwin-prometheus-ledger.log'),
          'StandardErrorPath':str(logs/'darwin-prometheus-ledger-error.log')}
    if path.exists():
        backup=path.with_suffix('.plist.bak')
        if backup.exists():raise SystemExit('Refuse overwrite: backup exists')
        backup.write_bytes(path.read_bytes());os.chmod(backup,0o600)
    path.write_bytes(plistlib.dumps(data));os.chmod(path,0o600)
    print('Wrote',path)
    return 0
if __name__=='__main__':sys.exit(main())