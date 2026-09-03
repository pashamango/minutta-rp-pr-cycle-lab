#!/usr/bin/env python3
"""Small, provider-neutral SHA-256 CAS proof-of-concept tool."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            if path.read_bytes() != data:
                raise RuntimeError(f"immutable path collision: {path}")
            os.unlink(tmp)
        else:
            os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def ingest(namespace, source):
    data = source.read_bytes()
    sha = digest(data)
    target = namespace / "objects" / "sha256" / sha[:2] / sha[2:]
    existed = target.exists()
    atomic_write(target, data)
    if digest(target.read_bytes()) != sha:
        raise RuntimeError("object verification failed")
    return {"sha256": sha, "size": len(data), "deduplicated": existed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("ingest"); p.add_argument("source", type=Path)
    p = sub.add_parser("manifest"); p.add_argument("--name", required=True); p.add_argument("entries", nargs="+")
    p = sub.add_parser("root"); p.add_argument("manifest_sha256"); p.add_argument("--previous-root")
    p = sub.add_parser("reconstruct"); p.add_argument("manifest_sha256"); p.add_argument("destination", type=Path)
    args = parser.parse_args(); ns = args.namespace

    if args.command == "ingest":
        print(json.dumps(ingest(ns, args.source), sort_keys=True)); return
    if args.command == "manifest":
        entries = []
        for item in args.entries:
            logical, source = item.split("=", 1)
            result = ingest(ns, Path(source))
            entries.append({"path": logical, "sha256": result["sha256"], "size": result["size"]})
        value = {"schema": "chitakasha-manifest/v1", "name": args.name,
                 "entries": sorted(entries, key=lambda x: x["path"])}
        data = canonical(value); sha = digest(data)
        atomic_write(ns / "manifests" / "sha256" / f"{sha}.json", data)
        print(sha); return
    if args.command == "root":
        value = {"schema": "chitakasha-root/v1", "manifests": [args.manifest_sha256],
                 "previous_root": args.previous_root}
        data = canonical(value); sha = digest(data)
        atomic_write(ns / "roots" / "sha256" / f"{sha}.json", data)
        print(sha); return
    manifest_path = ns / "manifests" / "sha256" / f"{args.manifest_sha256}.json"
    manifest = json.loads(manifest_path.read_bytes())
    for entry in manifest["entries"]:
        source = ns / "objects" / "sha256" / entry["sha256"][:2] / entry["sha256"][2:]
        data = source.read_bytes()
        if len(data) != entry["size"] or digest(data) != entry["sha256"]:
            raise RuntimeError("stored object verification failed")
        target = args.destination / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(target, data)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"cas: {exc}", file=sys.stderr)
        raise SystemExit(1)
