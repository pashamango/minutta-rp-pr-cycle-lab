"""Fail-closed quota forecasting and proposal engine.

This module only produces a report. It cannot spend, schedule, upgrade, launch,
or otherwise mutate a provider. Hours are a planning estimate, never a quota
conversion: each task pack declares its own expected provider units.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Mapping, Sequence

STALE_AFTER = timedelta(days=7)


def _parse(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class Quota:
    id: str
    provider: str
    amount: float | None
    unit: str
    window: str
    observed_at: datetime | str
    source: str
    confidence: float
    reset_at: datetime | str | None = None
    expires_at: datetime | str | None = None
    restrictions: tuple[str, ...] = ()
    reserved: float = 0.0
    used: float = 0.0

    def __post_init__(self):
        if not self.id or not self.provider or not self.unit or not self.source:
            raise ValueError("id, provider, unit, and observed source are required")
        if self.amount is not None and self.amount < 0:
            raise ValueError("amount cannot be negative")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.reserved < 0 or self.used < 0:
            raise ValueError("used and reserved cannot be negative")


@dataclass(frozen=True)
class Usage:
    quota_id: str
    amount: float
    observed_at: datetime | str


@dataclass(frozen=True)
class TaskPack:
    id: str
    title: str
    estimate_hours: float
    expected_outputs: tuple[str, ...]
    required_units: Mapping[str, float] = field(default_factory=dict)
    value: float = 0.0


@dataclass(frozen=True)
class OptimizerPolicy:
    now: datetime | str
    stale_after: timedelta = STALE_AFTER
    weekly_hours: float = 5.0
    reserve_ratio: float = 0.2
    max_proposal_hours: float = 10.0
    concurrent_windows: int = 1


@dataclass(frozen=True)
class OptimizationReport:
    overconsumption_alerts: tuple[str, ...]
    underutilized_quota_ids: tuple[str, ...]
    proposals: tuple[TaskPack, ...]
    excluded_quota_ids: tuple[str, ...]
    execution_policy: str = "REPORT_ONLY; human approval required"


def optimize(quotas: Sequence[Quota], packs: Sequence[TaskPack], policy: OptimizerPolicy) -> OptimizationReport:
    """Return conservative alerts and packs, excluding stale/unknown evidence."""
    now = _parse(policy.now)
    alerts: list[str] = []
    usable: dict[str, Quota] = {}
    excluded: list[str] = []
    for q in quotas:
        stale = now - _parse(q.observed_at) > policy.stale_after
        unknown = q.amount is None or q.confidence <= 0 or not q.source
        if stale or unknown:
            excluded.append(q.id)
            continue
        available = q.amount - q.used - q.reserved
        if available < 0:
            alerts.append(f"{q.id}: overconsumed by {-available:g} {q.unit}")
        elif q.used > q.amount:
            alerts.append(f"{q.id}: usage exceeds observed amount")
        usable[q.id] = q

    under: list[str] = []
    for q in usable.values():
        available = q.amount - q.used - q.reserved
        reserve = q.amount * policy.reserve_ratio
        if available > reserve and (q.expires_at is None or _parse(q.expires_at) > now):
            under.append(q.id)

    # A pack is eligible only if every declared unit fits after the reserve.
    # Sort by value/hour without pretending units are interchangeable with hours.
    candidates = []
    for pack in packs:
        if pack.estimate_hours <= 0 or pack.estimate_hours > policy.max_proposal_hours:
            continue
        if pack.estimate_hours > policy.weekly_hours * max(1, policy.concurrent_windows):
            continue
        if all(qid in usable and usable[qid].amount - usable[qid].used - usable[qid].reserved - usable[qid].amount * policy.reserve_ratio >= amount
               for qid, amount in pack.required_units.items()):
            candidates.append(pack)
    candidates.sort(key=lambda p: (p.value / p.estimate_hours if p.estimate_hours else 0, p.value), reverse=True)
    proposals: list[TaskPack] = []
    hours = 0.0
    for pack in candidates:
        if hours + pack.estimate_hours <= policy.weekly_hours * max(1, policy.concurrent_windows):
            proposals.append(pack)
            hours += pack.estimate_hours
    return OptimizationReport(tuple(alerts), tuple(sorted(under)), tuple(proposals), tuple(sorted(excluded)))
