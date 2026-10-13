#!/usr/bin/env python3
"""DP-01 Darwin Prometheus: append-only private JSONL event journal + SQLite projection.

No dependency on Work, cloud API, secrets, or privileged machine access.
The quota collector is *read only*: it observes governor.py's durable SQLite.
Hashes detect accidental/unauthorized editing, NOT malicious re-signing by file owner.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile
from contextlib import contextmanager

UTC = dt.timezone.utc
SCHEMA = 'chitakasha.prometheus.event/v1'
GENESIS = '0' * 64
DEFAULT_ROOT = '~/.local/share/darwin-prometheus'
DEFAULT_GOVERNOR_DB = '~/.local/share/token-governor/observations.sqlite3'
MAX_EVENT_BYTES = 8192
ALLOWED = {'quota.observation', 'quota.alert', 'host.health'}
HEX64 = re.compile(r'^[0-9a-f]{64}$')
DATE_FILE = re.compile(r'^\d{4}-\d{2}-\d{2}\.jsonl$')


def iso(t):
    if t.tzinfo is None: raise ValueError('Timezone required')
    return t.astimezone(UTC).isoformat(timespec='seconds').replace('+00:00', 'Z')


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_time(value):
    if not isinstance(value, str): raise ValueError('Invalid timestamp')
    t = dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('Timestamp missing zone')
    return t


def valid_payload(event_type, payload):
    """Strict allowlisted fields. No dynamic hostnames, path or user identifiers."""
    if not isinstance(payload, dict): raise ValueError('Payload must be object')
    if event_type == 'quota.observation':
        required = {'observed_at','weekly_reset_at','weekly_used_pct','collected_at',
                    'session_used_pct','source','attribution'}
        if set(payload) != required: raise ValueError('Unexpected observation fields')
        for field in ('observed_at','weekly_reset_at','collected_at'):
            validate_time(payload[field])
        for field in ('weekly_used_pct','session_used_pct'):
            v=payload[field]
            if v is not None and (isinstance(v,bool) or not isinstance(v,(int,float)) or not 0 <= v <= 100):
                raise ValueError('Invalid percentage')
        if payload['weekly_used_pct'] is None: raise ValueError('Missing weekly usage')
        if payload['source'] not in {'oauth','cli','auto','web','local','api','unknown','rpc','codex_cli'}:
            raise ValueError('Unsafe provider label')
        if payload['attribution'] != 'UNATTRIBUTED_CLOUD_WORK':
            raise ValueError('Unsupported Work attribution')
    elif event_type == 'quota.alert':
        if set(payload) != {'created_at','kind','delivery'}: raise ValueError('Unexpected alert fields')
        validate_time(payload['created_at'])
        if payload['kind'] not in {'BURN_SPIKE','LOW_BUDGET','STALE','PROBE_UNAVAILABLE'}:
            raise ValueError('Invalid alert kind')
        if payload['delivery'] not in {'PENDING','LOCAL_LEDGER_ONLY','GITHUB_SENT','GH_FAILED','DISABLED'}:
            raise ValueError('Unsafe alert delivery')
    elif event_type == 'host.health':
        if set(payload) != {'sampled_at','load_1m','load_5m','load_15m','disk_free_bytes','disk_total_bytes'}:
            raise ValueError('Unexpected host data')
        validate_time(payload['sampled_at'])
        for k in ('load_1m','load_5m','load_15m'):
            v=payload[k]
            if not isinstance(v,(float,int)) or isinstance(v,bool) or v<0 or v>100000: raise ValueError('Bad load')
        for k in ('disk_free_bytes','disk_total_bytes'):
            v=payload[k]
            if isinstance(v,bool) or not isinstance(v,int) or v<0: raise ValueError('Bad disk')
        if payload['disk_free_bytes']>payload['disk_total_bytes']:raise ValueError('Free > total')
    else: raise ValueError('Unknown event type')


def files(root):
    folder=root/'journal'
    return sorted(p for p in folder.glob('*.jsonl') if DATE_FILE.fullmatch(p.name)) if folder.exists() else []


def audit(root):
    last=GENESIS; seq=0; ids=set(); by_type={}; last_segment=None; tips={0:GENESIS}; existing_payloads={}
    for path in files(root):
        with path.open('rb') as f:
            for line in f:
                if not line.endswith(b'\n'): raise ValueError('Torn JSONL write: '+path.name)
                if len(line)>MAX_EVENT_BYTES: raise ValueError('Oversize event')
                try: record=json.loads(line)
                except (ValueError,UnicodeDecodeError):raise ValueError('Invalid JSONL event')
                if not isinstance(record,dict):raise ValueError('Non-object JSONL event')
                expected_fields={'schema','seq','event_id','event_type','recorded_at','provenance',
                                 'payload','prev_hash','hash'}
                if set(record) != expected_fields: raise ValueError('Unexpected record fields')
                if record['schema'] != SCHEMA or record['seq'] != seq+1:
                    raise ValueError('Schema / sequence invalid')
                if record['prev_hash'] != last or not HEX64.fullmatch(str(record['hash'])):
                    raise ValueError('Broken hash chain')
                if digest(canonical({k:v for k,v in record.items() if k!='hash'})) != record['hash']:
                    raise ValueError('Tampered record detected')
                if not HEX64.fullmatch(str(record['event_id'])) or record['event_id'] in ids:
                    raise ValueError('Invalid/duplicate event identity')
                if record['provenance'] != 'SOURCE_READ_LOCAL':
                    raise ValueError('Unsupported source provenance')
                t=validate_time(record['recorded_at'])
                if t.astimezone(UTC).date().isoformat()+'.jsonl' != path.name:
                    raise ValueError('Record in wrong date partition')
                valid_payload(record['event_type'],record['payload'])
                seq += 1; last=record['hash']; ids.add(record['event_id']); existing_payloads[record['event_id']]=digest(canonical(record['payload']))
                by_type[record['event_type']]=by_type.get(record['event_type'],0)+1
                last_segment=path.name; tips[seq]=last
    for cp in sorted((root/'checkpoints').glob('*.json')) if (root/'checkpoints').exists() else []:
        if not re.fullmatch(r'\d{12}-[0-9a-f]{12}\.json',cp.name):
            raise ValueError('Invalid checkpoint filename')
        data=json.loads(cp.read_bytes())
        if set(data)!={'schema','count','tip','created_at'} or data['schema']!='chitakasha.prometheus.checkpoint/v1':
            raise ValueError('Invalid checkpoint')
        n=data['count']
        if not isinstance(n,int) or isinstance(n,bool) or n not in tips or data['tip']!=tips[n]:
            raise ValueError('Checkpoint mismatch or journal truncation')
        if cp.name!=f"{n:012d}-{tips[n][:12]}.json":
            raise ValueError('Renamed checkpoint')
        validate_time(data['created_at'])
    return {'count':seq,'tip':last,'ids':ids,'types':by_type,'last_segment':last_segment,'payload_hashes':existing_payloads}


@contextmanager
def locked(root):
    root.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(root,0o700)
    lock=root/'.writer.lock'
    fd=os.open(str(lock),os.O_CREAT|os.O_RDWR,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)


def syncdir(p):
    fd=os.open(str(p),os.O_RDONLY)
    try: os.fsync(fd)
    finally:os.close(fd)


def write_event(root,state,event_type,event_id,payload,recorded_at=None):
    valid_payload(event_type,payload)
    if not HEX64.fullmatch(event_id):raise ValueError('Invalid event id')
    if event_id in state['ids']:
        if state['payload_hashes'][event_id]!=digest(canonical(payload)):
            raise ValueError('Conflicting content for existing event id')
        return None
    recorded_at=recorded_at or dt.datetime.now(UTC)
    record={'schema':SCHEMA,'seq':state['count']+1,'event_id':event_id,
            'event_type':event_type,'recorded_at':iso(recorded_at),
            'provenance':'SOURCE_READ_LOCAL','payload':payload,'prev_hash':state['tip']}
    record['hash']=digest(canonical(record))
    raw=canonical(record)+b'\n'
    if len(raw)>MAX_EVENT_BYTES:raise ValueError('Event too large')
    journal=root/'journal'
    journal.mkdir(mode=0o700,exist_ok=True)
    os.chmod(journal,0o700)
    path=journal/(recorded_at.astimezone(UTC).date().isoformat()+'.jsonl')
    exists=path.exists()
    # Immutable chronological partitions; avoid appending into earlier-day files.
    if state['last_segment'] is not None and path.name < state['last_segment']:
        raise ValueError('Clock moved backward into old partition')
    fd=os.open(str(path),os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
    try:
        if not exists and os.fstat(fd).st_size: raise ValueError('Unexpected preexisting content')
        size=os.write(fd,raw)
        if size!=len(raw):raise OSError('Partial write; journal requires manual recovery')
        os.fsync(fd)
    finally:os.close(fd)
    if not exists:syncdir(journal)
    state['count']+=1;state['tip']=record['hash'];state['ids'].add(event_id)
    state['payload_hashes'][event_id]=digest(canonical(payload))
    state['types'][event_type]=state['types'].get(event_type,0)+1
    state['last_segment']=path.name
    return record


def event_id(kind,stable):
    return digest(canonical([SCHEMA,kind,stable]))


def read_governor(db):
    path=Path(db).expanduser()
    if not path.is_file(): raise FileNotFoundError('Governor SQLite missing')
    # Read-only URI. No modification, schema migration or credential access.
    con=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        rows=con.execute('SELECT observed_at,weekly_reset_at,weekly_used_pct,session_used_pct,source,collected_at FROM observations ORDER BY observed_at').fetchall()
        alerts=con.execute('SELECT id,created_at,kind,delivery FROM alerts ORDER BY id').fetchall()
    finally:con.close()
    observations=[]
    for observed,reset,weekly,session,source,collected in rows:
        payload={'observed_at':observed,'weekly_reset_at':reset,'weekly_used_pct':weekly,
                 'session_used_pct':session,'source':source,'collected_at':collected,
                 'attribution':'UNATTRIBUTED_CLOUD_WORK'}
        valid_payload('quota.observation',payload)
        observations.append((event_id('quota.observation',observed),payload))
    alert_data=[]
    for id_,created,kind,delivery in alerts:
        payload={'created_at':created,'kind':kind,'delivery':delivery}
        valid_payload('quota.alert',payload)
        alert_data.append((event_id('quota.alert',str(id_)+':'+delivery),payload))
    return observations,alert_data


def reconcile(root,db,now=None):
    # Read DB before acquiring ledger lock: governor writes independently.
    observations,alerts=read_governor(db)
    appended={'quota.observation':0,'quota.alert':0}
    with locked(root):
        state=audit(root)  # fail closed on any corruption, including torn write
        items_by_kind=[('quota.observation',observations),('quota.alert',alerts)]
        # Reconciliation conflict gate: old identity with changed content is not safe reuse.
        # Preflight before writing to avoid a partial batch on semantic conflicts.
        for kind,items in items_by_kind:
            for uid,payload in items:
                if uid in state['payload_hashes'] and state['payload_hashes'][uid]!=digest(canonical(payload)):
                    raise ValueError('Conflicting source record for existing event id')
        for kind,items in items_by_kind:
            for uid,payload in items:
                if write_event(root,state,kind,uid,payload,recorded_at=now):appended[kind]+=1
        return {'status':'SYNCED','appended':appended,'total':state['count'],'tip':state['tip']}


def host_health(root,now=None):
    now=now or dt.datetime.now(UTC)
    sizes=shutil.disk_usage(str(Path.home()))
    loads=os.getloadavg()
    payload={'sampled_at':iso(now),'load_1m':round(loads[0],3),'load_5m':round(loads[1],3),
             'load_15m':round(loads[2],3),'disk_free_bytes':sizes.free,'disk_total_bytes':sizes.total}
    with locked(root):
        state=audit(root)
        event=write_event(root,state,'host.health',event_id('host.health',iso(now)),payload,recorded_at=now)
        return {'status':'SYNCED' if event else 'DUPLICATE','total':state['count'],'tip':state['tip']}


def project(root):
    with locked(root):
        state=audit(root)
        root.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd,tmp=tempfile.mkstemp(prefix='.projection-',suffix='.sqlite3',dir=root)
        os.close(fd);os.chmod(tmp,0o600)
        try:
            con=sqlite3.connect(tmp)
            con.execute('CREATE TABLE events (seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL, event_type TEXT NOT NULL, recorded_at TEXT NOT NULL, provenance TEXT NOT NULL, payload_json TEXT NOT NULL, prev_hash TEXT NOT NULL, record_hash TEXT NOT NULL)')
            con.execute('CREATE INDEX events_by_type ON events(event_type, recorded_at)')
            for path in files(root):
                with path.open('rb') as f:
                    for line in f:
                        e=json.loads(line)
                        con.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?,?)',
                            (e['seq'],e['event_id'],e['event_type'],e['recorded_at'],e['provenance'],
                             canonical(e['payload']).decode('utf8'),e['prev_hash'],e['hash']))
            con.commit();con.close()
            os.replace(tmp,str(root/'ledger.sqlite3'))
            syncdir(root)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        return {'status':'PROJECTED','events':state['count'],'tip':state['tip']}


def checkpoint(root):
    with locked(root):
        state=audit(root)
        name=f"{state['count']:012d}-{state['tip'][:12]}.json"
        folder=root/'checkpoints';folder.mkdir(exist_ok=True,mode=0o700)
        path=folder/name
        data={'schema':'chitakasha.prometheus.checkpoint/v1','count':state['count'],
              'tip':state['tip'],'created_at':iso(dt.datetime.now(UTC))}
        try:fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError:return {'status':'ALREADY_CHECKPOINTED','count':state['count'],'tip':state['tip']}
        with os.fdopen(fd,'wb') as f:
            f.write(canonical(data)+b'\n');f.flush();os.fsync(f.fileno())
        syncdir(folder)
        return {'status':'CHECKPOINT_CREATED','file':name,'count':state['count'],
                'tip':state['tip'],'checkpoint_sha256':digest(path.read_bytes())}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default=DEFAULT_ROOT)
    s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('sync-governor');a.add_argument('--governor-db',default=DEFAULT_GOVERNOR_DB)
    s.add_parser('verify');s.add_parser('project');s.add_parser('checkpoint');s.add_parser('host-health')
    args=p.parse_args()
    root=Path(args.root).expanduser()
    try:
        if args.command=='sync-governor': result=reconcile(root,args.governor_db)
        elif args.command=='verify':
            with locked(root):
                d=audit(root)
            result={'status':'VERIFIED','events':d['count'],'tip':d['tip'],'types':d['types']}
        elif args.command=='project':result=project(root)
        elif args.command=='checkpoint':result=checkpoint(root)
        else:result=host_health(root)
        print(json.dumps(result,sort_keys=True));return 0
    except (OSError,ValueError,sqlite3.Error,TypeError) as exc:
        print(json.dumps({'status':'READ_BLOCKED' if isinstance(exc,(FileNotFoundError,PermissionError)) else 'INVALID',
                          'error_type':type(exc).__name__},sort_keys=True));return 3

if __name__=='__main__':sys.exit(main())