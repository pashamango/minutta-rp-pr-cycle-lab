#!/usr/bin/env python3
"""Generate but DO NOT load Darwin DP-01B shadow hourly user LaunchAgent.

Keeps original DP-01 E1 LaunchAgent untouched. Launch is a distinct decision
performed only after successful on-Darwin disposable acceptance checks.
"""
import argparse
import os
from pathlib import Path
import plistlib
import sys

LABEL='org.chitakasha.darwin-prometheus-host-shadow'


def plan(home=None, python=None):
    home=Path(home) if home else Path.home()
    python=python or sys.executable
    script=home/'darwin-prometheus-dp01b-shadow'/'host_shadow_cycle.py'
    return {
      'Label':LABEL,
      'ProgramArguments':[str(python),str(script)],
      'RunAtLoad':True,
      'StartInterval':3600,
      'StandardOutPath':str(home/'Library'/'Logs'/'darwin-prometheus-host-shadow.log'),
      'StandardErrorPath':str(home/'Library'/'Logs'/'darwin-prometheus-host-shadow-error.log'),
    }


def install(home=None, python=None):
    home=Path(home) if home else Path.home()
    cfg=plan(home,python)
    if not Path(cfg['ProgramArguments'][1]).is_file():
        raise FileNotFoundError('Stage host_shadow_cycle.py in its own folder first')
    path=home/'Library'/'LaunchAgents'/(LABEL+'.plist')
    if path.exists():
        raise FileExistsError('Refuse overwriting existing shadow agent')
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    (home/'Library'/'Logs').mkdir(parents=True,exist_ok=True)
    data=plistlib.dumps(cfg)
    # Exclusive open prevents concurrent overwrite; no bootstrapping here.
    fd=os.open(str(path),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return {'status':'PLIST_CREATED_UNLOADED','label':LABEL,
            'production_agent_touched':False}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dry-run',action='store_true')
    args=p.parse_args(argv)
    os.umask(0o077)
    if sys.platform != 'darwin':
        print('macOS only',file=sys.stderr);return 3
    try:
        result={'status':'DRY_RUN','label':LABEL, 'production_agent_touched':False} if args.dry_run else install()
        print(result);return 0
    except (OSError,ValueError) as exc:
        print({'status':'BLOCKED','error_type':type(exc).__name__});return 3

if __name__=='__main__':sys.exit(main())