#!/usr/bin/env python3
"""Wolfram-only CodexBar CLI installer. Official GitHub release + SHA-256 digest.

No sudo, no shell pipes, no cookie reading, no remote credential transfer.
If release asset digest is absent, refuse to install.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.request

API='https://api.github.com/repos/steipete/CodexBar/releases/latest'


def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'ChitAkasha-Token-Governor-Pilot/1.0','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,timeout=45) as r:
        return r.read(120_000_000 + 1)


def main():
    if sys.platform!='darwin':
        print('Use on Wolfram (macOS) only; Darwin/macOS 12 compatibility is not established.',file=sys.stderr)
        return 2
    arch=platform.machine()
    if arch not in ('x86_64','arm64'):
        print('Unsupported CPU architecture',file=sys.stderr);return 2
    data=json.loads(get(API))
    candidates=[a for a in data.get('assets',[]) if a.get('name','').endswith('macos-'+arch+'.tar.gz') and a.get('name','').startswith('CodexBarCLI-')]
    if len(candidates)!=1:
        print('No unique official CodexBarCLI release tarball for '+arch,file=sys.stderr);return 2
    asset=candidates[0]
    digest=asset.get('digest') or ''
    if not digest.startswith('sha256:') or len(digest)!=71:
        print('GitHub release asset has no SHA-256 digest; refusing unverified automatic install. Download manually from GitHub Releases.',file=sys.stderr)
        return 3
    expected=digest.split(':',1)[1]
    url=asset.get('browser_download_url','')
    if not url.startswith('https://github.com/steipete/CodexBar/releases/download/'):
        print('Unexpected asset host',file=sys.stderr);return 3
    print('Downloading official release:',asset['name'],'tag:',data.get('tag_name'))
    blob=get(url)
    if len(blob)>120_000_000:
        print('Asset too large',file=sys.stderr);return 3
    actual=hashlib.sha256(blob).hexdigest()
    if actual!=expected:
        print('SHA-256 mismatch: installation aborted',file=sys.stderr);return 3
    with tempfile.TemporaryDirectory() as tmp:
        fn=Path(tmp)/asset['name'];fn.write_bytes(blob)
        with tarfile.open(fn,'r:gz') as tf:
            matches=[m for m in tf.getmembers() if m.isfile() and Path(m.name).name=='CodexBarCLI']
            if len(matches)!=1:
                print('Expected single CodexBarCLI executable in tarball',file=sys.stderr);return 3
            inp=tf.extractfile(matches[0])
            if inp is None:raise ValueError('missing CLI binary')
            target=Path.home()/'token-governor'/'bin'/'CodexBarCLI'
            target.parent.mkdir(parents=True,exist_ok=True)
            scratch=target.with_suffix('.new')
            with scratch.open('wb') as out:shutil.copyfileobj(inp,out)
            scratch.chmod(0o700)
            os.replace(scratch,target)
    print('Installed SHA-256-verified CLI to:',target)
    print('Next: '+str(target)+' --version')
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print('Install failed:',type(e).__name__,'(details deliberately omitted)',file=sys.stderr);sys.exit(3)