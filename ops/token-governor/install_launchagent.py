#!/usr/bin/env python3
"""Create a Darwin-only user LaunchAgent for hourly quota observation.
Do NOT install on Wolfram unless Wolfram is intentionally serving as governor.
"""
import argparse
from pathlib import Path
import plistlib
import re
import sys

LABEL='org.chitakasha.token-governor'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host',required=True,help='Trusted Tailscale SSH target, e.g. youruser@wolfram')
    p.add_argument('--notify-issue',help='Optional owner/repo#issue, requires gh auth')
    p.add_argument('--replace',action='store_true',help='Explicitly replace existing plist')
    args=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.@-]+',args.host) or args.host.startswith('-'):
        p.error('invalid --host')
    if args.notify_issue and not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*',args.notify_issue):
        p.error('invalid --notify-issue')
    home=Path.home()
    script=home/'token-governor'/'governor.py'
    if not script.exists():
        p.error('missing '+str(script)+'; unzip package first')
    pl=home/'Library'/'LaunchAgents'/(LABEL+'.plist')
    pl.parent.mkdir(parents=True,exist_ok=True)
    logs=home/'Library'/'Logs'
    logs.mkdir(parents=True,exist_ok=True)
    if pl.exists() and not args.replace:
        p.error(str(pl)+' exists; use --replace to update intentionally')
    cmd=[sys.executable,str(script),'poll','--host',args.host]
    if args.notify_issue:cmd += ['--notify-issue',args.notify_issue]
    data={
     'Label':LABEL,
     'ProgramArguments':cmd,
     'EnvironmentVariables':{'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'},
     'StartInterval':3600,
     'RunAtLoad':True,
     'StandardOutPath':str(logs/'token-governor.log'),
     'StandardErrorPath':str(logs/'token-governor-error.log'),
    }
    with pl.open('wb') as f:plistlib.dump(data,f)
    print('Wrote:',pl)
    print('To activate (on Darwin):')
    print('launchctl bootstrap gui/$(id -u) "$HOME/Library/LaunchAgents/'+LABEL+'.plist"')
    print('To check: tail -n 10 "$HOME/Library/Logs/token-governor.log"')
    return 0

if __name__=='__main__':sys.exit(main())