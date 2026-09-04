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


def publish(namespace, source, name, ref):
    source = source.resolve(strict=True)
    files = [source] if source.is_file() else sorted(p for p in source.rglob("*") if p.is_file())
    entries = []
    for path in files:
        if path.is_symlink():
            raise RuntimeError("symlinks are not publishable")
        result = ingest(namespace, path)
        logical = path.name if source.is_file() else path.relative_to(source).as_posix()
        entries.append({"path": logical, "sha256": result["sha256"], "size": result["size"]})
    manifest = canonical({"schema": "chitakasha-manifest/v1", "name": name,
                          "entries": entries})
    manifest_sha = digest(manifest)
    atomic_write(namespace / "manifests/sha256" / f"{manifest_sha}.json", manifest)
    root = canonical({"schema": "chitakasha-root/v1", "manifests": [manifest_sha],
                      "previous_root": None})
    root_sha = digest(root)
    atomic_write(namespace / "roots/sha256" / f"{root_sha}.json", root)
    if digest((namespace / "manifests/sha256" / f"{manifest_sha}.json").read_bytes()) != manifest_sha:
        raise RuntimeError("manifest verification failed")
    if digest((namespace / "roots/sha256" / f"{root_sha}.json").read_bytes()) != root_sha:
        raise RuntimeError("root verification failed")
    if not ref or ref.startswith("/") or any(part in ("", ".", "..") for part in Path(ref).parts):
        raise RuntimeError("invalid ref")
    ref_path = namespace / "refs" / ref
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=ref_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            stream.write(root_sha + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, ref_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return {"manifest_sha256": manifest_sha, "root_sha256": root_sha,
            "ref": ref, "files": len(entries)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("ingest"); p.add_argument("source", type=Path)
    p = sub.add_parser("manifest"); p.add_argument("--name", required=True); p.add_argument("entries", nargs="+")
    p = sub.add_parser("root"); p.add_argument("manifest_sha256"); p.add_argument("--previous-root")
    p = sub.add_parser("reconstruct"); p.add_argument("manifest_sha256"); p.add_argument("destination", type=Path)
    p = sub.add_parser("publish"); p.add_argument("--name", required=True); p.add_argument("--ref", required=True); p.add_argument("source", type=Path)
    args = parser.parse_args(); ns = args.namespace

    if args.command == "ingest":
        print(json.dumps(ingest(ns, args.source), sort_keys=True)); return
    if args.command == "publish":
        print(json.dumps(publish(ns, args.source, args.name, args.ref), sort_keys=True)); return
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
