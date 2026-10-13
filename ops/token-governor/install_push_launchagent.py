#!/usr/bin/env python3
"""Write an hourly Wolfram user LaunchAgent for outbound quota push (no sudo)."""
import argparse
import os
from pathlib import Path
import plistlib
import re
import sys

LABEL='org.chitakasha.token-governor-push'
HOST=re.compile(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+$')


def main():
    if sys.platform != 'darwin':
        raise SystemExit('macOS only')
    p=argparse.ArgumentParser()
    p.add_argument('--dest',required=True)
    p.add_argument('--replace',action='store_true')
    args=p.parse_args()
    if not HOST.fullmatch(args.dest) or args.dest.startswith('-'):
        raise SystemExit('Invalid SSH destination')
    home=Path.home()
    src=home/'token-governor'/'push_quota.py'
    if not src.is_file():
        raise SystemExit('push_quota.py not installed')
    out=home/'Library'/'LaunchAgents'/f'{LABEL}.plist'
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists() and not args.replace:
        raise SystemExit('Existing LaunchAgent; use --replace after backup/bootout')
    log=home/'Library'/'Logs'
    log.mkdir(parents=True,exist_ok=True)
    cfg={'Label':LABEL,'ProgramArguments':[sys.executable,str(src),'--dest',args.dest],
         'RunAtLoad':True,'StartInterval':3600,
         'StandardOutPath':str(log/'token-governor-push.log'),
         'StandardErrorPath':str(log/'token-governor-push-error.log')}
    if out.exists():
        back=out.with_suffix('.plist.bak')
        if back.exists():raise SystemExit('Backup already exists; inspect first')
        back.write_bytes(out.read_bytes())
        os.chmod(back,0o600)
    out.write_bytes(plistlib.dumps(cfg))
    os.chmod(out,0o600)
    print('Wrote',out)
    print(f'Load from logged-in user context: launchctl bootstrap gui/$(id -u) "{out}"')
    return 0

if __name__=='__main__':sys.exit(main())