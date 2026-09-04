#!/usr/bin/env python3
"""Install the Documents migration as a private user LaunchAgent."""
import argparse, os, plistlib, shutil, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--worker",type=Path,required=True); p.add_argument("--python",type=Path,required=True)
    p.add_argument("--home",type=Path,default=Path.home()); p.add_argument("--no-start",action="store_true"); a=p.parse_args()
    home=a.home.resolve(); state=home/"ChitAkasha-Storage/migrations/documents-0002"; install=state/"bin"
    install.mkdir(parents=True,exist_ok=True,mode=0o700); os.chmod(state,0o700); os.chmod(install,0o700)
    target=install/"documents_resumable.py"; shutil.copyfile(a.worker.resolve(strict=True),target); os.chmod(target,0o700)
    label="com.chitakasha.documents-migration"; logs=state/"logs"; logs.mkdir(exist_ok=True,mode=0o700)
    plist={"Label":label,"ProgramArguments":[str(a.python.resolve(strict=True)),str(target),"--state",str(state),"run",
      "--source",str(home/"Documents"),"--namespace",str(home/"ChitAkasha-Storage"),
      "--t0",str(home/"ChitAkasha-Storage/migrations/new-write-cutover-v1.json")],
      "RunAtLoad":True,"KeepAlive":False,"ProcessType":"Background",
      "StandardOutPath":str(logs/"worker.stdout.log"),"StandardErrorPath":str(logs/"worker.stderr.log")}
    agents=home/"Library/LaunchAgents"; agents.mkdir(parents=True,exist_ok=True); dest=agents/(label+".plist")
    temp=dest.with_suffix(".plist.tmp"); temp.write_bytes(plistlib.dumps(plist,sort_keys=True)); os.chmod(temp,0o600); os.replace(temp,dest)
    if not a.no_start:
        domain=f"gui/{os.getuid()}"; subprocess.run(["launchctl","bootout",domain,str(dest)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(["launchctl","bootstrap",domain,str(dest)],check=True)
    print(state)
if __name__=="__main__": main()
