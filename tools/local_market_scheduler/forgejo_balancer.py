"""Private Forgejo-backed launcher and two-host balancer.

The API client is intentionally credential-agnostic: callers inject an
authenticated transport.  The default launcher uses the existing SSH config
(`darwin`) and never forwards credentials or starts a listener.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Callable, Iterable, Protocol

from .scheduler import Host, Job, Scheduler


class ForgejoTransport(Protocol):
    def ready_jobs(self) -> Iterable[dict]: ...


class Launcher(Protocol):
    def launch(self, host: str, job: Job) -> dict: ...


@dataclass(frozen=True)
class LaunchResult:
    host: str
    task_id: str
    lease_id: str
    command: tuple[str, ...]


class SshLauncher:
    """Launch a bounded local worker command over an existing SSH alias."""

    def __init__(self, aliases: dict[str, str] | None = None,
                 runner: Callable[..., subprocess.CompletedProcess] = subprocess.run):
        self.aliases = aliases or {"darwin": "darwin", "wolfram": "localhost"}
        self.runner = runner

    def launch(self, host: str, job: Job) -> dict:
        if host not in self.aliases:
            raise ValueError(f"unknown host: {host}")
        # The remote command is data-only and uses the task binding as args;
        # shell interpretation is never involved.
        command = ("python3", "-m", "tools.local_market_scheduler.worker",
                   "--task-id", job.task_id, "--source-digest", job.source_digest,
                   "--lease-id", job.lease_id)
        argv = ("ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
                self.aliases[host], *command)
        result = self.runner(list(argv), check=True, capture_output=True, text=True)
        return {"host": host, "task_id": job.task_id, "lease_id": job.lease_id,
                "argv": list(argv), "stdout": result.stdout}


class ForgejoBalancer:
    """Poll, enqueue, dispatch at most one lease per host, and record events."""

    def __init__(self, transport: ForgejoTransport, launcher: Launcher,
                 scheduler: Scheduler):
        self.transport = transport
        self.launcher = launcher
        self.scheduler = scheduler

    def poll(self) -> list[dict]:
        for raw in self.transport.ready_jobs():
            required = {"task_id", "priority", "host_class", "source_digest"}
            if set(raw) != required:
                raise ValueError("Forgejo job shape must be exactly task_id/priority/host_class/source_digest")
            self.scheduler.enqueue(Job(**raw))
        decisions = self.scheduler.reconcile()
        launches = []
        for decision in decisions:
            job = self.scheduler.jobs[decision["task_id"]]
            result = self.launcher.launch(decision["host"], job)
            launches.append(result)
        return launches


class JsonForgejoTransport:
    """Read a local exported Forgejo queue; no network or secret handling."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def ready_jobs(self) -> list[dict]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("queue fixture must be a JSON list")
        return payload


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="run one private Forgejo balancer cycle")
    parser.add_argument("--queue", type=Path, required=True, help="local exported ready-job JSON")
    parser.add_argument("--db", type=Path, default=Path("local-market.sqlite"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    scheduler = Scheduler(str(args.db))
    scheduler.observe([Host("darwin", "available"), Host("wolfram", "available")])
    launcher = SshLauncher(runner=(lambda *a, **k: subprocess.CompletedProcess(a[0], 0, "DRY_RUN\n", "")) if args.dry_run else subprocess.run)
    launches = ForgejoBalancer(JsonForgejoTransport(args.queue), launcher, scheduler).poll()
    print(json.dumps(launches, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
