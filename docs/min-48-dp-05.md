# MIN-48 DP-05

The optimizer keeps provider resources in explicit units and requires fresh,
source-backed observations. Unknown or stale observations are excluded from
both alerts and proposals. Reservations and a configurable reserve ratio are
deducted before a pack is considered. The default planning window is one
concurrent 5-hour weekly window; provider quota is never converted to hours.

`optimize()` is report-only: it cannot create accounts, spend, upgrade models,
schedule work, or launch Work. A human execution policy is required.
