#!/usr/bin/env python3
"""TOKEN_GOVERNOR_CODEXBAR_PILOT/v1: read-only quota collector and hourly alert.

Standard library only. No credentials leave the provider host: 'probe' emits a
sanitized subset of CodexBar JSON. Cloud Work branch attribution is UNKNOWN.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys

UTC = dt.timezone.utc
SCHEMA = 'chitakasha.token_governor.sample/v1'
ISSUE_PATTERN = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*$')
HOST_PATTERN = re.compile(r'^[A-Za-z0-9_.@-]+$')
DEFAULT_DB = '~/.local/share/token-governor/observations.sqlite3'


def iso(value):
    return value.astimezone(UTC).isoformat().replace('+00:00','Z')


def read_time(value):
    if not isinstance(value, str) or not value:
        raise ValueError('missing timestamp')
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp missing timezone')
    return parsed.astimezone(UTC)


def percentage(value):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not 0 <= value <= 100:
        raise ValueError('invalid percentage')
    return float(value)


def safe_source(raw):
    """Only stable provider labels; never relay arbitrary identity text."""
    allowed = {'oauth', 'cli', 'auto', 'web', 'local', 'api', 'unknown', 'rpc', 'codex_cli'}
    return raw if isinstance(raw, str) and raw in allowed else 'unknown'


def sanitize_codexbar(raw, gathered=None):
    """Accept documented CLI usage JSON, drop account details and all other fields."""
    rows = raw if isinstance(raw,list) else [raw]
    matches = [r for r in rows if isinstance(r,dict) and r.get('provider')=='codex']
    if len(matches)!=1:
        raise ValueError('exactly one Codex provider required')
    row = matches[0]
    usage = row.get('usage')
    if not isinstance(usage,dict):
        raise ValueError('usage missing')
    weekly = usage.get('secondary')
    if not isinstance(weekly,dict):
        raise ValueError('weekly quota missing')
    primary = usage.get('primary')
    observed=read_time(usage.get('updatedAt'))
    reset=read_time(weekly.get('resetsAt'))
    now = gathered or dt.datetime.now(UTC)
    sample={
      'schema':SCHEMA,
      'provider':'codex',
      'source':safe_source(row.get('source')),
      'observed_at':iso(observed),
      'collected_at':iso(now),
      'weekly_used_pct':percentage(weekly.get('usedPercent')),
      'weekly_reset_at':iso(reset),
      'session_used_pct':None,
      'session_reset_at':None,
      'attribution':'UNATTRIBUTED_CLOUD_WORK',
    }
    if isinstance(primary,dict) and primary.get('usedPercent') is not None:
        sample['session_used_pct']=percentage(primary['usedPercent'])
        if primary.get('resetsAt'):
            sample['session_reset_at']=iso(read_time(primary['resetsAt']))
    return sample


def validate_sample(raw):
    if not isinstance(raw,dict) or raw.get('schema')!=SCHEMA or raw.get('provider')!='codex':
        raise ValueError('unknown sanitized sample schema')
    result={k:raw.get(k) for k in ('schema','provider','source','observed_at','collected_at',
        'weekly_used_pct','weekly_reset_at','session_used_pct','session_reset_at','attribution')}
    result['weekly_used_pct']=percentage(result['weekly_used_pct'])
    for name in ('observed_at','collected_at','weekly_reset_at'):
        result[name]=iso(read_time(result[name]))
    if result['session_used_pct'] is not None:
        result['session_used_pct']=percentage(result['session_used_pct'])
    if result['session_reset_at'] is not None:
        result['session_reset_at']=iso(read_time(result['session_reset_at']))
    if result['attribution']!='UNATTRIBUTED_CLOUD_WORK':
        raise ValueError('cloud attribution unsupported in v1')
    if not isinstance(result['source'],str) or len(result['source'])>32:
        raise ValueError('invalid source')
    return result


def get_codexbar():
    found=shutil.which('codexbar')
    if found:return found
    for name in ('~/token-governor/bin/codexbar','~/token-governor/bin/CodexBarCLI',
                 '~/bin/codexbar','~/bin/CodexBarCLI','/opt/homebrew/bin/codexbar',
                 '/usr/local/bin/codexbar'):
        path=os.path.expanduser(name)
        if os.path.isfile(path) and os.access(path,os.X_OK): return path
    raise RuntimeError('CodexBar CLI not found; install/sign in on Wolfram first')


def capture_source():
    cmd=[get_codexbar(),'usage','--provider','codex','--source','oauth','--format','json']
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=75,check=False)
    if r.returncode!=0:
        # deliberately don't print stderr: it could contain account identifiers
        raise RuntimeError('CodexBar failed (nonzero exit); verify Codex sign-in locally')
    return json.loads(r.stdout)


def connect_db(path):
    fn=Path(path).expanduser();fn.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(str(fn))
    os.chmod(fn, 0o600)  # keep quota observations private on macOS
    con.execute('PRAGMA busy_timeout=5000')
    con.execute('''CREATE TABLE IF NOT EXISTS observations (
      observed_at TEXT PRIMARY KEY, weekly_reset_at TEXT NOT NULL,
      weekly_used_pct REAL NOT NULL, session_used_pct REAL, source TEXT NOT NULL,
      collected_at TEXT NOT NULL)''')
    con.execute('''CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
      kind TEXT NOT NULL, message TEXT NOT NULL, delivery TEXT NOT NULL DEFAULT 'PENDING')''')
    con.commit();return con


def previous_record(con,obs):
    row=con.execute('SELECT observed_at,weekly_reset_at,weekly_used_pct FROM observations '
                    'WHERE observed_at < ? ORDER BY observed_at DESC LIMIT 1',
                    (obs['observed_at'],)).fetchone()
    return dict(observed_at=row[0],weekly_reset_at=row[1],weekly_used_pct=row[2]) if row else None


def analyze(sample,previous=None,now=None,threshold=4.0,min_delta=2.0,max_age=90.0,
            min_remaining=20.0):
    now=now or dt.datetime.now(UTC)
    age=(now-read_time(sample['observed_at'])).total_seconds()/60
    out={'status':'BASELINE','alert':False,'weekly_remaining_pct':round(100-sample['weekly_used_pct'],3),
         'session_remaining_pct':None if sample['session_used_pct'] is None else round(100-sample['session_used_pct'],3),
         'observed_at':sample['observed_at'],'weekly_reset_at':sample['weekly_reset_at'],
         'source':sample['source'],'age_minutes':round(age,2),
         'attribution':'UNATTRIBUTED_CLOUD_WORK'}
    if age < -5 or age > max_age:
        out['status']='STALE';out['alert']=True;return out
    if out['weekly_remaining_pct'] < min_remaining:
        out['status']='LOW_BUDGET';out['alert']=True;return out
    if previous is None:return out
    if previous['weekly_reset_at']!=sample['weekly_reset_at']:
        out['status']='RESET_CHANGED';return out
    span=(read_time(sample['observed_at'])-read_time(previous['observed_at'])).total_seconds()
    if span<=0:
        out['status']='DUPLICATE_OR_OLD';return out
    delta=sample['weekly_used_pct']-previous['weekly_used_pct']
    out['delta_used_pp']=round(delta,3)
    if delta<0:
        out['status']='RECONCILIATION';return out
    if span<600:
        out['status']='INTERVAL_TOO_SHORT';return out
    out['burn_pp_per_hour']=round(delta*3600/span,3)
    if delta>=min_delta and out['burn_pp_per_hour']>=threshold:
        out['status']='BURN_SPIKE';out['alert']=True
    else:
        out['status']='NORMAL'
    return out


def make_alert(con,result,now,cooldown_hours=6):
    cutoff=iso(now-dt.timedelta(hours=cooldown_hours))
    found=con.execute('SELECT id FROM alerts WHERE kind=? AND created_at>=? LIMIT 1',
                      (result['status'],cutoff)).fetchone()
    if found:return None
    message='Token Governor P1: '+result['status']+'; weekly_remaining='+str(result.get('weekly_remaining_pct','unknown'))+\
        '%; burn_pp_per_hour='+str(result.get('burn_pp_per_hour','unknown'))+\
        '; source='+str(result.get('source','unknown'))+'; attribution=UNATTRIBUTED_CLOUD_WORK'
    cur=con.execute('INSERT INTO alerts(created_at,kind,message) VALUES(?,?,?)',
                    (iso(now),result['status'],message))
    con.commit()
    return cur.lastrowid


def record_failure(db,issue=None,now=None):
    now=now or dt.datetime.now(UTC)
    con=connect_db(db)
    try:
        result={'status':'PROBE_UNAVAILABLE','alert':True,'reason':'NO_FRESH_MEASUREMENT',
                'allow_governed_expensive_work':False,'attribution':'UNATTRIBUTED_CLOUD_WORK'}
        result['alert_id']=make_alert(con,result,now)
        result.update(notify_issue(con,issue) if issue else {'delivery':'LOCAL_LEDGER_ONLY'})
        return result
    finally:con.close()

def notify_issue(con,issue):
    if not issue:return {'delivery':'DISABLED'}
    if not ISSUE_PATTERN.fullmatch(issue):
        return {'delivery':'INVALID_ISSUE_CONFIG'}
    gh=shutil.which('gh')
    if gh is None:
        for candidate in ('/opt/homebrew/bin/gh','/usr/local/bin/gh'):
            if os.path.isfile(candidate) and os.access(candidate,os.X_OK):
                gh=candidate;break
    if not gh:
        return {'delivery':'GH_NOT_INSTALLED'}
    repo,num=issue.split('#')
    rows=con.execute("SELECT id,message FROM alerts WHERE delivery='PENDING' ORDER BY id LIMIT 3").fetchall()
    count=0
    for id_,message in rows:
        cmd=[gh,'issue','comment',num,'--repo',repo,'--body',message+'\nRead-only pilot, no auto-execution.']
        try:
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=25,check=False)
            if result.returncode:
                return {'delivery':'GH_FAILED','delivered':count}
            con.execute("UPDATE alerts SET delivery='GITHUB_SENT' WHERE id=?",(id_,))
            con.commit();count+=1
        except (OSError,subprocess.TimeoutExpired):
            return {'delivery':'GH_FAILED','delivered':count}
    return {'delivery':'GITHUB_SENT' if count else 'NO_PENDING_ALERTS','delivered':count}


def ingest(sample,db,max_age=90,threshold=4,min_delta=2,min_remaining=20,issue=None,now=None):
    obs=validate_sample(sample)
    now=now or dt.datetime.now(UTC)
    con=connect_db(db)
    try:
        existing=con.execute('SELECT 1 FROM observations WHERE observed_at=?',(obs['observed_at'],)).fetchone()
        previous=previous_record(con,obs)
        result=analyze(obs,previous,now,threshold,min_delta,max_age,min_remaining)
        if existing:
            result['status']='DUPLICATE';result['alert']=False
        if result['status']!='STALE' and not existing:
            con.execute('INSERT INTO observations VALUES(?,?,?,?,?,?)',
                        (obs['observed_at'],obs['weekly_reset_at'],obs['weekly_used_pct'],
                         obs['session_used_pct'],obs['source'],obs['collected_at']))
            con.commit()
        if result['alert']:
            alert_id=make_alert(con,result,now)
            result['alert_id']=alert_id
        if issue:
            result.update(notify_issue(con,issue))
        else:result['delivery']='LOCAL_LEDGER_ONLY'
        return result
    finally:con.close()


def remote_probe(host):
    if not HOST_PATTERN.fullmatch(host) or host.startswith('-'):
        raise ValueError('invalid SSH host; use user@tailscale-name')
    cmd=['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
         '-o','ConnectTimeout=10','-o','ForwardAgent=no',host,
         'python3 "$HOME/token-governor/governor.py" probe']
    res=subprocess.run(cmd,capture_output=True,text=True,timeout=95,check=False)
    if res.returncode:
        raise RuntimeError('SSH probe unavailable; check trusted host key, login and CodexBar')
    return json.loads(res.stdout)


def latest_status(db,max_age=90,min_remaining=20):
    con=connect_db(db)
    try:
        row=con.execute('SELECT observed_at,weekly_reset_at,weekly_used_pct,session_used_pct,source '
                        'FROM observations ORDER BY observed_at DESC LIMIT 1').fetchone()
        if not row:return {'status':'UNAVAILABLE','reason':'NO_OBSERVATIONS','allow_governed_expensive_work':False}
        age=(dt.datetime.now(UTC)-read_time(row[0])).total_seconds()/60
        result={'status':'FRESH' if -5<=age<=max_age else 'STALE','age_minutes':round(age,2),
                'observed_at':row[0],'weekly_reset_at':row[1],
                'weekly_remaining_pct':round(100-row[2],2),
                'session_remaining_pct':None if row[3] is None else round(100-row[3],2),
                'source':row[4],'attribution':'UNATTRIBUTED_CLOUD_WORK'}
        result['allow_governed_expensive_work']=result['status']=='FRESH' and result['weekly_remaining_pct']>=min_remaining
        return result
    finally:con.close()


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='action',required=True)
    probe=sub.add_parser('probe',help='Run CodexBar locally and emit sanitized sample')
    probe.add_argument('--fixture',help='Test input only: local raw CodexBar JSON')
    poll=sub.add_parser('poll',help='Darwin SSH pull, classify and optionally notify')
    poll.add_argument('--host',required=True,help='SSH target, e.g. user@wolfram')
    ingest_parser=sub.add_parser('ingest',help='Read sanitized sample from stdin or a file')
    ingest_parser.add_argument('--file',help='Read sanitized JSON file instead of stdin')
    for s in (poll,ingest_parser):
        s.add_argument('--db',default=DEFAULT_DB)
        s.add_argument('--max-age-min',type=float,default=90)
        s.add_argument('--burn-threshold',type=float,default=4)
        s.add_argument('--min-delta',type=float,default=2)
        s.add_argument('--min-weekly-remaining',type=float,default=20)
        s.add_argument('--notify-issue',help='Optional Github gh CLI: owner/repo#issue')
    status=sub.add_parser('status',help='Cached status (no network calls)')
    status.add_argument('--db',default=DEFAULT_DB)
    status.add_argument('--max-age-min',type=float,default=90)
    status.add_argument('--min-weekly-remaining',type=float,default=20)
    args=p.parse_args(argv)
    try:
        if args.action=='probe':
            if args.fixture:
                with open(args.fixture,encoding='utf-8') as f: raw=json.load(f)
            else:raw=capture_source()
            out=sanitize_codexbar(raw)
            print(json.dumps(out,ensure_ascii=False,sort_keys=True));return 0
        if args.action=='status':
            out=latest_status(args.db,args.max_age_min,args.min_weekly_remaining)
            print(json.dumps(out,ensure_ascii=False,sort_keys=True))
            return 0 if out['allow_governed_expensive_work'] else 3
        if args.action=='poll':
            sample=remote_probe(args.host)
        else:
            if args.file:
                with open(args.file,encoding='utf-8') as f: sample=json.load(f)
            else: sample=json.load(sys.stdin)
        result=ingest(sample,args.db,args.max_age_min,args.burn_threshold,args.min_delta,
                      args.min_weekly_remaining,args.notify_issue)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 2 if result['alert'] else 0
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError,json.JSONDecodeError) as ex:
        # Do not expose raw CLI stderr or auth details. Poll failures are durable P1 alerts.
        if args.action=='poll':
            result=record_failure(args.db,args.notify_issue)
            print(json.dumps(result,sort_keys=True));return 3
        print(json.dumps({'status':'UNAVAILABLE','reason':type(ex).__name__,
                          'allow_governed_expensive_work':False},sort_keys=True))
        return 3

if __name__=='__main__':sys.exit(main())