#!/usr/bin/env python3
"""DP-01B *read-only* deployed-source fingerprint and conservative local safety gate.

Never prints source bytes, home paths, identities or regex matches. This is a
triage scanner, NOT a claim of security or authorization to publish source.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat

MAX_BYTES = 512_000
EXPECTED = 'a916cdffa81312b12ff1761dc5f81fbb30dcb04670c52ad02e08eeee07f22f81'
SUSPICIOUS = [
    rb'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    rb'gh[pousr]_[A-Za-z0-9_]{12,}',
    rb'github_pat_[A-Za-z0-9_]{12,}',
    rb'(?i)(?:sk-|sk-proj-)[A-Za-z0-9_-]{15,}',
    rb'(?i)(?:api[_-]?key|password|access[_-]?token|client_secret)\s*[:=]\s*[\"\']?[^\s,\"\']{8,}',
    rb'(?i)authorization\s*:\s*(?:bearer|basic)\s+',
    rb'(?i)[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
    rb'(?i)/Users/[^/\s\"\']+',
    rb'\b(?:\d{1,3}\.){3}\d{1,3}\b',
]


def audit_source(path, expected=EXPECTED):
    path=Path(path).expanduser()
    # Do not follow symlink or read a device, FIFO, or socket.
    try:
        status=path.lstat()
    except FileNotFoundError:
        return {'schema':'chitakasha.prometheus.source-attestation/v1',
                'status':'MISSING','sha256':None,'reference':'UNKNOWN_NOT_PRESENT',
                'publication':'DENIED'}
    if not stat.S_ISREG(status.st_mode) or status.st_size > MAX_BYTES or status.st_size < 1:
        raise ValueError('Unsafe file type or size')
    data=path.read_bytes()
    if len(data)!=status.st_size or len(data)>MAX_BYTES:
        raise ValueError('File changed during read')
    actual=hashlib.sha256(data).hexdigest()
    counts=sum(bool(re.search(p,data)) for p in SUSPICIOUS)
    return {'schema':'chitakasha.prometheus.source-attestation/v1',
            'status':'FINGERPRINTED', 'sha256':actual,
            'reference':'MATCH' if actual==expected else 'DIFFERENT',
            'suspicious_pattern_classes':counts,
            'publication':'HUMAN_REVIEW_REQUIRED',
            'source_size_bytes':len(data)}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--file',required=True)
    p.add_argument('--expected-sha256',default=EXPECTED)
    a=p.parse_args(argv)
    os.umask(0o077)
    if not re.fullmatch('[a-f0-9]{64}',a.expected_sha256):
        p.error('bad expected digest')
    try: report=audit_source(a.file,a.expected_sha256)
    except (OSError,ValueError) as exc:
        report={'schema':'chitakasha.prometheus.source-attestation/v1',
                'status':'READ_BLOCKED','error_type':type(exc).__name__,
                'publication':'DENIED'}
    print(json.dumps(report,sort_keys=True))
    return 0 if report['status']=='FINGERPRINTED' else 3

if __name__=='__main__':raise SystemExit(main())
