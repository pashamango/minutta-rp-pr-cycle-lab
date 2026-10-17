"""Deterministic synthetic fixture tests for MIN-74 (NICLI-B) Linear dispatcher and lease harness."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from nicli_dispatcher import (
    DispatcherConfig,
    DispatcherError,
    HostResourceState,
    LeaseStore,
    LinearIssueSnapshot,
    NicliDispatcher,
    NicliJob,
    NicliRunReceipt,
    QuotaState,
    ReviewerReceipt,
    ScopedPublisher,
    WorkerOutcome,
    compute_task_revision_hash,
    evaluate_admission,
)


def make_candidate(**overrides) -> LinearIssueSnapshot:
    base = LinearIssueSnapshot(
        issue_id="MIN-68",
        uuid="544f6b52-0af3-4243-bc27-575d077a75db",
        team_key="MIN",
        status="Todo",
        title="[MIN-67.1] Semantics Gate: Freeze Exact Wheel Model",
        description="Implement exact pure mathematical reference model.",
        labels=("Role: Builder-Ready",),
        updated_at="2026-10-16T22:15:58.118Z",
        parent_id="MIN-67",
        parent_status="In Progress",
        parent_labels=("Role: PM-Watch",),
        ic_decision_ref="PRD-2-IC-2026-10-15",
        handoff_refs=("MIN-067_Execution_Plan.md", "AGENT_HANDOFF_LOG.md", "repo_workspace/ORIGIN.toml"),
        blocked_by=(),
        source_repo="pashamango/minutta-rp-pr-cycle-lab",
        source_commit="f0f420a" + "0" * 33,
        allowed_paths=("dark_math/", "tests/"),
        capabilities=("local-tests-only",),
        acceptance_commands=("python3 -m unittest",),
        git_branch_name="minutta/min-68-min-671-semantics-gate-freeze-exact-wheel-model",
    )
    return replace(base, **overrides)


class FakeLinearTransport:
    def __init__(self, pages: list[list[LinearIssueSnapshot]] | None = None, live_by_id: dict[str, LinearIssueSnapshot] | None = None):
        self.pages = pages or [[]]
        self.live_by_id = dict(live_by_id or {})
        for page in self.pages:
            for item in page:
                self.live_by_id.setdefault(item.issue_id, item)

    def list_candidate_issues(self, cursor: str | None = None, limit: int = 50):
        idx = int(cursor) if cursor is not None else 0
        page = self.pages[idx] if idx < len(self.pages) else []
        next_cursor = str(idx + 1) if idx + 1 < len(self.pages) else None
        return list(page), next_cursor

    def get_issue(self, issue_id: str) -> LinearIssueSnapshot:
        return self.live_by_id[issue_id]


class FakeWorkerHarness:
    def __init__(self, handler=None):
        self.handler = handler
        self.calls: list[tuple[NicliJob, str]] = []

    def run(self, job: NicliJob, worker_credential_handle: str) -> WorkerOutcome:
        self.calls.append((job, worker_credential_handle))
        if self.handler:
            return self.handler(job, worker_credential_handle)
        out_file = Path(job.workspace) / "wheel_ref.py"
        out_file.write_text("WHEEL_REF = True\n", encoding="utf-8")
        return WorkerOutcome(
            exit_code=0,
            models_observed=(job.explicit_model,),
            turns_used=3,
            artifact_paths=("wheel_ref.py",),
            tests_run_and_results=({"command": "python3 -m unittest", "status": "pass"},),
            usage_observed_or_unknown={"prompt_tokens": 120, "completion_tokens": 80},
            host_resource_peak={"rss_bytes": 64 * 1024 * 1024, "disk_bytes": 4096},
        )


class NicliDispatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = LeaseStore(self.root / "state" / "leases.sqlite3")
        self.config = DispatcherConfig(
            host_id="darwin-pilot",
            explicit_model="gemini-2.5-flash-lite",
            cli_version="0.8.0",
        )
        self.publisher = ScopedPublisher(self.config.publisher_credential_handle)
        self.quota_ok = QuotaState(bucket="ai-studio-free-tier", status="AVAILABLE", remaining_requests=25)
        self.host_ok = HostResourceState(
            host_id="darwin-pilot",
            disk_free_bytes=20 * 1024 * 1024 * 1024,
            rss_Headroom_bytes=8 * 1024 * 1024 * 1024,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def make_dispatcher(self, linear: FakeLinearTransport, worker: FakeWorkerHarness) -> NicliDispatcher:
        return NicliDispatcher(
            config=self.config,
            store=self.store,
            linear=linear,
            worker=worker,
            publisher=self.publisher,
            workspace_root=self.root / "workspaces",
        )

    def test_empty_queue_and_admission_rejections_make_zero_model_calls(self) -> None:
        worker = FakeWorkerHarness()
        empty_disp = self.make_dispatcher(FakeLinearTransport([[]]), worker)
        res = empty_disp.poll_and_dispatch(now="2026-10-16T23:00:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res["status"], "IDLE_EMPTY_QUEUE")
        self.assertEqual(res["model_calls"], 0)
        self.assertEqual(len(worker.calls), 0)

        # Unmet dependency (MIN-69 blocked by MIN-68) + parent conflicting role (MIN-67 Architect-Needed) + missing repo
        blocked_dep = make_candidate(issue_id="MIN-69", blocked_by=({"id": "MIN-68", "status": "Todo"},))
        conflicting_parent = make_candidate(
            issue_id="MIN-68",
            parent_labels=("Role: PM-Watch", "Role: Architect-Needed"),
        )
        missing_repo = make_candidate(issue_id="MIN-70", source_repo=None)
        vetoed = make_candidate(issue_id="MIN-71", labels=("Role: Builder-Ready", "Human-Hold"))

        ineligible_disp = self.make_dispatcher(
            FakeLinearTransport([[blocked_dep, conflicting_parent], [missing_repo, vetoed]]),
            worker,
        )
        res2 = ineligible_disp.poll_and_dispatch(now="2026-10-16T23:01:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res2["status"], "NO_ELIGIBLE_TASKS")
        self.assertEqual(res2["model_calls"], 0)
        self.assertEqual(
            res2["rejections"],
            {
                "MIN-69": "UNMET_DEPENDENCY",
                "MIN-68": "CONFLICTING_ROLE_STATE",
                "MIN-70": "MISSING_REPOSITORY_OR_ACCEPTANCE",
                "MIN-71": "VETO_OR_HOLD",
            },
        )
        self.assertEqual(len(worker.calls), 0)

    def test_duplicate_and_concurrent_claims_and_wip_one_limit(self) -> None:
        snap = make_candidate()
        rev = compute_task_revision_hash(snap)
        lease1 = self.store.claim_lease(
            issue_id="MIN-68",
            task_revision_hash=rev,
            attempt_id="att-1",
            now="2026-10-16T23:00:00Z",
            ttl_s=900,
            max_wip=1,
        )
        self.assertEqual(lease1.lease_generation, 1)

        # Duplicate claim for same issue fails with ALREADY_CLAIMED
        with self.assertRaises(DispatcherError) as ctx1:
            self.store.claim_lease(
                issue_id="MIN-68",
                task_revision_hash=rev,
                attempt_id="att-2",
                now="2026-10-16T23:01:00Z",
                ttl_s=900,
                max_wip=1,
            )
        self.assertEqual(ctx1.exception.code, "ALREADY_CLAIMED")

        # Concurrent claim for a second eligible issue fails because WIP=1
        with self.assertRaises(DispatcherError) as ctx2:
            self.store.claim_lease(
                issue_id="MIN-69",
                task_revision_hash="b" * 64,
                attempt_id="att-3",
                now="2026-10-16T23:01:00Z",
                ttl_s=900,
                max_wip=1,
            )
        self.assertEqual(ctx2.exception.code, "WIP_LIMIT_REACHED")

    def test_crash_restart_requires_isolation_and_fences_stale_generation(self) -> None:
        snap = make_candidate()
        rev = compute_task_revision_hash(snap)
        lease1 = self.store.claim_lease(
            issue_id="MIN-68",
            task_revision_hash=rev,
            attempt_id="att-1",
            now="2026-10-16T23:00:00Z",
            ttl_s=60,
            max_wip=1,
            max_attempts=2,
        )
        # After lease expiry (23:02:00Z > 23:01:00Z), replacement is STILL blocked until predecessor is isolated
        with self.assertRaises(DispatcherError) as ctx_unisolated:
            self.store.claim_lease(
                issue_id="MIN-68",
                task_revision_hash=rev,
                attempt_id="att-2",
                now="2026-10-16T23:02:00Z",
                ttl_s=60,
                max_wip=1,
                max_attempts=2,
            )
        self.assertEqual(ctx_unisolated.exception.code, "PREDECESSOR_NOT_ISOLATED")

        # Confirm old worker process is stopped and isolated
        self.store.confirm_worker_stopped_and_isolated(issue_id="MIN-68", lease_generation=lease1.lease_generation)

        # Now replacement claim succeeds with monotonic generation=2
        restarted_store = LeaseStore(self.store.db_path)
        lease2 = restarted_store.claim_lease(
            issue_id="MIN-68",
            task_revision_hash=rev,
            attempt_id="att-2",
            now="2026-10-16T23:02:05Z",
            ttl_s=600,
            max_wip=1,
            max_attempts=2,
        )
        self.assertEqual(lease2.lease_generation, 2)

        # Late heartbeat or late result from generation 1 is rejected by fencing check
        with self.assertRaises(DispatcherError) as ctx_stale:
            restarted_store.heartbeat(
                issue_id="MIN-68",
                attempt_id="att-1",
                lease_generation=1,
                now="2026-10-16T23:02:10Z",
                ttl_s=600,
            )
        self.assertEqual(ctx_stale.exception.code, "STALE_FENCING_GENERATION")

        with self.assertRaises(DispatcherError) as ctx_stale_verify:
            restarted_store.verify_fencing(
                issue_id="MIN-68",
                attempt_id="att-1",
                lease_generation=1,
                now="2026-10-16T23:02:10Z",
            )
        self.assertEqual(ctx_stale_verify.exception.code, "STALE_FENCING_GENERATION")

    def test_changed_spec_and_veto_at_boundaries(self) -> None:
        snap = make_candidate()
        edited_snap = make_candidate(description="Mutated spec mid-flight")
        worker = FakeWorkerHarness()
        # Spec changed between list_candidate_issues and get_issue before claim
        disp = self.make_dispatcher(FakeLinearTransport([[snap]], {"MIN-68": edited_snap}), worker)
        res = disp.poll_and_dispatch(now="2026-10-16T23:00:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res["status"], "BLOCKED_AT_CLAIM_BOUNDARY")
        self.assertEqual(res["blocker"], "SPEC_REVISION_CHANGED")
        self.assertEqual(len(worker.calls), 0)

        # Veto applied mid-flight while worker is running (caught before publication)
        linear_veto = FakeLinearTransport([[snap]], {"MIN-68": snap})

        def veto_during_run(job: NicliJob, cred: str) -> WorkerOutcome:
            linear_veto.live_by_id["MIN-68"] = make_candidate(labels=("Role: Builder-Ready", "Human-Hold"))
            (Path(job.workspace) / "wheel_ref.py").write_text("x = 1\n", encoding="utf-8")
            return WorkerOutcome(
                exit_code=0,
                models_observed=(job.explicit_model,),
                turns_used=2,
                artifact_paths=("wheel_ref.py",),
                tests_run_and_results=({"command": "python3 -m unittest", "status": "pass"},),
            )

        disp_veto = self.make_dispatcher(linear_veto, FakeWorkerHarness(veto_during_run))
        res_veto = disp_veto.poll_and_dispatch(now="2026-10-16T23:05:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res_veto["status"], "ABORTED_VETO_AT_BOUNDARY")
        self.assertEqual(res_veto["receipt"]["blocker"], "VETO_OR_HOLD")
        self.assertTrue(res_veto["receipt"]["END"])
        self.assertFalse(res_veto["receipt"]["DONE"])
        self.assertEqual(len(self.publisher.published_branches), 0)

    def test_unknown_or_exhausted_quota_and_billing_fail_closed(self) -> None:
        snap = make_candidate()
        worker = FakeWorkerHarness()
        disp = self.make_dispatcher(FakeLinearTransport([[snap]]), worker)

        unknown_quota = QuotaState(bucket="ai-studio-free-tier", status="UNKNOWN", remaining_requests=None)
        with self.assertRaises(DispatcherError) as ctx_unk:
            disp.poll_and_dispatch(now="2026-10-16T23:00:00Z", quota=unknown_quota, host=self.host_ok)
        self.assertEqual(ctx_unk.exception.code, "QUOTA_UNKNOWN")

        exhausted_quota = QuotaState(bucket="ai-studio-free-tier", status="EXHAUSTED", remaining_requests=0)
        with self.assertRaises(DispatcherError) as ctx_exh:
            disp.poll_and_dispatch(now="2026-10-16T23:00:00Z", quota=exhausted_quota, host=self.host_ok)
        self.assertEqual(ctx_exh.exception.code, "QUOTA_EXHAUSTED")

        paid_quota = QuotaState(bucket="paid", status="AVAILABLE", remaining_requests=100, billing_enabled=True)
        with self.assertRaises(DispatcherError) as ctx_paid:
            disp.poll_and_dispatch(now="2026-10-16T23:00:00Z", quota=paid_quota, host=self.host_ok)
        self.assertEqual(ctx_paid.exception.code, "BILLING_FORBIDDEN")
        self.assertEqual(len(worker.calls), 0)

    def test_timeout_full_disk_and_http_401_403_429_controls(self) -> None:
        # 1. Host full disk preflight pauses dispatcher without running worker
        snap = make_candidate()
        worker = FakeWorkerHarness()
        disp = self.make_dispatcher(FakeLinearTransport([[snap]]), worker)
        low_disk_host = HostResourceState(host_id="darwin-pilot", disk_free_bytes=1024, rss_Headroom_bytes=10**9)
        with self.assertRaises(DispatcherError) as ctx_disk:
            disp.poll_and_dispatch(now="2026-10-16T23:00:00Z", quota=self.quota_ok, host=low_disk_host)
        self.assertEqual(ctx_disk.exception.code, "HOST_DISK_FULL_OR_PRESSURE")
        self.assertTrue(self.store.is_paused())
        self.store.set_paused(False)

        # 2. Timeout / turn limit
        disp_timeout = self.make_dispatcher(
            FakeLinearTransport([[make_candidate(issue_id="MIN-68")]]),
            FakeWorkerHarness(
                lambda job, _: WorkerOutcome(
                    exit_code=124,
                    models_observed=(job.explicit_model,),
                    turns_used=13,
                    timed_out=True,
                )
            ),
        )
        res_to = disp_timeout.poll_and_dispatch(now="2026-10-16T23:01:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res_to["status"], "TIMED_OUT_OR_TURN_LIMIT")
        self.assertTrue(res_to["receipt"]["END"])
        self.assertFalse(res_to["receipt"]["DONE"])

        # 3. HTTP 429 bounded Retry-After backoff
        disp_429 = self.make_dispatcher(
            FakeLinearTransport([[make_candidate(issue_id="MIN-69")]]),
            FakeWorkerHarness(
                lambda job, _: WorkerOutcome(
                    exit_code=1,
                    models_observed=(job.explicit_model,),
                    turns_used=1,
                    http_status=429,
                    retry_after_s=180,
                )
            ),
        )
        res_429 = disp_429.poll_and_dispatch(now="2026-10-16T23:02:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res_429["status"], "FAILED_PROVIDER_RATE_LIMIT_429")
        self.assertEqual(res_429["receipt"]["retry_backoff_s"], 180)
        self.assertFalse(self.store.is_paused())

        # 4. HTTP 401/403 stops and pauses new workers
        disp_401 = self.make_dispatcher(
            FakeLinearTransport([[make_candidate(issue_id="MIN-70")]]),
            FakeWorkerHarness(
                lambda job, _: WorkerOutcome(
                    exit_code=1,
                    models_observed=(job.explicit_model,),
                    turns_used=1,
                    http_status=401,
                )
            ),
        )
        res_401 = disp_401.poll_and_dispatch(now="2026-10-16T23:03:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res_401["status"], "FAILED_PROVIDER_AUTH_401")
        self.assertTrue(self.store.is_paused())

    def test_missing_artifact_and_exit0_with_failed_tests_never_claim_done(self) -> None:
        # Case A: Exit 0 with failed tests
        disp_fail_test = self.make_dispatcher(
            FakeLinearTransport([[make_candidate(issue_id="MIN-68")]]),
            FakeWorkerHarness(
                lambda job, _: WorkerOutcome(
                    exit_code=0,
                    models_observed=(job.explicit_model,),
                    turns_used=2,
                    artifact_paths=("wheel_ref.py",),
                    tests_run_and_results=({"command": "python3 -m unittest", "status": "fail"},),
                )
            ),
        )
        res_ft = disp_fail_test.poll_and_dispatch(now="2026-10-16T23:00:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res_ft["status"], "EXIT0_WITH_FAILED_OR_MISSING_TESTS")
        self.assertEqual(res_ft["receipt"]["blocker"], "TESTS_FAILED")
        self.assertTrue(res_ft["receipt"]["END"])
        self.assertFalse(res_ft["receipt"]["DONE"])

        # Case B: Exit 0 with passing tests, but declared artifact is missing on disk
        disp_missing_art = self.make_dispatcher(
            FakeLinearTransport([[make_candidate(issue_id="MIN-69")]]),
            FakeWorkerHarness(
                lambda job, _: WorkerOutcome(
                    exit_code=0,
                    models_observed=(job.explicit_model,),
                    turns_used=2,
                    artifact_paths=("nonexistent.py",),
                    tests_run_and_results=({"command": "python3 -m unittest", "status": "pass"},),
                )
            ),
        )
        res_ma = disp_missing_art.poll_and_dispatch(now="2026-10-16T23:01:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(res_ma["status"], "ARTIFACT_PUBLICATION_FAILED:MISSING_ARTIFACT")
        self.assertEqual(res_ma["receipt"]["blocker"], "MISSING_ARTIFACT")
        self.assertTrue(res_ma["receipt"]["END"])
        self.assertFalse(res_ma["receipt"]["DONE"])

    def test_credential_separation_protected_branch_guard_and_independent_qa_done(self) -> None:
        snap = make_candidate(issue_id="MIN-68")
        worker = FakeWorkerHarness()
        disp = self.make_dispatcher(FakeLinearTransport([[snap]]), worker)
        res = disp.poll_and_dispatch(now="2026-10-16T23:10:00Z", quota=self.quota_ok, host=self.host_ok)

        # Verify worker only received worker credential handle and manifest has no Linear/publisher secrets
        job_sent, cred_sent = worker.calls[0]
        self.assertEqual(cred_sent, self.config.worker_credential_handle)
        manifest_text = (Path(job_sent.workspace) / "nicli-job.json").read_text(encoding="utf-8")
        self.assertNotIn(self.config.dispatcher_credential_handle, manifest_text)
        self.assertNotIn(self.config.publisher_credential_handle, manifest_text)

        # Builder finishes at In Review + QA-Needed with END=True, DONE=False
        self.assertEqual(res["status"], "COMPLETED_AWAITING_QA")
        self.assertEqual(res["linear_projection"], "In Review + QA-Needed")
        self.assertTrue(res["receipt"]["END"])
        self.assertFalse(res["receipt"]["DONE"])

        # Protected branch 'main' is strictly rejected by publisher
        lease = self.store.get_lease("MIN-68")
        assert lease is not None
        with self.assertRaises(DispatcherError) as ctx_branch:
            self.publisher.publish_review_branch(
                lease=lease,
                job=job_sent,
                branch_name="main",
                workspace_dir=Path(job_sent.workspace),
                artifact_rel_paths=("wheel_ref.py",),
            )
        self.assertEqual(ctx_branch.exception.code, "PROTECTED_OR_INVALID_BRANCH")

        # Independent GPT reviewer verifies artifacts and certifies DONE=True
        builder_receipt = NicliRunReceipt(
            **{
                **res["receipt"],
                "models_observed": tuple(res["receipt"]["models_observed"]),
                "tool_receipts": tuple(res["receipt"]["tool_receipts"]),
                "tests_run_and_results": tuple(res["receipt"]["tests_run_and_results"]),
            }
        )
        manifest_sha = hashlib.sha256(
            json.dumps(builder_receipt.artifact_refs_and_sha256, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        review = ReviewerReceipt(
            receipt_id="qa-min68-001",
            reviewer_role="GPT",
            issue_id="MIN-68",
            attempt_id=builder_receipt.attempt_id,
            lease_generation=builder_receipt.lease_generation,
            task_revision_hash=builder_receipt.task_revision_hash,
            artifact_manifest_sha256=manifest_sha,
            verdict="PASS",
            checks_rerun=True,
            reviewed_at="2026-10-16T23:15:00Z",
        )
        final_receipt = disp.record_independent_qa(prior_receipt=builder_receipt, review=review)
        self.assertTrue(final_receipt.END)
        self.assertTrue(final_receipt.DONE)
        self.assertEqual(final_receipt.reviewer_receipt_ref, "qa-min68-001")
        self.assertEqual(len(self.store.list_receipts("MIN-68")), 2)

    def test_separate_api_free_tier_and_antigravity_pro_auth_quota_lanes(self) -> None:
        # 1. Cross-lane quota bucket mixing in config or runtime is rejected
        with self.assertRaises(DispatcherError) as ctx_cfg_mix:
            DispatcherConfig(
                host_id="wolfram",
                explicit_model="gemini-4-argon-medium",
                cli_version="1.4.0",
                auth_mode="antigravity_google_ai_pro",
                quota_bucket="ai-studio-free-tier",
            ).validate()
        self.assertEqual(ctx_cfg_mix.exception.code, "QUOTA_BUCKET_MISMATCH")

        # 2. Automatic model upgrade is forbidden
        with self.assertRaises(DispatcherError) as ctx_auto_upg:
            DispatcherConfig(
                host_id="wolfram",
                explicit_model="gemini-4-argon-medium",
                cli_version="1.4.0",
                auth_mode="antigravity_google_ai_pro",
                quota_bucket="antigravity-google-ai-pro",
                allow_auto_model_upgrade=True,
            ).validate()
        self.assertEqual(ctx_auto_upg.exception.code, "AUTO_MODEL_UPGRADE_FORBIDDEN")

        # 3. Antigravity Google AI Pro worker lane on Wolfram: rejects paid overages, unknown quota, or wrong bucket
        ag_config = DispatcherConfig(
            host_id="wolfram",
            explicit_model="gemini-4-argon-medium",
            cli_version="1.4.0",
            auth_mode="antigravity_google_ai_pro",
            quota_bucket="antigravity-google-ai-pro",
            worker_credential_handle="keychain://mindrock/antigravity-pro-session",
        )
        worker = FakeWorkerHarness()
        ag_disp = NicliDispatcher(
            config=ag_config,
            store=self.store,
            linear=FakeLinearTransport([[make_candidate(issue_id="MIN-68")]]),
            worker=worker,
            publisher=self.publisher,
            workspace_root=self.root / "ag_workspaces",
        )

        # Runtime bucket mismatch (passing AI Studio quota to Antigravity worker) fails closed
        with self.assertRaises(DispatcherError) as ctx_rt_mix:
            ag_disp.poll_and_dispatch(now="2026-10-16T23:20:00Z", quota=self.quota_ok, host=self.host_ok)
        self.assertEqual(ctx_rt_mix.exception.code, "QUOTA_BUCKET_MISMATCH")

        # Paid overages enabled on Antigravity subscription fails closed
        ag_overage_quota = QuotaState(
            bucket="antigravity-google-ai-pro",
            status="AVAILABLE",
            remaining_requests=10,
            free_only=False,
            billing_enabled=False,
            overage_billing_enabled=True,
            subscription_tier="google_ai_pro",
        )
        with self.assertRaises(DispatcherError) as ctx_overage:
            ag_disp.poll_and_dispatch(now="2026-10-16T23:20:00Z", quota=ag_overage_quota, host=self.host_ok)
        self.assertEqual(ctx_overage.exception.code, "BILLING_FORBIDDEN")

        # Unknown Antigravity quota fails closed
        ag_unknown_quota = QuotaState(
            bucket="antigravity-google-ai-pro",
            status="UNKNOWN",
            remaining_requests=None,
            free_only=False,
            billing_enabled=False,
            overage_billing_enabled=False,
            subscription_tier="google_ai_pro",
        )
        with self.assertRaises(DispatcherError) as ctx_ag_unk:
            ag_disp.poll_and_dispatch(now="2026-10-16T23:20:00Z", quota=ag_unknown_quota, host=self.host_ok)
        self.assertEqual(ctx_ag_unk.exception.code, "QUOTA_UNKNOWN")
        self.assertEqual(len(worker.calls), 0)

        # Valid bounded Antigravity Google AI Pro quota succeeds and records auth_mode + pinned model
        ag_valid_quota = QuotaState(
            bucket="antigravity-google-ai-pro",
            status="AVAILABLE",
            remaining_requests=15,
            free_only=False,
            billing_enabled=False,
            overage_billing_enabled=False,
            subscription_tier="google_ai_pro",
        )
        res_ag = ag_disp.poll_and_dispatch(now="2026-10-16T23:21:00Z", quota=ag_valid_quota, host=self.host_ok)
        self.assertEqual(res_ag["status"], "COMPLETED_AWAITING_QA")
        self.assertEqual(res_ag["receipt"]["auth_mode"], "antigravity_google_ai_pro")
        self.assertEqual(res_ag["receipt"]["model_requested"], "gemini-4-argon-medium")
        self.assertEqual(res_ag["receipt"]["models_observed"], ["gemini-4-argon-medium"])
        self.assertTrue(res_ag["receipt"]["END"])
        self.assertFalse(res_ag["receipt"]["DONE"])


if __name__ == "__main__":
    unittest.main()
