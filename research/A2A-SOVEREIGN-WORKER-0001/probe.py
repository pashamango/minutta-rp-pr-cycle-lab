#!/usr/bin/env python3
"""Disposable, loopback-free A2A/ACP-like sovereignty boundary probe.

The coordinator and worker are separate objects with an explicit allow-list;
no filesystem, shell, browser, credential, or account capability is exposed.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


PRIVATE_SENTINEL = "LP_PRIVATE_SENTINEL_NEVER_DELEGATED"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass
class Worker:
    private_fixture: str = PRIVATE_SENTINEL
    completed: dict[str, dict] = field(default_factory=dict)
    cancelled: set[str] = field(default_factory=set)

    def capability_card(self) -> dict:
        return {
            "protocol": "sovereign-worker-card/v1",
            "task_classes": ["public.echo"],
            "privacy_class": "private-host-never-delegated",
            "runtime_class": "local-deterministic",
            "budget": {"max_tasks": 1, "availability": "bounded"},
        }

    def dispatch(self, envelope: dict) -> dict:
        task_id = envelope["task_id"]
        if task_id in self.completed:
            return self.completed[task_id]
        if task_id in self.cancelled:
            return {"task_id": task_id, "state": "cancelled"}
        if envelope.get("task_class") != "public.echo":
            return {"task_id": task_id, "state": "denied", "reason": "task_class_not_allowed"}
        if set(envelope) - {"task_id", "task_class", "input"}:
            return {"task_id": task_id, "state": "denied", "reason": "unknown_capability_request"}
        result = {"echo": envelope["input"]}
        response = {
            "task_id": task_id,
            "state": "completed",
            "progress": [{"state": "accepted"}, {"state": "completed"}],
            "artifact": result,
            "evidence_sha256": digest({"task_id": task_id, "artifact": result}),
        }
        self.completed[task_id] = response
        return response

    def cancel(self, task_id: str) -> dict:
        self.cancelled.add(task_id)
        return {"task_id": task_id, "state": "cancelled"}


def run() -> dict:
    worker = Worker()
    card = worker.capability_card()
    envelope = {"task_id": "synthetic-001", "task_class": "public.echo", "input": "public fixture"}
    first = worker.dispatch(envelope)
    duplicate = worker.dispatch(envelope)
    denied = worker.dispatch({"task_id": "synthetic-002", "task_class": "shell.exec", "input": "cat private"})
    denied_primitive = worker.dispatch({"task_id": "synthetic-003", "task_class": "public.echo", "input": "x", "filesystem": "read"})
    cancelled = worker.cancel("synthetic-004")
    after_cancel = worker.dispatch({"task_id": "synthetic-004", "task_class": "public.echo", "input": "x"})
    transcript = json.dumps({"card": card, "responses": [first, duplicate, denied, denied_primitive, cancelled, after_cancel]}, sort_keys=True)
    return {
        "capability_card": card,
        "first": first,
        "duplicate": duplicate,
        "denied": denied,
        "denied_primitive": denied_primitive,
        "cancelled": cancelled,
        "after_cancel": after_cancel,
        "private_fixture_exposed": PRIVATE_SENTINEL in transcript,
        "worker_capabilities": ["dispatch(public.echo)", "cancel(task_id)"],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
