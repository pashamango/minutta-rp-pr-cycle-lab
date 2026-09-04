#!/usr/bin/env python3
"""Resumable, source-preserving Documents to SHA-256 CAS migration worker."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import signal
import sqlite3
import stat
import subprocess
import tempfile
import time
from pathlib import Path

SCHEMA = "chitakasha-documents-migration/v1"
CHUNK = 8 * 1024 * 1024
STOP = False


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def atomic_replace(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)


def connect(state: Path) -> sqlite3.Connection:
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state, 0o700)
    db = sqlite3.connect(state / "checkpoints.sqlite3", timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.executescript("""
      CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS dirs(
        path BLOB PRIMARY KEY, status TEXT NOT NULL DEFAULT 'pending',
        attempts INTEGER NOT NULL DEFAULT 0, error TEXT);
      CREATE TABLE IF NOT EXISTS entries(
        path BLOB PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL,
        size INTEGER, mtime_ns INTEGER, dev INTEGER, ino INTEGER,
        digest TEXT, attempts INTEGER NOT NULL DEFAULT 0, error TEXT);
      CREATE TABLE IF NOT EXISTS objects(
        digest TEXT PRIMARY KEY, size INTEGER NOT NULL, created INTEGER NOT NULL);
    """)
    db.commit()
    return db


def rel_bytes(path: Path, source: Path) -> bytes:
    return os.fsencode(path.relative_to(source))


def abs_path(source: Path, raw: bytes) -> Path:
    return source / os.fsdecode(raw)


def initialize(db: sqlite3.Connection, source: Path, namespace: Path, t0: Path) -> None:
    existing = dict(db.execute("SELECT key,value FROM meta"))
    fixed = {"schema": SCHEMA, "source": os.fspath(source),
             "namespace": os.fspath(namespace), "t0_record": os.fspath(t0)}
    for key, value in fixed.items():
        if key in existing and existing[key] != value:
            raise RuntimeError(f"state binding mismatch: {key}")
        db.execute("INSERT OR IGNORE INTO meta VALUES(?,?)", (key, value))
    db.execute("INSERT OR IGNORE INTO meta VALUES('phase','enumerating')")
    db.execute("INSERT OR IGNORE INTO meta VALUES('started_at',?)", (str(time.time()),))
    db.execute("INSERT OR IGNORE INTO dirs(path) VALUES(?)", (b"",))
    # A crash between durable per-entry phases is safely replayable: CAS writes
    # are content-addressed and verified files are the only terminal rows.
    db.execute("UPDATE entries SET status='pending' WHERE status IN ('hydrating','hashed')")
    db.commit()


def request_hydration(path: Path) -> None:
    try:
        subprocess.run(["brctl", "download", os.fspath(path)], timeout=10,
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def enumerate_one(db: sqlite3.Connection, source: Path) -> bool:
    row = db.execute("SELECT path,attempts FROM dirs WHERE status IN ('pending','blocked') "
                     "AND attempts < 4 ORDER BY status='pending' DESC,path LIMIT 1").fetchone()
    if not row:
        return False
    parent = abs_path(source, row["path"])
    try:
        children = sorted(os.scandir(parent), key=lambda x: os.fsencode(x.name))
        values = []
        subdirs = []
        for child in children:
            path = Path(child.path)
            st = path.lstat()
            raw = rel_bytes(path, source)
            if stat.S_ISLNK(st.st_mode): kind, status = "symlink", "verified"
            elif stat.S_ISDIR(st.st_mode): kind, status = "directory", "verified"; subdirs.append(raw)
            elif stat.S_ISREG(st.st_mode): kind, status = "file", "pending"
            else: kind, status = "special", "blocked"
            values.append((raw, kind, status, st.st_size, st.st_mtime_ns, st.st_dev, st.st_ino,
                           "unsupported special entry" if kind == "special" else None))
        with db:
            db.executemany("INSERT INTO entries(path,kind,status,size,mtime_ns,dev,ino,error) "
                           "VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(path) DO NOTHING", values)
            db.executemany("INSERT OR IGNORE INTO dirs(path) VALUES(?)", ((p,) for p in subdirs))
            db.execute("UPDATE dirs SET status='done',attempts=attempts+1,error=NULL WHERE path=?", (row["path"],))
        return True
    except OSError as exc:
        request_hydration(parent)
        with db:
            db.execute("UPDATE dirs SET status='blocked',attempts=attempts+1,error=? WHERE path=?",
                       (f"{type(exc).__name__}: {exc}", row["path"]))
        return True


class EntryTimeout(RuntimeError):
    pass


def _alarm(_signum, _frame):
    raise EntryTimeout("bounded entry read timed out")


def ingest(path: Path, namespace: Path, timeout: int) -> tuple[str, int, bool]:
    staging = namespace / "staging" / "documents-0002"
    staging.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="object-", dir=staging)
    digest, size = hashlib.sha256(), 0
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(timeout)
    try:
        with path.open("rb", buffering=0) as src, os.fdopen(fd, "wb") as dst:
            while True:
                block = src.read(CHUNK)
                if not block: break
                digest.update(block); size += len(block); dst.write(block)
            dst.flush(); os.fsync(dst.fileno())
        value = digest.hexdigest()
        target = namespace / "objects" / "sha256" / value[:2] / value[2:]
        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        if existed:
            if target.stat().st_size != size: raise RuntimeError("CAS size collision")
            os.unlink(tmp)
        else:
            os.replace(tmp, target)
        check = hashlib.sha256()
        with target.open("rb", buffering=0) as stream:
            while block := stream.read(CHUNK): check.update(block)
        if check.hexdigest() != value or target.stat().st_size != size:
            raise RuntimeError("CAS verification failed")
        return value, size, existed
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, old)
        with contextlib.suppress(FileNotFoundError): os.unlink(tmp)


def process_one(db: sqlite3.Connection, source: Path, namespace: Path,
                timeout: int, retries: int) -> bool:
    row = db.execute("SELECT * FROM entries WHERE kind='file' AND status IN ('pending','blocked') "
                     "AND attempts < ? ORDER BY status='pending' DESC,path LIMIT 1", (retries,)).fetchone()
    if not row: return False
    path = abs_path(source, row["path"])
    try:
        first = path.stat()
        with db:
            db.execute("UPDATE entries SET status='hydrating' WHERE path=?", (row["path"],))
        request_hydration(path)
        digest, size, existed = ingest(path, namespace, timeout)
        with db:
            db.execute("UPDATE entries SET status='hashed',digest=?,size=? WHERE path=?",
                       (digest, size, row["path"]))
        second = path.stat()
        identity = (first.st_dev, first.st_ino, first.st_size, first.st_mtime_ns)
        after = (second.st_dev, second.st_ino, second.st_size, second.st_mtime_ns)
        if identity != after: raise RuntimeError("source changed during ingestion")
        with db:
            db.execute("INSERT OR IGNORE INTO objects VALUES(?,?,?)", (digest, size, 0 if existed else 1))
            db.execute("UPDATE entries SET status='verified',digest=?,size=?,mtime_ns=?,dev=?,ino=?,"
                       "attempts=attempts+1,error=NULL WHERE path=?",
                       (digest,size,second.st_mtime_ns,second.st_dev,second.st_ino,row["path"]))
        return True
    except Exception as exc:
        with db:
            db.execute("UPDATE entries SET status='blocked',attempts=attempts+1,error=? WHERE path=?",
                       (f"{type(exc).__name__}: {exc}", row["path"]))
        return True


def aggregates(db: sqlite3.Connection, lock_path: Path) -> dict:
    counts = {r[0]: r[1] for r in db.execute("SELECT kind,COUNT(*) FROM entries GROUP BY kind")}
    statuses = {r[0]: r[1] for r in db.execute("SELECT status,COUNT(*) FROM entries GROUP BY status")}
    dirs = dict(db.execute("SELECT status,COUNT(*) FROM dirs GROUP BY status"))
    logical = db.execute("SELECT COALESCE(SUM(size),0) FROM entries WHERE kind='file'").fetchone()[0]
    verified = db.execute("SELECT COUNT(*),COALESCE(SUM(size),0) FROM entries WHERE kind='file' AND status='verified'").fetchone()
    unique = db.execute("SELECT COALESCE(SUM(size),0) FROM objects WHERE created=1").fetchone()[0]
    running = False
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB); fcntl.flock(lock, fcntl.LOCK_UN)
        except BlockingIOError: running = True
    pending_dirs = sum(v for k,v in dirs.items() if k != "done")
    pending_files = db.execute("SELECT COUNT(*) FROM entries WHERE kind='file' AND status!='verified'").fetchone()[0]
    phase = "enumerating" if pending_dirs else ("acquiring" if pending_files else "converging")
    return {"phase": phase, "directories_enumerated": dirs.get("done",0),
            "entries_seen": sum(counts.values()), "regular_files": counts.get("file",0),
            "files_verified": verified[0], "logical_bytes_seen": logical,
            "verified_logical_bytes": verified[1], "unique_cas_bytes": unique,
            "deduplicated_bytes": max(0, verified[1]-unique), "icloud_hydrated": 0,
            "unresolved": statuses.get("blocked",0)+dirs.get("blocked",0),
            "changed_reingested": 0, "last_checkpoint": int(time.time()),
            "worker_state": "running" if running else "stopped"}


def write_status(db: sqlite3.Connection, state: Path) -> dict:
    value = aggregates(db, state / "worker.lock")
    atomic_replace(state / "status.json", canonical(value), 0o600)
    return value


def run(args) -> int:
    source, namespace, state = args.source.resolve(strict=True), args.namespace.resolve(), args.state.resolve()
    if source != Path.home() / "Documents" and not args.allow_test_source:
        raise RuntimeError("source must be the logical ~/Documents tree")
    db = connect(state); initialize(db, source, namespace, args.t0.resolve(strict=True))
    lock_path = state / "worker.lock"
    with lock_path.open("a+") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: return 73
        completed = 0
        while not STOP and (args.max_actions == 0 or completed < args.max_actions):
            did = enumerate_one(db, source) or process_one(db, source, namespace, args.timeout, args.retries)
            write_status(db, state)
            if did: completed += 1
            elif args.once: break
            else: time.sleep(args.idle_seconds)
    write_status(db, state); db.close(); return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    work = sub.add_parser("run")
    work.add_argument("--source", type=Path, required=True); work.add_argument("--namespace", type=Path, required=True)
    work.add_argument("--t0", type=Path, required=True); work.add_argument("--timeout", type=int, default=120)
    work.add_argument("--retries", type=int, default=3); work.add_argument("--idle-seconds", type=int, default=30)
    work.add_argument("--max-actions", type=int, default=0); work.add_argument("--once", action="store_true")
    work.add_argument("--allow-test-source", action="store_true", help=argparse.SUPPRESS)
    sub.add_parser("status")
    args = parser.parse_args()
    if args.command == "status":
        db = connect(args.state); print(json.dumps(write_status(db,args.state),sort_keys=True)); db.close(); return 0
    global STOP
    signal.signal(signal.SIGTERM, lambda *_: globals().__setitem__("STOP", True))
    signal.signal(signal.SIGINT, lambda *_: globals().__setitem__("STOP", True))
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
