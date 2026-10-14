#!/usr/bin/env python3
"""Muse external testimony ingest: isolated append-only ledger and Prometheus textfile output.

Never treats agent content or Drive existence as authoritative host telemetry.
No OAuth, API calls, token handling, or network listener. Reads one explicitly staged file.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sqlite3
import sys
import tempfile
from zoneinfo import ZoneInfo

SCHEMA = 'simsim.prometheus.external-muse/v1'
REPORT = 'muse-telemetry/v1'
ROOT = '~/.local/share/darwin-prometheus-muse'
ZERO = '0' * 64
MAX_INPUT = 64 * 1024
MAX_RECORD = 12 * 1024
MAX_JOBS = 32
JOB = re.compile(r'^[a-z][a-z0-9_ (),-]{0,63}$')
DRIVE_ID = re.compile(r'^[A-Za-z0-9_-]{10,128}$')
UTC = dt.timezone.utc
PDT = ZoneInfo('America/Los_Angeles')


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def instant(s):
    if not isinstance(s, str):
        raise ValueError('Timestamp type')
    x = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    if x.tzinfo is None:
        raise ValueError('Timezone required')
    return x.astimezone(UTC)


def check_int(n, max_value=100000000):
    if type(n) is not int or not (0 <= n <= max_value):
        raise ValueError('Invalid integer')
    return n


def check_pct(n):
    if isinstance(n, bool) or not isinstance(n, (float, int)) or not math.isfinite(n) or not (0 <= n <= 100):
        raise ValueError('Invalid percent')
    return float(n)


def normalize(raw):
    if not isinstance(raw, dict) or raw.get('schema') != REPORT:
        raise ValueError('Unknown Muse schema')
    date = dt.date.fromisoformat(raw['report_date'])
    if date.isoformat() != raw['report_date']:
        raise ValueError('Noncanonical report date')
    generated = instant(raw['generated_at'])
    local = generated.astimezone(PDT)
    if local.date() != date:
        raise ValueError('Generated date disagrees with report date')
    cron = raw['cron_runs']
    if not isinstance(cron, dict) or not isinstance(cron.get('by_job'), dict):
        raise ValueError('Missing cron runs')
    by_job = cron['by_job']
    if len(by_job) > MAX_JOBS:
        raise ValueError('Too many job labels')
    jobs = []
    sums = {'runs': 0, 'succeeded': 0, 'failed': 0}
    for name, item in sorted(by_job.items()):
        if not isinstance(name, str) or not JOB.fullmatch(name) or not isinstance(item, dict):
            raise ValueError('Unsafe job entry')
        runs = check_int(item.get('runs'))
        succeeded = check_int(item.get('succeeded'))
        failed = check_int(item.get('failed'))
        if succeeded + failed != runs:
            raise ValueError('Inconsistent job counts')
        average = item.get('avg_duration_s')
        if isinstance(average, bool) or not isinstance(average, (float, int)) or not math.isfinite(average) or not 0 <= average <= 86400:
            raise ValueError('Invalid duration')
        jobs.append({'job': name, 'runs': runs, 'succeeded': succeeded, 'failed': failed,
                     'avg_duration_seconds': round(float(average), 4)})
        for key in sums:
            sums[key] += {'runs': runs, 'succeeded': succeeded, 'failed': failed}[key]
    for src, key in [('total_runs', 'runs'), ('total_succeeded', 'succeeded'), ('total_failed', 'failed')]:
        if check_int(cron.get(src)) != sums[key]:
            raise ValueError('Reported totals do not add up')
    subscription = raw['subscription']
    session = raw['session_context']
    if not isinstance(subscription, dict) or not isinstance(session, dict):
        raise ValueError('Missing usage')
    usage = check_pct(subscription['usage_pct_of_weekly_limit'])
    resets = instant(subscription['resets_at'])
    session_used = check_pct(session['used_pct'])
    session_available = check_pct(session['available_pct'])
    if abs((session_used + session_available) - 100.0) > 0.1:
        raise ValueError('Inconsistent session usage')
    errors = raw['errors_anomalies']
    if not isinstance(errors, dict):
        raise ValueError('Invalid errors')
    errors_count = check_int(errors.get('count'))
    # None of the free-text claims, filenames, proof refs or untrusted 'perimeter' enters ledger.
    # Nightly cutoff is not midnight-end completeness; 20:20 early report remains preliminary.
    cutoff_reached = local.hour > 23 or (local.hour == 23 and local.minute >= 30)
    return {'schema': SCHEMA, 'agent': 'muse', 'report_date': date.isoformat(),
            'generated_at': generated.isoformat(timespec='seconds').replace('+00:00', 'Z'),
            'period_status': 'NIGHTLY_CUTOFF' if cutoff_reached else 'PRELIMINARY',
            'confidence': 'EXTERNAL_AGENT_TESTIMONY',
            'weekly_usage_pct': usage,
            'weekly_reset_at': resets.isoformat(timespec='seconds').replace('+00:00','Z'),
            'session_used_pct': session_used,
            'session_available_pct': session_available,
            'reported_error_count': errors_count, 'totals': sums, 'jobs': jobs}


def normalize_file(path):
    p=Path(path).expanduser()
    s=p.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_size > MAX_INPUT or s.st_size < 1:
        raise ValueError('Unsafe file size/type')
    fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    try:
        observed=os.fstat(fd)
        if observed.st_ino != s.st_ino or observed.st_dev != s.st_dev:
            raise ValueError('Source replaced during read')
        data=os.read(fd,MAX_INPUT+1)
        if len(data)>MAX_INPUT or len(data)!=observed.st_size:
            raise ValueError('Changed or oversized source')
    finally:
        os.close(fd)
    return normalize(json.loads(data)), digest(data)


def secure_root(root):
    candidate=Path(root).expanduser()
    if candidate.is_symlink():
        raise ValueError('Symlink root')
    root = candidate.resolve()
    home=Path.home().resolve()/'.local'/'share'
    # Fail closed if pointed at the production E1 or shadow event store.
    for base in (home/'darwin-prometheus',home/'darwin-prometheus-shadow'):
        if root == base or root.is_relative_to(base):
            raise ValueError('Cannot write into E1 or shadow ledger root')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(root, 0o700)
    return root


def audit(root):
    path=root/'muse.jsonl'
    tip=ZERO; seq=0; seen=set(); latest=None
    if not path.exists():
        return {'events':0,'tip':ZERO,'seen':seen,'latest':None}
    with path.open('rb') as f:
        for line in f:
            if len(line)>MAX_RECORD or not line.endswith(b'\n'):
                raise ValueError('Torn or oversized ledger entry')
            obj=json.loads(line)
            if set(obj) != {'schema','seq','event_id','prev_hash','recorded_at','source_sha256','drive_file_id','payload','hash'}:
                raise ValueError('Unexpected ledger fields')
            if obj['schema']!=SCHEMA or type(obj['seq']) is not int or obj['seq']!=seq+1 or obj['prev_hash']!=tip:
                raise ValueError('Invalid chain')
            if not isinstance(obj['source_sha256'],str) or not re.fullmatch('[0-9a-f]{64}',obj['source_sha256']):
                raise ValueError('Invalid source hash')
            file_id=obj['drive_file_id']
            if file_id is not None and (not isinstance(file_id,str) or not DRIVE_ID.fullmatch(file_id)):
                raise ValueError('Bad provider file id')
            if instant(obj['recorded_at']) is None or obj['payload'] != normalize_ledger_payload(obj['payload']):
                raise ValueError('Invalid ledger payload')
            expected=digest(canonical({k:v for k,v in obj.items() if k!='hash'}))
            if obj['hash']!=expected or not re.fullmatch('[0-9a-f]{64}',obj['hash']):
                raise ValueError('Tampered ledger')
            event_id=digest(canonical([SCHEMA,obj['payload']['report_date'],obj['payload']['generated_at'],obj['source_sha256']]))
            if event_id!=obj['event_id'] or obj['event_id'] in seen:
                raise ValueError('Invalid event identity')
            seen.add(event_id); seq+=1; tip=obj['hash']; latest=obj
    return {'events':seq,'tip':tip,'seen':seen,'latest':latest}


def normalize_ledger_payload(p):
    """Ensure canonical bounded derived-only schema; don't allow unknown fields to persist."""
    if not isinstance(p,dict) or set(p)!={'schema','agent','report_date','generated_at','period_status','confidence','weekly_usage_pct','weekly_reset_at','session_used_pct','session_available_pct','reported_error_count','totals','jobs'}:
        raise ValueError('Unexpected payload fields')
    if p['schema']!=SCHEMA or p['agent']!='muse' or p['confidence']!='EXTERNAL_AGENT_TESTIMONY':
        raise ValueError('Wrong provenance')
    if p['period_status'] not in ('PRELIMINARY','NIGHTLY_CUTOFF'):
        raise ValueError('Invalid period')
    stamp=instant(p['generated_at']).astimezone(PDT)
    expected='NIGHTLY_CUTOFF' if stamp.hour==23 and stamp.minute>=30 else 'PRELIMINARY'
    if p['period_status']!=expected:raise ValueError('Inconsistent period status')
    date=dt.date.fromisoformat(p['report_date'])
    if date.isoformat()!=p['report_date'] or instant(p['generated_at']).astimezone(PDT).date()!=date:
        raise ValueError('Invalid date')
    if instant(p['weekly_reset_at']) is None:raise ValueError('Invalid reset')
    for k in ('weekly_usage_pct','session_used_pct','session_available_pct'):check_pct(p[k])
    if abs(p['session_used_pct']+p['session_available_pct']-100)>0.1:raise ValueError('Bad percentage sum')
    check_int(p['reported_error_count'])
    if set(p['totals'])!={'runs','succeeded','failed'}:raise ValueError('Bad totals')
    for k in p['totals']:check_int(p['totals'][k])
    if len(p['jobs'])>MAX_JOBS or not isinstance(p['jobs'],list):raise ValueError('Bad jobs')
    sums={'runs':0,'succeeded':0,'failed':0}
    names=set()
    for j in p['jobs']:
        if not isinstance(j,dict) or set(j)!={'job','runs','succeeded','failed','avg_duration_seconds'}:raise ValueError('Unexpected job fields')
        if not isinstance(j['job'],str) or not JOB.fullmatch(j['job']) or j['job'] in names:raise ValueError('Invalid job label')
        names.add(j['job'])
        for k in sums: sums[k]+=check_int(j[k])
        if j['succeeded']+j['failed']!=j['runs']:raise ValueError('Inconsistent job totals')
        avg=j['avg_duration_seconds']
        if isinstance(avg,bool) or not isinstance(avg,(int,float)) or not math.isfinite(avg) or avg<0 or avg>86400:
            raise ValueError('Bad job duration')
    if sums != p['totals']:
        raise ValueError('Mismatched totals')
    return p


def ingest(root, input_path, drive_file_id=None):
    if drive_file_id is not None and not DRIVE_ID.fullmatch(drive_file_id):
        raise ValueError('Invalid Google Drive file ID')
    p,raw_sha=normalize_file(input_path)
    uid=digest(canonical([SCHEMA,p['report_date'],p['generated_at'],raw_sha]))
    root=secure_root(root)
    lock=os.open(str(root/'.writer.lock'),os.O_CREAT|os.O_RDWR,0o600)
    try:
        fcntl.flock(lock,fcntl.LOCK_EX)
        state=audit(root)
        if uid in state['seen']:
            return {'status':'DUPLICATE','events':state['events'],'tip':state['tip'],
                    'source_sha256':raw_sha,'period_status':p['period_status']}
        e={'schema':SCHEMA,'seq':state['events']+1,'event_id':uid,'prev_hash':state['tip'],
           'recorded_at':dt.datetime.now(UTC).isoformat(timespec='seconds').replace('+00:00','Z'),
           'source_sha256':raw_sha,'drive_file_id':drive_file_id,'payload':p}
        e['hash']=digest(canonical(e));line=canonical(e)+b'\n'
        if len(line)>MAX_RECORD:raise ValueError('Event too large')
        fd=os.open(str(root/'muse.jsonl'),os.O_CREAT|os.O_WRONLY|os.O_APPEND,0o600)
        try:
            n=os.write(fd,line)
            if n!=len(line):raise OSError('Torn write: manual recovery required')
            os.fsync(fd)
        finally:os.close(fd)
        df=os.open(str(root),os.O_RDONLY)
        try:os.fsync(df)
        finally:os.close(df)
        return {'status':'INGESTED','events':state['events']+1,'tip':e['hash'],
                'source_sha256':raw_sha,'period_status':p['period_status']}
    finally:
        fcntl.flock(lock,fcntl.LOCK_UN)
        os.close(lock)


def project(root):
    root=secure_root(root)
    state=audit(root)
    fd,tmp=tempfile.mkstemp(prefix='.muse-',suffix='.sqlite3',dir=root)
    os.close(fd);os.chmod(tmp,0o600)
    try:
        con=sqlite3.connect(tmp)
        con.execute('CREATE TABLE reports(seq INTEGER PRIMARY KEY, report_date TEXT, generated_at TEXT, period_status TEXT, weekly_usage_pct REAL, weekly_reset_at TEXT, session_used_pct REAL, session_available_pct REAL, reported_error_count INTEGER, runs INTEGER, succeeded INTEGER, failed INTEGER, source_sha256 TEXT, record_hash TEXT)')
        con.execute('CREATE TABLE jobs(seq INTEGER, job TEXT, runs INTEGER, succeeded INTEGER, failed INTEGER, avg_duration_seconds REAL, PRIMARY KEY(seq,job))')
        j=root/'muse.jsonl'
        if j.exists():
            with j.open('rb') as f:
                for line in f:
                    e=json.loads(line);p=e['payload'];t=p['totals']
                    con.execute('INSERT INTO reports VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(e['seq'],p['report_date'],p['generated_at'],p['period_status'],p['weekly_usage_pct'],p['weekly_reset_at'],p['session_used_pct'],p['session_available_pct'],p['reported_error_count'],t['runs'],t['succeeded'],t['failed'],e['source_sha256'],e['hash']))
                    for x in p['jobs']:
                        con.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?)',(e['seq'],x['job'],x['runs'],x['succeeded'],x['failed'],x['avg_duration_seconds']))
        con.commit();con.close()
        os.replace(tmp,root/'muse.sqlite3')
        return {'status':'PROJECTED','events':state['events'],'tip':state['tip']}
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def prom(root):
    state=audit(Path(root).expanduser())
    if not state['latest']:
        return '# No Muse telemetry ingested yet; unknown is not zero.\n'
    p=state['latest']['payload'];ts=int(instant(p['generated_at']).timestamp())
    def metric(name,val,labels=''):
        return f'{name}{labels} {val}\n'
    prefix='simsim_muse_'
    lines=[f'# Muse independent agent self-reported telemetry. Not direct host observation.\n',
           metric(prefix+'report_generated_timestamp_seconds',ts),
           metric(prefix+'weekly_quota_used_percent',p['weekly_usage_pct']),
           metric(prefix+'session_used_percent',p['session_used_pct']),
           metric(prefix+'daily_runs',p['totals']['runs']),
           metric(prefix+'daily_succeeded',p['totals']['succeeded']),
           metric(prefix+'daily_failed',p['totals']['failed']),
           metric(prefix+'daily_reported_errors',p['reported_error_count']),
           metric(prefix+'report_cutoff_reached',1 if p['period_status']=='NIGHTLY_CUTOFF' else 0),
           metric(prefix+'source_testimony',1)]
    for j in p['jobs']:
        label='{job='+json.dumps(j['job'],ensure_ascii=True)+'}'
        for suffix,key in [('daily_job_runs','runs'),('daily_job_succeeded','succeeded'),
                           ('daily_job_failed','failed'),('daily_job_avg_duration_seconds','avg_duration_seconds')]:
            lines.append(metric(prefix+suffix,j[key],label))
    return ''.join(lines)


def output_atomic(path,content):
    path=Path(path).expanduser()
    if not path.parent.is_dir():raise FileNotFoundError('Missing textfile directory')
    fd,tmp=tempfile.mkstemp(prefix='.muse_',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:
            os.fchmod(f.fileno(),0o600)
            f.write(content);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default=ROOT)
    s=p.add_subparsers(dest='command',required=True)
    i=s.add_parser('ingest');i.add_argument('--input',required=True);i.add_argument('--drive-file-id')
    s.add_parser('verify');s.add_parser('project')
    e=s.add_parser('export');e.add_argument('--output')
    a=p.parse_args(argv)
    os.umask(0o077)
    try:
        if a.command=='ingest':out=ingest(a.root,a.input,a.drive_file_id)
        elif a.command=='verify':
            t=audit(Path(a.root).expanduser());out={'status':'VERIFIED','events':t['events'],'tip':t['tip']}
        elif a.command=='project':out=project(a.root)
        else:
            data=prom(a.root)
            if a.output:output_atomic(a.output,data);out={'status':'EXPORTED','bytes':len(data)}
            else:sys.stdout.write(data);return 0
        print(json.dumps(out,sort_keys=True));return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError,sqlite3.Error) as exc:
        print(json.dumps({'status':'READ_BLOCKED','error_type':type(exc).__name__}));return 3

if __name__=='__main__':raise SystemExit(main())
