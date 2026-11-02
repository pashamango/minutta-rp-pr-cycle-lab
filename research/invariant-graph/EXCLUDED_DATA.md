# Documented Excluded Data Catalog (Issue #168)
**Task Reference:** MIN-18 | **Author:** `agy@wolfram`  
**Upstream Source:** [pashamango/minutta-rp-pr-cycle-lab#168](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168)  
**Total Cataloged Excluded Records:** 20  
**Epistemic Rule:** Do not treat heartbeat records or automated status ticks as discoveries.  

---

## 1. Constitutional Exclusion Policy

Per the task acceptance criteria:
> *«Ingest first 30–50 meaningful comments from upstream Issue #168 without treating heartbeat records as discoveries... documented excluded data. No giant mirror of GitHub comments.»*

Automated runner receipts (`GITHUB_RUN_RECEIPT/v1`), periodic health pings, hourly execution counters, and empty NO-OP cycles are strictly **excluded from claim extraction**. While essential for operational observability, treating execution receipts as epistemic claims introduces semantic clutter, distorts graph topology, and creates false discovery inflation.

---

## 2. Excluded Record Classification Criteria

| Record Pattern | Classification | Rationale for Exclusion |
|---|---|---|
| `GITHUB_RUN_RECEIPT/v1` | Automated Telemetry | Contains run timestamps, observed run markers, and execution status checks without hypothesis or empirical discovery. |
| `status: NO-OP` / `status: <NO-OP>` | Execution No-Op | Explicitly declares zero new information discovered during the hourly cycle. |
| `observed_run_time: ...` | Heartbeat Pulse | Routine cron telemetry emitted by runner schedulers. |

---

## 3. Catalog of Excluded Records (Direct Source Audit)

| Source ID | Timestamp | Scheduler | Record Type | Excerpt Snippet |
|---|---|---|---|---|
| [6199466905](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6199466905) | `2026-10-15T18:34:47Z` | `Golden Research Step` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Golden Research Step observed_run_time: 2026-10-15T11:33:00-07:00 run_marker: Golden-Research-Step--2026-10-15T11:33:00-07:00 o |
| [6199832727](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6199832727) | `2026-10-15T18:52:39Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T11:51:59-07:00 run_marker: MorningResearchCounsel-Model |
| [6200571059](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6200571059) | `2026-10-15T19:30:53Z` | `Golden Research Step` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Golden Research Step observed_run_time: 2026-10-15T12:29:20-07:00 run_marker: Golden-Research-Step--2026-10-15T12:29:20-07:00 o |
| [6200930557](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6200930557) | `2026-10-15T19:50:35Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T12:49:37-07:00 run_marker: MorningResearchCounsel-Model |
| [6201740312](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6201740312) | `2026-10-15T20:35:30Z` | `Golden Research Step` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Golden Research Step observed_run_time: 2026-10-15T13:33:45-07:00 run_marker: Golden-Research-Step--2026-10-15T13:33:45-07:00 o |
| [6202042386](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6202042386) | `2026-10-15T20:52:48Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T13:51:49-07:00 run_marker: MorningResearchCounsel-Model |
| [6202792649](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6202792649) | `2026-10-15T21:36:31Z` | `Golden Research Step` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Golden Research Step observed_run_time: 2026-10-15T14:34:50-07:00 run_marker: Golden-Research-Step--2026-10-15T14:34:50-07:00 o |
| [6203025704](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6203025704) | `2026-10-15T21:51:16Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T14:50:39-07:00 run_marker: MorningResearchCounsel-Model |
| [6203642252](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6203642252) | `2026-10-15T22:32:35Z` | ``Golden Research Step`` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 - scheduler: `Golden Research Step` - observed_run_time: `2026-10-15T15:29:50-07:00` - run_marker: `Golden-Research-Step--2026-10-15T15:2 |
| [6203982549](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6203982549) | `2026-10-15T22:55:35Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T15:54:50-07:00 run_marker: MorningResearchCounsel-Model |
| [6204429710](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6204429710) | `2026-10-15T23:29:12Z` | ``Golden Research Step`` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 - scheduler: `Golden Research Step` - observed_run_time: `2026-10-15T16:27:38-07:00` - run_marker: `Golden-Research-Step--2026-10-15T16:2 |
| [6204685427](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6204685427) | `2026-10-15T23:49:16Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T16:48:15-07:00 run_marker: MorningResearchCounsel-Model |
| [6205302218](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6205302218) | `2026-10-16T00:36:32Z` | ``Golden Research Step`` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 - scheduler: `Golden Research Step` - observed_run_time: `2026-10-15T17:34:58-07:00` - run_marker: `Golden-Research-Step--2026-10-15T17:3 |
| [6205488980](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6205488980) | `2026-10-16T00:50:56Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T17:50:19-07:00 run_marker: MorningResearchCounsel-Model |
| [6205971204](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6205971204) | `2026-10-16T01:31:25Z` | ``Golden Research Step`` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 - scheduler: `Golden Research Step` - observed_run_time: `2026-10-15T18:28:26-07:00` - run_marker: `Golden-Research-Step--2026-10-15T18:2 |
| [6206201993](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6206201993) | `2026-10-16T01:50:12Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T18:49:25-07:00 run_marker: MorningResearchCounsel-Model |
| [6206691947](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6206691947) | `2026-10-16T02:29:24Z` | ``Golden Research Step`` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 - scheduler: `Golden Research Step` - observed_run_time: `2026-10-15T19:27:24-07:00` - run_marker: `Golden-Research-Step--2026-10-15T19:2 |
| [6206924724](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6206924724) | `2026-10-16T02:49:43Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T19:48:54-07:00 run_marker: MorningResearchCounsel-Model |
| [6207414432](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6207414432) | `2026-10-16T03:28:04Z` | ``Golden Research Step`` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 - scheduler: `Golden Research Step` - observed_run_time: `2026-10-15T20:25:23-07:00` - run_marker: `Golden-Research-Step--2026-10-15T20:2 |
| [6207686450](https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-6207686450) | `2026-10-16T03:52:34Z` | `Morning Research Counsel -- Model Unknown` | `GITHUB_RUN_RECEIPT/v1` | GITHUB_RUN_RECEIPT/v1 scheduler: Morning Research Counsel -- Model Unknown observed_run_time: 2026-10-15T20:51:47-07:00 run_marker: MorningResearchCounsel-Model |

---
## 4. Verification Check
All 20 sampled records above were verified directly against GitHub Issue #168. None contain a hypothesis, observation, or empirical falsification claim. Their exclusion ensures the Invariant Graph remains a pure semantic knowledge representation.
