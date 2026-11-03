#!/usr/bin/env python3
import unittest
import json
import os
import hashlib
import re
import math
from collections import Counter, defaultdict, deque

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV_DIR = os.path.join(BASE_DIR, "research", "invariant-graph")

class TestInvariantGraph(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(INV_DIR, "normalized_claims.json")) as f:
            self.claims = json.load(f)
        with open(os.path.join(INV_DIR, "claim_graph.json")) as f:
            self.graph = json.load(f)
        with open(os.path.join(INV_DIR, "falsification_specs.json")) as f:
            self.specs = json.load(f)
        with open(os.path.join(INV_DIR, "excluded_data.json")) as f:
            self.excluded = json.load(f)
        with open(os.path.join(INV_DIR, "direct_objects_cache.json")) as f:
            self.direct_objects = json.load(f)

    def test_claim_count_in_range(self):
        """Verify claim count is between 30 and 50 as mandated by MIN-18 (exactly 45)."""
        self.assertTrue(30 <= len(self.claims) <= 50, f"Expected 30-50 claims, got {len(self.claims)}")
        self.assertEqual(len(self.claims), 45)

    def test_claim_fields_complete(self):
        """Verify every claim unit possesses all required schema fields."""
        required = [
            "claim_id", "source_id", "source_url", "source_sha256",
            "exact_source_read_evidence", "canonical_invariant_id",
            "epistemic_label", "statement", "assumptions", "null_test",
            "contradictions", "duplicates", "duplicate_lineage",
            "applications", "versions", "scheduler", "domain", "cluster"
        ]
        for c in self.claims:
            for field in required:
                self.assertIn(field, c, f"Claim {c.get('claim_id')} missing field {field}")
            self.assertIn(c['epistemic_label'], ["fact", "hypothesis", "derived", "user testimony"])
            self.assertTrue(len(c['exact_source_read_evidence']) >= 50)
            self.assertIn("null_hypothesis", c['null_test'])
            self.assertIn("test_procedure", c['null_test'])
            self.assertIn("rejection_threshold", c['null_test'])

    def test_claim_fields_relevance_and_diversity(self):
        """Verify claim fields (assumptions, contradictions, rejection thresholds, applications) are semantically relevant, domain-grounded, and non-boilerplate."""
        total = len(self.claims)
        self.assertEqual(total, 45)

        # 1. 100% unique, domain-specific assumptions and contradictions per claim
        unique_assumptions = {str(c['assumptions']) for c in self.claims}
        self.assertEqual(len(unique_assumptions), 45, "Every claim must possess tailored, unique assumptions")

        unique_contradictions = {str(c['contradictions']) for c in self.claims}
        self.assertEqual(len(unique_contradictions), 45, "Every claim must possess tailored, unique contradictions")

        unique_applications = {str(c['applications']) for c in self.claims}
        self.assertEqual(len(unique_applications), 45, "Every claim must possess tailored, unique applications")

        # 2. Differentiated rejection thresholds tailored across systems, process, CRDT, cryptographic, and statistical domains
        unique_thresholds = {c['null_test']['rejection_threshold'] for c in self.claims}
        self.assertTrue(len(unique_thresholds) >= 20, f"Expected >= 20 domain-specific rejection thresholds, got {len(unique_thresholds)}")

        # 3. Elimination of generic boilerplate
        for c in self.claims:
            cid = c['claim_id']
            for a in c['assumptions']:
                self.assertNotIn("Standard operational context of scheduler", a, f"Generic scheduler boilerplate in {cid} assumptions")
            for cont in c['contradictions']:
                self.assertNotIn("Unbounded parameter tuning risks overfitting to synthetic evaluation suites.", cont, f"Generic overfitting boilerplate in {cid} contradictions")
            rej = c['null_test']['rejection_threshold']
            self.assertNotEqual(rej, "Empirical rejection at p < 0.01 / Bayes Factor > 20 / e-wealth > 100 without post-hoc selection.",
                                f"Generic uniform rejection threshold in {cid}")

        # 4. Structured Field Fixtures: rigorous verification of domain grounding,
        # essential prerequisite assumptions, concrete counter-mechanisms, operational computation,
        # quantitative decision boundaries, and strict procedure-threshold concordance.
        STRUCTURED_FIELD_FIXTURES = {
            'CLAIM-001': {
                'domain_entity': 'φ',
                'target_variable': 'held-out out-of-sample percentile',
                'computation': 'evaluate all six c/b/v permutations on a training split',
                'units': 'percentile',
                'comparison_operator': '<',
                'threshold_bound': '95.0%',
                'counter_mechanism': 'in-sample permutation selection produces apparent performance gain that collapses on held-out test splits',
                'assumption_prerequisite': 'triadic resource allocation can be parameterized on a 2-simplex',
                'app': 'triadic'
            },
            'CLAIM-002': {
                'domain_entity': 'adaptive',
                'target_variable': 'generalization performance',
                'computation': 'record `search_budget / candidate_count / selection_rule / frozen_at / heldout_evidence`',
                'units': 'delta',
                'comparison_operator': '>',
                'threshold_bound': '0.15',
                'counter_mechanism': 'agent architectures generating value claims by unconstrained post-hoc selection over unmetered variant pools',
                'assumption_prerequisite': 'search budget (variants, prompts, retries) can be audited and recorded at selection time',
                'app': 'evidence-contract'
            },
            'CLAIM-003': {
                'domain_entity': 'status',
                'target_variable': 'discordance between supervisor exit status and leaf pid kernel state',
                'computation': 'compare direct shell execution with the exact runner handoff',
                'units': 'percentage',
                'comparison_operator': '>',
                'threshold_bound': '0%',
                'counter_mechanism': 'transport wrapper timeout or connection drop reporting exit status 137 while leaf worker process continues running',
                'assumption_prerequisite': 'host os kernel exposes inspectable process trees and wait statuses via procfs or mach task apis',
                'app': 'cross-host'
            },
            'CLAIM-004': {
                'domain_entity': 'search',
                'target_variable': 'expected portfolio e-wealth e[e*]',
                'computation': 'adaptive search + e-process/held-out settlement',
                'units': 'e-wealth',
                'comparison_operator': '>',
                'threshold_bound': '1.0',
                'counter_mechanism': 'parallel agent branches creating new settlement capital through unconstrained retries without capital dilution',
                'assumption_prerequisite': 'evidence streams can be mapped to anytime-valid e-processes with expectation e[e] <= 1 under null',
                'app': 'conserved'
            },
            'CLAIM-005': {
                'domain_entity': 'ordered',
                'target_variable': 'forward 1:phi:phi^2 mapping',
                'computation': 'pre-register the forward role mapping c:b:v = 1:φ:φ²',
                'units': 'p-value',
                'comparison_operator': '<',
                'threshold_bound': '0.01',
                'counter_mechanism': 'reversed phase mapping (phi^2 : phi : 1) or arbitrary permutations outperforming canonical 1 : phi : phi^2 forward mapping',
                'assumption_prerequisite': 'cognitive task execution follows an irreversible three-phase pipeline',
                'app': 'phase-ordered'
            },
            'CLAIM-006': {
                'domain_entity': '1:φ:φ²',
                'target_variable': 'effect size difference between golden c:b split and uniform c:b split',
                'computation': 'evaluate effect size difference (cohen\'s d) with 95% confidence interval on held-out test splits',
                'units': 'cohen_d',
                'comparison_operator': '<',
                'threshold_bound': '0.20',
                'counter_mechanism': 'all measured advantage of 1:phi:phi^2 being driven entirely by coarse 50% future allocation',
                'assumption_prerequisite': 'value stage capacity can be decoupled from context/behavior sub-allocation',
                'app': 'ablation'
            },
            'CLAIM-007': {
                'domain_entity': 'valid',
                'target_variable': 'mean drift in log(e_t)',
                'computation': 'measure empirical mean drift in log(e_t) across 5,000 monte carlo steps under pure noise null',
                'units': 'drift',
                'comparison_operator': '>',
                'threshold_bound': '0.005',
                'counter_mechanism': 'ledger resets or selective reporting of highest-performing child branches bypassing conservation constraints',
                'assumption_prerequisite': 'log-transformed e-values provide additive coordinates for sequential evidence accounting',
                'app': 'additive'
            },
            'CLAIM-008': {
                'domain_entity': 'evidence',
                'target_variable': 'growth of evidence bits',
                'computation': 'simulate a broker with predeclared e-processes and settle only evidence-bit deltas',
                'units': 'bits',
                'comparison_operator': '>',
                'threshold_bound': '0.05 bits',
                'counter_mechanism': 'conflating evidence bits with transferable currency tokens leading to speculative gaming of scientific null tests',
                'assumption_prerequisite': 'evidence bits = log2(e-process wealth) measure accumulated information divergence from the null hypothesis',
                'app': 'information-theoretic'
            },
            'CLAIM-009': {
                'domain_entity': 'organizational',
                'target_variable': 'privilege escalation attack',
                'computation': 'validate the same request schema against google and forgejo fixtures',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'exchanging machine actor identity for organizational role allowing unauthorized privilege escalation',
                'assumption_prerequisite': 'identity dimensions in multi-agent systems are orthogonal and non-substitutable across organizational roles, provider principals, and machine runtime execution identities',
                'app': 'three-identity'
            },
            'CLAIM-010': {
                'domain_entity': 'weights',
                'target_variable': 'dimensional inconsistency or non-unit sum in allocated resource vector',
                'computation': 'verify that allocated resource vector satisfies unit sum |sum(w) - 1.0| <= 1e-6',
                'units': 'variance',
                'comparison_operator': '>',
                'threshold_bound': '1e-6',
                'counter_mechanism': 'applying golden trinity proportions across incompatible dimensions',
                'assumption_prerequisite': 'resource allocation requires a single commensurable underlying metric',
                'app': 'distribution'
            },
            'CLAIM-011': {
                'domain_entity': 'richest',
                'target_variable': 'portfolio e-value expectation e[e*]',
                'computation': 'clone one evidence stream with e-value e into m identities',
                'units': 'e-value',
                'comparison_operator': '>',
                'threshold_bound': '1.0',
                'counter_mechanism': 'dynamically re-allocating weights to post-hoc winning agents after observing favorable noise spikes',
                'assumption_prerequisite': 'ensemble of exploration agents can be bounded by a unit simplex weight vector w in delta_m',
                'app': 'admissible'
            },
            'CLAIM-012': {
                'domain_entity': 'weight',
                'target_variable': 'kraft sum over active hypothesis tree leaves',
                'computation': 'compute kraft sum over active hypothesis tree leaves sum(2^(-depth_i))',
                'units': 'sum',
                'comparison_operator': '>',
                'threshold_bound': '1.0 + 1e-7',
                'counter_mechanism': 'deeply nested hypothesis trees allocating branch weights that sum to greater than 1',
                'assumption_prerequisite': 'hypothesis exploration can be structured as a prefix-free tree over discrete decision codes',
                'app': 'tree-structured'
            },
            'CLAIM-013': {
                'domain_entity': 'ratio',
                'target_variable': 'non-invariance of optimal ratio under monotonic score rescaling',
                'computation': 'for each proposed measure, declare its admissible transformations and run a representation-invariance stress test',
                'units': 'percentage',
                'comparison_operator': '>',
                'threshold_bound': '10%',
                'counter_mechanism': 'attempting to verify 1:phi:phi^2 ratios using subjective likert ratings or arbitrary ordinal ranks',
                'assumption_prerequisite': 'evaluation of ratio claims requires an interval or ratio measurement scale',
                'app': 'measurement'
            },
            'CLAIM-014': {
                'domain_entity': 'mixture',
                'target_variable': 'sum of child branch initial capital',
                'computation': 'compare max-branch settlement, matched-budget held-out settlement, and preweighted e-mixture settlement',
                'units': 'capital',
                'comparison_operator': '>',
                'threshold_bound': 'w_parent',
                'counter_mechanism': 'spawning child agents with full duplicate betting capital without dividing parent endowment',
                'assumption_prerequisite': 'evidence capital represents finite statistical betting stock',
                'app': 'subagent'
            },
            'CLAIM-015': {
                'domain_entity': 'report',
                'target_variable': 'unsigned or invalidly signed memory artifact accepted',
                'computation': 'verify that an unverified but syntactically valid “successful result” cannot enter canonical reusable memory',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'agents consuming memory objects from shared caches without verifying cryptographic origin or schema integrity',
                'assumption_prerequisite': 'shared memory spaces are subject to pollution, byzantine corruption, or accidental mutation',
                'app': 'zero-trust'
            },
            'CLAIM-016': {
                'domain_entity': 'valid',
                'target_variable': 'presence of cycles in evidence dependency graph',
                'computation': 'attack a toy dag with duplicated observations, checking for presence of cycles and verifying invalidation recall',
                'units': 'percentage',
                'comparison_operator': '<',
                'threshold_bound': '100%',
                'counter_mechanism': 'cycles in evidence dag causing circular justification or infinite feedback loops',
                'assumption_prerequisite': 'evidence dependencies can be modeled as a directed acyclic graph',
                'app': 'git-like'
            },
            'CLAIM-017': {
                'domain_entity': 'report',
                'target_variable': 'task transition to in review permitted with dirty git working tree or unpushed commit sha',
                'computation': 'verify that handoff gate strictly rejects dirty git working tree or unpushed commit sha',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'agent claiming task completion based on local unpushed files or uncommitted workspace modifications',
                'assumption_prerequisite': 'git content-addressable storage serves as canonical immutable audit log',
                'app': 'handoff'
            },
            'CLAIM-018': {
                'domain_entity': 'conserved',
                'target_variable': 're-use of identical observation dataset increases aggregate evidence rank',
                'computation': 'a naive product gives 4 and should be rejected; a 50/50 mixture remains 2 and should pass',
                'units': 'rank',
                'comparison_operator': 'increases',
                'threshold_bound': 'initial singular rank',
                'counter_mechanism': 're-submitting the same observational dataset across multiple sub-hypotheses and treating them as statistically independent corroborations',
                'assumption_prerequisite': 'empirical observations possess linear logic properties: they cannot be cloned to double evidential power',
                'app': 'systems'
            },
            'CLAIM-019': {
                'domain_entity': 'provenance',
                'target_variable': 'linear correlation between dag depth and empirical effect size',
                'computation': 'compute linear correlation between dag depth and empirical effect size under randomized null benchmarks',
                'units': 'correlation',
                'comparison_operator': '>',
                'threshold_bound': '0.15',
                'counter_mechanism': 'assigning higher confidence to a hypothesis merely because its derivation graph is complex or multi-layered',
                'assumption_prerequisite': 'lineage depth and provenance complexity are orthogonal to empirical statistical strength',
                'app': 'provenance-strength'
            },
            'CLAIM-020': {
                'domain_entity': 'provenance',
                'target_variable': 'non-zero state delta or weight mutation',
                'computation': 'require the shadow algebra to reject shared-source products, permit disjoint-source products, and leave shared-source alternatives/mixtures representable',
                'units': 'delta',
                'comparison_operator': '>',
                'threshold_bound': '0',
                'counter_mechanism': 'audit operations mutating underlying claim weights or leaving fee residue that affects future scheduling',
                'assumption_prerequisite': 'auditing and inspecting provenance metadata must not alter system state or consume evidential capital',
                'app': 'zero-side-effect'
            },
            'CLAIM-021': {
                'domain_entity': 'evidence',
                'target_variable': 'multi-use of consumable evidence without holm-bonferroni or e-value multiple-testing adjustment',
                'computation': 'encode one toy evidence dag under two semantics',
                'units': 'percentage',
                'comparison_operator': '>',
                'threshold_bound': '5%',
                'counter_mechanism': 'treating empirical dataset as reusable without multiple-testing corrections',
                'assumption_prerequisite': 'empirical evidence is consumed by hypothesis testing (degrees of freedom loss), whereas invariant capabilities are reusable without exhaustion',
                'app': 'resource'
            },
            'CLAIM-022': {
                'domain_entity': 'consumer',
                'target_variable': 'acceptance of payload with mismatched content hash or unverified issuer authority signature',
                'computation': 'test acceptance of payload with mismatched content hash or unverified issuer authority signature, and require restart replay to remain idempotent',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'verifying file hash integrity while ignoring issuer key authorization',
                'assumption_prerequisite': 'cryptographic content hash (sha-256) and issuer authority signature are orthogonal dimensions of trust',
                'app': 'two-coordinate'
            },
            'CLAIM-023': {
                'domain_entity': 'golden',
                'target_variable': 'coordination overhead scaling exponent',
                'computation': 'measure coordination overhead scaling exponent under increasing agent team size n in triadic configurations',
                'units': 'exponent',
                'comparison_operator': '>=',
                'threshold_bound': '1.0',
                'counter_mechanism': 'ensembles of 1:phi:phi^2 agents exhibiting super-additive coordination collapse under team scaling',
                'assumption_prerequisite': 'multi-agent group allocations can be modeled as vector fields over context, behavior, and value',
                'app': 'multi-agent'
            },
            'CLAIM-024': {
                'domain_entity': 'golden',
                'target_variable': 'total variation distance between aggregate team allocation and canonical phi-simplex',
                'computation': 'construct two populations with identical unweighted distributions of distances ||p_i-g|| but swap which agents receive the largest t_i',
                'units': 'distance',
                'comparison_operator': '>',
                'threshold_bound': '0.08',
                'counter_mechanism': 'aggregated team allocation diverging exponentially from golden simplex under linear consensus updates',
                'assumption_prerequisite': 'convex combinations of individual agent allocation vectors remain within bounded distance of canonical phi-state',
                'app': 'decentralized'
            },
            'CLAIM-025': {
                'domain_entity': 'golden',
                'target_variable': 'misclassification rate',
                'computation': 'build four synthetic populations: (1) low b/low h, (2) low b/high h via cancelling deviations, (3) high b/low h via common shifted ratio, and (4) high b/high h',
                'units': 'percentage',
                'comparison_operator': '>',
                'threshold_bound': '5%',
                'counter_mechanism': 'claiming golden group dynamics based solely on scalar resource expenditure without verifying triadic shape alignment',
                'assumption_prerequisite': 'characterizing group behavior requires separating relative directional proportion from absolute resource intensity',
                'app': 'two-parameter'
            },
            'CLAIM-026': {
                'domain_entity': 'provenance',
                'target_variable': 'empirical type i error',
                'computation': 'four synthetic receipts: duplicate ancestry; disjoint ids with perfectly correlated latent source; genuinely conditionally valid sequential factor; post-hoc reweighting',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.01',
                'counter_mechanism': 'multiplying non-independent e-values using tensor product otimes, leading to catastrophic type i error inflation',
                'assumption_prerequisite': 'combining evidence requires explicit distinction between correlated streams (mixture oplus) and independent streams (product otimes)',
                'app': 'dependence-aware'
            },
            'CLAIM-027': {
                'domain_entity': 'evidence',
                'target_variable': 'capability grant succeeds when requested permissions exceed parent capability permissions',
                'computation': 'write a four-cell adversarial matrix testing capability attenuation and measuring privilege escalation rate',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'delegated capability tokens gaining new permissions or extending expiration timestamps beyond root capability (unauthorized privilege escalation)',
                'assumption_prerequisite': 'security and trust boundaries can be enforced via object-capability security models',
                'app': 'object-capability'
            },
            'CLAIM-028': {
                'domain_entity': 'evidence',
                'target_variable': 'intersection operation yielding non-subset capability',
                'computation': 'define tiny rules for `⊕`, `⊗`, and settlement; attack capability intersection to verify that cap_a intersect cap_b is strictly a subset of parent capabilities',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'intersection of two capability sets producing a permission not present in both parent sets',
                'assumption_prerequisite': 'capability composition follows lattice intersection; delegation follows monotone specialization',
                'app': 'capability'
            },
            'CLAIM-029': {
                'domain_entity': 'authority',
                'target_variable': 'confidence bound or validity domain of derived theorem exceeds empirical domain bound of supporting observations',
                'computation': 'encode evidencecapability dimensions as attenuating caveats and verify that derived theorem validity domain bound does not exceed empirical domain bound',
                'units': 'bound',
                'comparison_operator': 'exceeds',
                'threshold_bound': 'empirical domain bound',
                'counter_mechanism': 'derived conclusions claiming broader operational domains or higher confidence intervals than primary empirical measurements',
                'assumption_prerequisite': 'downstream mathematical and logical derivations cannot exceed evidentiary scope of their input empirical premises',
                'app': 'epistemic'
            },
            'CLAIM-030': {
                'domain_entity': 'authorization',
                'target_variable': 'join/meet operations on policy tuples violate semilattice associativity, commutativity, or idempotence',
                'computation': 'apply the same two caveats in opposite orders and require identical effective `(r,o)`; retry a child that restores a removed settlement right',
                'units': 'difference',
                'comparison_operator': '>',
                'threshold_bound': '0',
                'counter_mechanism': 'state mutation bypassing capability constraints',
                'assumption_prerequisite': 'multi-dimensional security policies form a bounded meet-semilattice',
                'app': 'algebraic'
            },
            'CLAIM-031': {
                'domain_entity': 'crdt',
                'target_variable': 'remote executor executes command with permissions exceeding transmitted token scope',
                'computation': 'define product partial order, verify aci merge laws, and test remote executor command containment failure rate',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'remote node discarding token constraints and executing commands under unrestricted local host privileges',
                'assumption_prerequisite': 'cross-host rpc channels can safely convey attenuated tokens without exposing root host credentials',
                'app': 'cross-host'
            },
            'CLAIM-032': {
                'domain_entity': 'averaging',
                'target_variable': 'kolmogorov-smirnov test fails to reject uniform equilibrium distribution',
                'computation': 'sample random initial allocations on the simplex; simulate multi-agent pairwise exchange and perform kolmogorov-smirnov test against uniform distribution',
                'units': 'p-value',
                'comparison_operator': '>=',
                'threshold_bound': '0.05',
                'counter_mechanism': 'simulated multi-agent interactions converging to arbitrary random fixed points while authors claim emergence of golden ratio',
                'assumption_prerequisite': 'emergence claims require demonstrating that interaction dynamics specifically select golden ratio over neighboring equilibria',
                'app': 'dynamical'
            },
            'CLAIM-033': {
                'domain_entity': 'monotone',
                'target_variable': 'state rollback or non-monotonic transition observed during out-of-order message replay',
                'computation': 'classify existing mailbox lifecycle transitions under history extension; for every transition labeled non-monotone, construct a minimal later-message counterexample',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'out-of-order message processing causing local task state to regress or overwrite completed work',
                'assumption_prerequisite': 'mailbox coordination can achieve consistency using monotonic conflict-free replicated data structures (crdts)',
                'app': 'decentralized'
            },
            'CLAIM-034': {
                'domain_entity': 'recurrence',
                'target_variable': 'spectral radius of iteration map deviates from golden ratio',
                'computation': 'sample positive initial pairs over several orders of magnitude and iterate the recurrence using exact integers or high precision; compute spectral radius',
                'units': 'deviation',
                'comparison_operator': '>',
                'threshold_bound': '1e-4',
                'counter_mechanism': 'resource rebalancing dynamics exhibiting chaotic divergence or limit cycles rather than converging to dominant eigenvector',
                'assumption_prerequisite': 'iterative resource rebalancing between memory and action can be formalized as a discrete linear dynamical system',
                'app': 'dynamical'
            },
            'CLAIM-035': {
                'domain_entity': 'monotone',
                'target_variable': 'stale superseded capability token accepted by authorization gate after successor issuance',
                'computation': 'spec-only adversarial matrix: copied token after expiry; paused executor resurrection; delegated right-widening; offline verifier',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.0%',
                'counter_mechanism': 'replay of superseded capability tokens accepted after valid successor publication',
                'assumption_prerequisite': 'distributed systems handle capability updates more cleanly via immutable successor pointers than asynchronous revocation broadcasts',
                'app': 'decentralized'
            },
            'CLAIM-036': {
                'domain_entity': 'causal',
                'target_variable': 'mutual information between cause and purpose feature vectors',
                'computation': 'for a sample of claim-units, obtain a cause-only explanation and a purpose model with preregistered u, horizon, and a feasible intervention',
                'units': 'mutual_information',
                'comparison_operator': '>',
                'threshold_bound': '0.15',
                'counter_mechanism': 'substituting mechanistic description for purpose specification leading to reward hacking and specification gaming',
                'assumption_prerequisite': 'causal mechanism (how an effect is produced) and teleological purpose (why/to what end) are mathematically non-substitutable',
                'app': 'goal-directed'
            },
            'CLAIM-037': {
                'domain_entity': 'task',
                'target_variable': 'task ranking under triplet (u, d_epsilon, omega) correlates negatively with actual collaborative problem-solving success',
                'computation': 'create matched research-task cards with the same causal background',
                'units': 'kendall_tau',
                'comparison_operator': '<',
                'threshold_bound': '0.20',
                'counter_mechanism': 'high difficulty score assigned to computationally trivial but poorly framed tasks',
                'assumption_prerequisite': 'task complexity is characterized by normative utility u, epsilon-tolerance difficulty d_epsilon, and future option expansion omega',
                'app': 'prioritization'
            },
            'CLAIM-038': {
                'domain_entity': 'bc-ur',
                'target_variable': 'decoding failure rate',
                'computation': 'on one existing degradation harness, compare static qr, sequential multipart qr, and bc-ur fountain multipart under matched payload/module/exposure budget',
                'units': 'rate',
                'comparison_operator': '>',
                'threshold_bound': '0.1%',
                'counter_mechanism': 'sequential multi-frame qr protocols outperforming rateless fountain codes under 20% frame loss',
                'assumption_prerequisite': 'air-gapped optical channels experience packet erasure and out-of-order frame capture',
                'app': 'air-gapped'
            },
            'CLAIM-039': {
                'domain_entity': 'observer-relative',
                'target_variable': 'priority score of candidate with high testing cost and vague predictions exceeds priority of candidate with cheap, definitive falsification test',
                'computation': 'create blinded candidate cards with identical p, t, and g but varying stated w/a; require independent reviewers to rank first tests before outcomes',
                'units': 'score',
                'comparison_operator': 'exceeds',
                'threshold_bound': 'priority of candidate with cheap, definitive falsification test',
                'counter_mechanism': 'allocating large exploration budgets to absurd hypotheses with high test costs and untestable predictions',
                'assumption_prerequisite': 'radical or absurd hypotheses can be objectively prioritized by expected information gain per unit testing cost',
                'app': 'high-risk'
            },
            'CLAIM-040': {
                'domain_entity': 'fountain',
                'target_variable': 'marginal evidence rank or settlement reward increases upon adding redundant copies of existing provenance atom',
                'computation': 'model one observation encoded into n redundant fragments; allow reconstruction to improve with fragment count while asserting constant provenance-weight 1',
                'units': 'rank',
                'comparison_operator': '>',
                'threshold_bound': '0',
                'counter_mechanism': 'multi-agent systems treating 100 mirrors of an identical report as 100 corroborating pieces of evidence',
                'assumption_prerequisite': 'data redundancy (retries, mirrors, erasure fragments) increases availability probability but adds zero marginal information',
                'app': 'anti-inflationary'
            },
            'CLAIM-041': {
                'domain_entity': 'brier',
                'target_variable': 'calibration score in ledger f contaminated by agent popularity in ledger u',
                'computation': 'create paired toy laws with identical text and outcomes but swap their declared u, or keep u fixed while replace calibrated forecasts with uncalibrated ones',
                'units': 'brier_score',
                'comparison_operator': '>=',
                'threshold_bound': '0.25',
                'counter_mechanism': 'using high value-preference popularity (u) to override empirical factual calibration (f)',
                'assumption_prerequisite': 'governance requires strict structural separation of factual forecasts (f), value preferences (u), and constitutional rules (r)',
                'app': 'epistemic'
            },
            'CLAIM-042': {
                'domain_entity': 'value',
                'target_variable': 'mathematical rank of evidence matrix increases after appending linearly dependent copies of existing observation vector',
                'computation': 'feed one provenance atom through n retries/fragments/agents and require evidence/value rank to stay 1 while availability rises',
                'units': 'matrix_rank',
                'comparison_operator': '>',
                'threshold_bound': 'rank(e)',
                'counter_mechanism': 'linear combinations or re-encodings of existing evidence atoms spanning higher dimensional rank',
                'assumption_prerequisite': 'storage availability multiplicity and epistemic rank form a cartesian product space',
                'app': 'linear-algebraic'
            },
            'CLAIM-043': {
                'domain_entity': 'static',
                'target_variable': 'policy claiming decomposition fails to achieve equivalent terminal utility within bound h',
                'computation': 'take a toy task with a fixed input and fixed deadline. compare (a) one-shot solution, (b) time-sliced solution with no new information and equal total compute',
                'units': 'utility',
                'comparison_operator': 'fails',
                'threshold_bound': 'equivalent terminal utility within bound h',
                'counter_mechanism': 'claiming successful problem decomposition while silently relaxing terminal acceptance criteria or extending deadlines indefinitely',
                'assumption_prerequisite': 'static problem complexity (representation size / search space) is orthogonal to temporal decomposability into independent sequential sub-problems',
                'app': 'hierarchical'
            },
            'CLAIM-044': {
                'domain_entity': 'redundancy',
                'target_variable': 'novelty credit minted for transport-level relay, packet replication, or fountain re-encoding without new independent data source',
                'computation': 'toy evidence dag: include duplicate atoms, linear recombinations, mirrors, and one genuinely new source',
                'units': 'credit',
                'comparison_operator': '>',
                'threshold_bound': '0',
                'counter_mechanism': 'paying scientific discovery bounties to mirror nodes that merely relay existing packets',
                'assumption_prerequisite': 'network resilience/delivery service can be compensated through transport fees without issuing new epistemic capital or scientific credit',
                'app': 'two-tier'
            },
            'CLAIM-045': {
                'domain_entity': 'source',
                'target_variable': 'value credited to target-relevant ledger without verifiable reduction in hypothesis uncertainty',
                'computation': 'toy dag with duplicates, one irrelevant independent source, an xor-synergy pair, and one directly informative source',
                'units': 'entropy',
                'comparison_operator': '>=',
                'threshold_bound': '0',
                'counter_mechanism': 'minting scientific value for independent source rank that has zero relevance to target hypothesis',
                'assumption_prerequisite': 'complete accounting of distributed scientific contributions requires three orthogonal ledgers: delivery durability, independent provenance rank, and target utility gain',
                'app': 'three-dimensional'
            }
        }

        REFUTATIONAL_MARKERS = [
            'fail', 'collapse', 'in-sample', 'overfit', 'gaming', 'unbounded', 'violation',
            'unauthorized', 'forgery', 'drift', 'divergence', 'leakage', 'invalid', 'bias',
            'drop', 'spurious', 'loss', 'degrade', 'disparity', 'outperform', 'distortion',
            'counter', 'flaw', 'rejection', 'accepting', 'accepts', 'accepted', 'stale', 'unearned',
            'escalation', 'chaotic', 'break', 'misdiagnosis', 'misclassif', 'blind', 'conflat',
            'without', 'unconstrained', 'unmetered', 'substitut', 'ignor', 'discard', 'arbitrary',
            'merely', 'overrid', 'non-independent', 'unpartition', 'unrestricted', 're-encod',
            'poison', 'unpushed', 'uncommitted', 'unsound', 'escape', 'lack', 'zero marginal',
            'no significant difference', 'pure noise', 'mutat', 'alter', 'residue', 'inability',
            'contract', 'trivial'
        ]

        claims_by_id = {c['claim_id']: c for c in self.claims}
        self.assertEqual(len(STRUCTURED_FIELD_FIXTURES), 45, "Structured fixtures must cover all 45 claims")

        for cid, fix in STRUCTURED_FIELD_FIXTURES.items():
            c = claims_by_id[cid]
            ev = c['exact_source_read_evidence'].lower()
            st = c['statement'].lower()
            ass = ' '.join(c['assumptions']).lower()
            cont = ' '.join(c['contradictions']).lower()
            tp = c['null_test']['test_procedure'].lower()
            rt = c['null_test']['rejection_threshold'].lower()
            app = ' '.join(c['applications']).lower()

            # 1. Statement and verbatim evidence must share direct domain grounding
            self.assertIn(fix['domain_entity'].lower(), ev, f"{cid} verbatim evidence missing domain anchor '{fix['domain_entity']}'")
            self.assertIn(fix['domain_entity'].lower(), st, f"{cid} statement missing domain anchor '{fix['domain_entity']}'")

            # 2. Assumptions must contain required domain concept and essential prerequisite
            self.assertIn(fix['assumption_prerequisite'].lower(), ass,
                          f"{cid} assumptions missing essential prerequisite '{fix['assumption_prerequisite']}'")

            # 3. Contradictions must contain concrete counter-mechanism AND explicit refutational marker
            self.assertIn(fix['counter_mechanism'].lower(), cont,
                          f"{cid} contradictions missing concrete counter-mechanism '{fix['counter_mechanism']}'")
            self.assertTrue(any(m in cont for m in REFUTATIONAL_MARKERS),
                            f"{cid} contradictions lack explicit refutational markers")

            # 4. Test procedure must contain operational computation step
            self.assertIn(fix['computation'].lower(), tp,
                          f"{cid} test_procedure missing operational computation '{fix['computation']}'")

            # 5. Rejection threshold must contain target_variable, exact comparison_operator, and quantitative bound
            self.assertIn(fix['target_variable'].lower(), rt,
                          f"{cid} rejection_threshold missing target_variable '{fix['target_variable']}'")
            self.assertIn(fix['comparison_operator'].lower(), rt,
                          f"{cid} rejection_threshold missing comparison operator '{fix['comparison_operator']}'")
            self.assertIn(fix['threshold_bound'].lower(), rt,
                          f"{cid} rejection_threshold missing quantitative threshold bound '{fix['threshold_bound']}'")

            # 6. Strict Procedure-Threshold Concordance:
            # Prove that the specific target_variable bounded in rejection_threshold is directly computed in test_procedure
            stop_words = {'between', 'from', 'with', 'that', 'this', 'have', 'more', 'over', 'than', 'only', 'under', 'into', 'upon', 'after', 'without'}
            var_tokens = [w for w in re.findall(r'[a-zA-Z]{4,}', fix['target_variable'].lower()) if w not in stop_words]
            tp_tokens = set(re.findall(r'[a-zA-Z]{4,}', tp))
            rt_tokens = set(re.findall(r'[a-zA-Z]{4,}', rt))
            shared_var_tokens = set(var_tokens).intersection(tp_tokens).intersection(rt_tokens)
            self.assertTrue(bool(shared_var_tokens),
                            f"{cid} strict procedure-threshold concordance failed for target variable '{fix['target_variable']}' (var_tokens: {var_tokens})")

            # 7. Applications must contain domain concept
            self.assertIn(fix['app'].lower(), app, f"{cid} applications missing domain concept '{fix['app']}'")

    def test_direct_object_read_exact_evidence(self):
        """Verify exact_source_read_evidence is an exact, verbatim character-by-character substring of GitHub direct object."""
        for c in self.claims:
            sid = str(c['source_id'])
            self.assertIn(sid, self.direct_objects, f"Source ID {sid} missing from direct objects cache")
            d_obj = self.direct_objects[sid]
            body = d_obj['body']
            ev = c['exact_source_read_evidence']
            self.assertIn(ev, body, f"Verbatim evidence mismatch in {c['claim_id']}: exact substring not found in comment {sid}")

    def test_direct_object_urls_and_ids(self):
        """Verify source URL, source ID, and SHA-256 match direct objects cache."""
        for c in self.claims:
            sid = str(c['source_id'])
            self.assertIn(sid, self.direct_objects)
            d_obj = self.direct_objects[sid]
            expected_url = f"https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-{sid}"
            self.assertEqual(c['source_url'], expected_url)
            computed_sha = hashlib.sha256(d_obj['body'].encode('utf-8')).hexdigest()
            self.assertEqual(c['source_sha256'], computed_sha)

    def test_canonical_duplicate_lineage(self):
        """Verify canonical deduplication, strict acyclicity of parent chains and forest, valid merge rules, and semantic lineage correctness."""
        claims_by_id = {c['claim_id']: c for c in self.claims}
        valid_lineage_types = {'CANONICAL_ORIGIN', 'SEMANTIC_DUPLICATE', 'REFINEMENT', 'EMPIRICAL_INSTANCE'}
        valid_canonical_ids = {'CANONICAL-01', 'CANONICAL-02', 'CANONICAL-03', 'CANONICAL-04', 'CANONICAL-05', 'CANONICAL-06'}

        # 1. Structural schema and parent chain walk with cycle detection (arbitrary cycle lengths)
        for c in self.claims:
            cid = c['claim_id']
            lineage = c['duplicate_lineage']
            canonical_id = lineage['canonical_invariant_id']
            self.assertIn(canonical_id, valid_canonical_ids)
            self.assertIn(lineage['lineage_type'], valid_lineage_types)
            self.assertTrue(len(lineage['merge_rule']) > 15, "Merge rule must be explicit and non-empty")

            # Traverse parent chain from c to root
            visited_in_path = []
            curr_id = cid
            while curr_id is not None:
                self.assertNotIn(curr_id, visited_in_path, f"Cycle detected in lineage chain starting from {cid}: {visited_in_path} -> {curr_id}")
                visited_in_path.append(curr_id)

                curr_claim = claims_by_id[curr_id]
                curr_lineage = curr_claim['duplicate_lineage']
                # Every ancestor in the chain must share the identical canonical invariant
                self.assertEqual(curr_lineage['canonical_invariant_id'], canonical_id,
                                 f"Canonical invariant mismatch in lineage chain: {curr_id} has {curr_lineage['canonical_invariant_id']}, expected {canonical_id}")

                parent_id = curr_lineage.get('parent_claim_id')
                if parent_id is None:
                    # Root of lineage must be CANONICAL_ORIGIN
                    self.assertEqual(curr_lineage['lineage_type'], 'CANONICAL_ORIGIN',
                                     f"Root {curr_id} in lineage of {cid} must have lineage_type CANONICAL_ORIGIN")
                    break
                else:
                    self.assertIn(parent_id, claims_by_id, f"Parent claim {parent_id} not found in claims")
                    curr_id = parent_id

        # 2. Formal Topological Sort (Kahn's Algorithm) over the entire parent lineage graph
        adj = defaultdict(list)
        in_degree = {cid: 0 for cid in claims_by_id}
        for cid, c in claims_by_id.items():
            parent = c['duplicate_lineage'].get('parent_claim_id')
            if parent:
                adj[cid].append(parent)
                in_degree[parent] += 1

        queue = deque([cid for cid, deg in in_degree.items() if deg == 0])
        sorted_count = 0
        while queue:
            node = queue.popleft()
            sorted_count += 1
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        self.assertEqual(sorted_count, len(claims_by_id), "Topological sort failed: directed cycle exists in lineage forest")

        # 3. Semantic Lineage Correctness (Resolving Defect MIN-18-QA-02)
        # CANONICAL-05 must strictly govern process-binding and dispatch boundary identity (CLAIM-003, CLAIM-009)
        c05_claims = {c['claim_id'] for c in self.claims if c['canonical_invariant_id'] == 'CANONICAL-05'}
        self.assertEqual(c05_claims, {'CLAIM-003', 'CLAIM-009'}, "CANONICAL-05 must only govern process and credential boundary identity")

        # CANONICAL-02 must govern genuine redundancy vs true value claims (CLAIM-040, CLAIM-042, CLAIM-044, CLAIM-045)
        c02_claims = {c['claim_id'] for c in self.claims if c['canonical_invariant_id'] == 'CANONICAL-02'}
        self.assertEqual(c02_claims, {'CLAIM-040', 'CLAIM-042', 'CLAIM-044', 'CLAIM-045'}, "CANONICAL-02 must govern redundancy vs true value claims")
        self.assertEqual(claims_by_id['CLAIM-040']['duplicate_lineage']['lineage_type'], 'CANONICAL_ORIGIN')

        # CANONICAL-01 must govern evidence capital, e-wealth, and ancestry algebra (CLAIM-004..026)
        c01_claims = {c['claim_id'] for c in self.claims if c['canonical_invariant_id'] == 'CANONICAL-01'}
        self.assertEqual(c01_claims, {'CLAIM-004', 'CLAIM-007', 'CLAIM-008', 'CLAIM-011', 'CLAIM-012', 'CLAIM-014', 'CLAIM-016', 'CLAIM-019', 'CLAIM-020', 'CLAIM-026'})

    def test_graph_relations_strictly_typed(self):
        """Verify that all graph relations are strictly typed and eliminate ambiguous relations."""
        allowed_relations = {'refines', 'generalizes', 'supports', 'contradicts', 'duplicates', 'maps_to_canonical'}
        self.assertTrue(len(self.graph['edges']) >= 45)
        for edge in self.graph['edges']:
            rel = edge['relation']
            self.assertIn(rel, allowed_relations, f"Disallowed relation '{rel}' found in edge")
            self.assertNotEqual(rel, 'refines_or_deduplicates', "Ambiguous relation 'refines_or_deduplicates' must not exist")

        # Exactly 45 claims must map to canonical invariants
        canonical_maps = [e for e in self.graph['edges'] if e['relation'] == 'maps_to_canonical']
        self.assertEqual(len(canonical_maps), 45)

    def test_cluster_counts_consistency(self):
        """Verify cluster counts are strictly 10 / 16 / 19 across all artifacts."""
        expected_counts = {'Cluster-1': 10, 'Cluster-2': 16, 'Cluster-3': 19}
        actual_counts = dict(Counter(c['cluster_id'] for c in self.claims))
        self.assertEqual(actual_counts, expected_counts)
        self.assertEqual(self.graph['graph_metadata']['cluster_counts'], expected_counts)

    def test_top_three_falsification_specs_and_reproducible_ranking(self):
        """Verify all 6 canonical invariants are evaluated objectively, score bands strictly match rubric definitions, and top 3 emerge reproducibly."""
        rubric = self.specs['metadata']['scoring_rubric']
        w = rubric['weights']
        all_evals = self.specs['all_canonical_evaluations']

        # 1. All 6 canonical invariants must be evaluated
        self.assertEqual(len(all_evals), 6, "All 6 canonical invariants must be evaluated")
        eval_ids = {e['canonical_invariant_id'] for e in all_evals}
        expected_ids = {'CANONICAL-01', 'CANONICAL-02', 'CANONICAL-03', 'CANONICAL-04', 'CANONICAL-05', 'CANONICAL-06'}
        self.assertEqual(eval_ids, expected_ids)

        # 2. Bidirectional Mutually Exclusive Rubric Compliance Verification (Resolving QA Rework Defects 1 & 2)
        for e in all_evals:
            cid = e['canonical_invariant_id']
            c = e['component_scores']
            bands = e['rubric_bands']
            justifications = e['component_justifications']

            for axis in ['C1_rigor_and_falsifiability', 'C2_anti_sybil_and_grounding', 'C3_cross_domain_generality', 'C4_test_cost_efficiency']:
                self.assertIn(axis, c)
                self.assertIn(axis, bands)
                self.assertIn(axis, justifications)
                score = c[axis]
                band_str = bands[axis]

                # Parse band min and max
                if '-' in band_str:
                    b_min, b_max = map(float, band_str.split('-'))
                    self.assertTrue(b_min <= score <= b_max, f"{cid} on {axis} score {score} outside declared band {band_str}")
                elif 'below' in band_str:
                    b_max = float(band_str.replace('below_', ''))
                    self.assertTrue(score < b_max, f"{cid} on {axis} score {score} not below {b_max}")

            # Bidirectional C1 (Rigor & Falsifiability)
            score_c1 = c['C1_rigor_and_falsifiability']
            band_c1 = bands['C1_rigor_and_falsifiability']
            j_c1 = justifications['C1_rigor_and_falsifiability'].lower()
            if 9.0 <= score_c1 <= 10.0:
                self.assertEqual(band_c1, "9.0-10.0")
                self.assertTrue(any(t in j_c1 for t in ['closed-form', 'e-process', 'martingale', 'rank']))
                self.assertFalse(any(t in j_c1 for t in ['qualitative structural partition', 'taxonomy lacking exact']))
            elif 7.5 <= score_c1 <= 8.9:
                self.assertEqual(band_c1, "7.5-8.9")
                self.assertTrue(any(t in j_c1 for t in ['semi-formal', 'operational', 'protocol', 'state-machine']))
                self.assertFalse(any(t in j_c1 for t in ['closed-form e-process', 'closed-form linear-algebraic']))
            elif 6.0 <= score_c1 <= 7.4:
                self.assertEqual(band_c1, "6.0-7.4")
                self.assertTrue(any(t in j_c1 for t in ['qualitative', 'taxonomy', 'structural partition', 'lacks exact']))
            # Converse C1
            if any(t in j_c1 for t in ['qualitative', 'taxonomy', 'lacks exact mathematical test statistic']):
                self.assertTrue(score_c1 <= 7.4 and band_c1 == "6.0-7.4",
                                f"{cid} C1 converse failure: qualitative taxonomy must receive band 6.0-7.4 and score <= 7.4, got {score_c1}")
            if any(t in j_c1 for t in ['closed-form e-process', 'closed-form linear-algebraic']):
                self.assertTrue(score_c1 >= 9.0 and band_c1 == "9.0-10.0",
                                f"{cid} C1 converse failure: closed-form proof must receive band 9.0-10.0, got {score_c1}")

            # Bidirectional C2 (Anti-Sybil & Grounding)
            score_c2 = c['C2_anti_sybil_and_grounding']
            band_c2 = bands['C2_anti_sybil_and_grounding']
            j_c2 = justifications['C2_anti_sybil_and_grounding'].lower()
            if 9.5 <= score_c2 <= 10.0:
                self.assertEqual(band_c2, "9.5-10.0")
                self.assertTrue(any(t in j_c2 for t in ['provable anti-sybil', 'simplex conservation', 'replication cloning']))
            elif 8.5 <= score_c2 <= 9.4:
                self.assertEqual(band_c2, "8.5-9.4")
                self.assertTrue(any(t in j_c2 for t in ['cryptographic', 'kernel', 'process tables', 'capability']))
            elif 7.0 <= score_c2 <= 8.4:
                self.assertEqual(band_c2, "7.0-8.4")
                self.assertTrue(any(t in j_c2 for t in ['heuristic', 'semantic', 'vulnerable']))
            # Converse C2
            if any(t in j_c2 for t in ['heuristic', 'vulnerable to high-dimensional', 'subjective redefinition']):
                self.assertTrue(score_c2 <= 8.4 and band_c2 == "7.0-8.4")
            if any(t in j_c2 for t in ['provable anti-sybil', 'mathematically provable anti-sybil']):
                self.assertTrue(score_c2 >= 9.5 and band_c2 == "9.5-10.0")

            # Bidirectional C3 (Cross-Domain Generality)
            score_c3 = c['C3_cross_domain_generality']
            band_c3 = bands['C3_cross_domain_generality']
            j_c3 = justifications['C3_cross_domain_generality'].lower()
            if 9.0 <= score_c3 <= 10.0:
                self.assertEqual(band_c3, "9.0-10.0")
                self.assertTrue(any(t in j_c3 for t in ['universal', 'multi-agent', 'scientific', 'settlement']))
            elif 8.0 <= score_c3 <= 8.9:
                self.assertEqual(band_c3, "8.0-8.9")
                self.assertTrue(any(t in j_c3 for t in ['broadly applicable', 'distributed execution', 'multi-host', 'specialized to runtime']))
            elif 7.0 <= score_c3 <= 7.9:
                self.assertEqual(band_c3, "7.0-7.9")
                self.assertTrue(any(t in j_c3 for t in ['domain-specific', 'limited transfer', 'prompt']))
            # Converse C3
            if any(t in j_c3 for t in ['domain-specific to prompt', 'domain-specific to task taxonomy']):
                self.assertTrue(score_c3 <= 7.9 and band_c3 == "7.0-7.9")
            if any(t in j_c3 for t in ['universal across multi-agent consensus']):
                self.assertTrue(score_c3 >= 9.0 and band_c3 == "9.0-10.0")

            # Bidirectional C4 (Test Cost Efficiency)
            score_c4 = c['C4_test_cost_efficiency']
            band_c4 = bands['C4_test_cost_efficiency']
            j_c4 = justifications['C4_test_cost_efficiency'].lower()
            if 9.5 <= score_c4 <= 10.0:
                self.assertEqual(band_c4, "9.5-10.0")
                self.assertTrue(any(t in j_c4 for t in ['< 3.5s', '< 2.0s', '< 1.5s', '< 1.0s', 'ultra-low-cost']))
            # Converse C4: Any test cheaper than 3.5s must be in 9.5-10.0
            if any(t in j_c4 for t in ['< 3.5s', '< 2.0s', '< 1.5s', '< 1.0s']):
                self.assertTrue(score_c4 >= 9.5 and band_c4 == "9.5-10.0",
                                f"{cid} C4 converse failure: test < 3.5s must receive band 9.5-10.0 and score >= 9.5, got {score_c4}")

        # 3. Dynamic Calculation and Sorting
        calculated_scores = []
        for e in all_evals:
            cid = e['canonical_invariant_id']
            c = e['component_scores']
            computed_s = (
                w['C1_rigor_and_falsifiability'] * c['C1_rigor_and_falsifiability'] +
                w['C2_anti_sybil_and_grounding'] * c['C2_anti_sybil_and_grounding'] +
                w['C3_cross_domain_generality'] * c['C3_cross_domain_generality'] +
                w['C4_test_cost_efficiency'] * c['C4_test_cost_efficiency']
            )
            self.assertAlmostEqual(e['composite_score'], computed_s, places=2)
            calculated_scores.append((computed_s, cid, e))

        calculated_scores.sort(key=lambda x: x[0], reverse=True)
        ranked_ids = [item[1] for item in calculated_scores]

        # Top 3 strictly match CANONICAL-01, CANONICAL-02, CANONICAL-05
        self.assertEqual(ranked_ids[0], 'CANONICAL-01')
        self.assertEqual(ranked_ids[1], 'CANONICAL-02')
        self.assertEqual(ranked_ids[2], 'CANONICAL-05')

        # Remaining ranks match CANONICAL-06, CANONICAL-03, CANONICAL-04
        self.assertEqual(ranked_ids[3], 'CANONICAL-06')
        self.assertEqual(ranked_ids[4], 'CANONICAL-03')
        self.assertEqual(ranked_ids[5], 'CANONICAL-04')

        # 4. Verify exactly 3 falsification specs correspond to the top 3 ranked invariants
        specs = self.specs['specs']
        self.assertEqual(len(specs), 3)
        expected_spec_anchors = {"CLAIM-011", "CLAIM-040", "CLAIM-003"}
        actual_spec_anchors = {s['anchor_claim_id'] for s in specs}
        self.assertEqual(actual_spec_anchors, expected_spec_anchors)

        for s in specs:
            self.assertIn("spec_id", s)
            self.assertIn("canonical_invariant_id", s)
            self.assertIn(s['canonical_invariant_id'], {'CANONICAL-01', 'CANONICAL-02', 'CANONICAL-05'})
            self.assertIn("null_hypothesis", s)
            self.assertIn("falsification_procedure", s)
            self.assertIn("pass_fail_criteria", s)
            self.assertIn("cheapest_test", s)

        # 5. Executable Bounded Decision Criteria Verification for FALSIF-SPEC-001 (Resolving QA Rework Defects 1, 2, 3)
        s1 = next(s for s in specs if s['spec_id'] == 'FALSIF-SPEC-001')
        self.assertIn("Doob's optional stopping theorem", s1['formulation'],
                      "FALSIF-SPEC-001 formulation must specify Doob's optional stopping theorem")
        self.assertIn("bounded horizon T_max", s1['formulation'],
                      "FALSIF-SPEC-001 formulation must specify supermartingale property on bounded horizon")
        self.assertIn("adapted stopping time", s1['formulation'].lower(),
                      "FALSIF-SPEC-001 formulation must restrict Doob's theorem to adapted stopping times")
        self.assertIn("Ville's maximal inequality", s1['formulation'],
                      "FALSIF-SPEC-001 formulation must govern running suprema via Ville's inequality")
        self.assertNotIn("argmax", s1['formulation'].lower(),
                      "FALSIF-SPEC-001 formulation must not treat non-adapted argmax as stopping time")

        null_hyp = s1['null_hypothesis']
        self.assertIn("T_max = 500", null_hyp)
        self.assertIn("m = 100", null_hyp)
        self.assertIn("simplex-partitioned weights", null_hyp,
                      "FALSIF-SPEC-001 null hypothesis must specify simplex-partitioned weights")

        proc_text = ' '.join(s1['falsification_procedure'])
        self.assertNotIn("argmax_{t <= 50}", proc_text,
                         "FALSIF-SPEC-001 procedure must not include non-adapted argmax peak in stopping time family")
        self.assertIn("SeedSequence(20261102)", proc_text, "FALSIF-SPEC-001 must declare deterministic seed policy")
        self.assertIn("T_max = 500", proc_text, "FALSIF-SPEC-001 procedure must specify bounded horizon T_max = 500")
        self.assertIn("N = 5,000", proc_text, "FALSIF-SPEC-001 procedure must specify finite sample trajectory N = 5,000")
        self.assertIn("adapted stopping time family", proc_text.lower(), "FALSIF-SPEC-001 procedure must specify adapted stopping time family T")
        self.assertIn("paired parallel trajectories", proc_text.lower(), "FALSIF-SPEC-001 procedure must execute paired control trajectories")
        self.assertIn("D^(j)_tau", proc_text, "FALSIF-SPEC-001 procedure must define paired difference metric D^(j)_tau")
        self.assertIn("UCB_0.999", proc_text, "FALSIF-SPEC-001 procedure must specify Studentized upper confidence bound UCB_0.999")
        self.assertIn("LCB_0.999", proc_text, "FALSIF-SPEC-001 procedure must specify Studentized lower confidence bound LCB_0.999")
        self.assertIn("alpha = 10^-3", proc_text, "FALSIF-SPEC-001 procedure must specify alpha = 10^-3")

        pass_text = s1['pass_fail_criteria']['pass_condition']
        fail_text = s1['pass_fail_criteria']['fail_condition']
        inconcl_text = s1['pass_fail_criteria']['inconclusive_condition']
        crit_dict = s1['pass_fail_criteria']

        # Verify Deterministic Priority Order & Mutually Exclusive Disjoint Partitions
        self.assertIn("deterministic priority", crit_dict['decision_framework'].lower())
        self.assertIn("Priority 1: FAIL", crit_dict['deterministic_priority_order'])
        self.assertIn("Priority 2: PASS", crit_dict['deterministic_priority_order'])
        self.assertIn("Priority 3: INCONCLUSIVE", crit_dict['deterministic_priority_order'])

        # Verify Group-Sequential Family-Wise Error Rate (FWER) Bonferroni Correction & Multiplicity Family M = 57
        self.assertIn("Bonferroni", crit_dict['statistical_guarantee_scope'])
        self.assertIn("pointwise", crit_dict['statistical_guarantee_scope'].lower())
        self.assertEqual(crit_dict['parameters']['stopping_family_size_K'], 9)
        self.assertEqual(crit_dict['parameters']['endpoints_per_look'], 19)
        self.assertEqual(crit_dict['parameters']['max_sequential_looks'], 3)
        self.assertEqual(crit_dict['parameters']['multiplicity_family_size_M'], 57)
        self.assertEqual(crit_dict['parameters']['fwer_alpha'], 0.001)
        self.assertAlmostEqual(crit_dict['parameters']['alpha_adjusted_bonferroni'], 0.001 / 57, places=7)
        self.assertEqual(crit_dict['parameters']['critical_value_t_fwer_bonferroni'], 4.294)
        self.assertEqual(crit_dict['parameters']['critical_value_t_pointwise'], 3.090)
        self.assertEqual(crit_dict['parameters']['ville_threshold_p_hat_max'], 0.0632)

        # Verify Mutually Exclusive Pass & Fail Partitions under Operative FWER Bounds
        self.assertIn("LCB_FWER(E[E*_tau]) <= 1.0", pass_text, "Pass condition must require LCB_FWER <= 1.0 to eliminate overlap with Fail")
        self.assertIn("LCB_FWER(E[Delta E*_tau]) <= 0.0", pass_text, "Pass condition must require LCB_FWER(Delta) <= 0.0 to eliminate overlap with Fail")
        self.assertIn("P_hat_LCB_FWER", pass_text, "Pass condition must evaluate tail LCB <= 0.05 to eliminate overlap with Fail")
        self.assertIn("epsilon_tol", pass_text, "Pass condition must evaluate tolerance budget epsilon_tol")
        self.assertIn("<= 1.0 + epsilon_tol", pass_text, "Pass condition must bound portfolio wealth UCB <= 1.0 + epsilon_tol")
        self.assertIn("SE_max = 0.015", pass_text, "Pass condition must enforce maximum standard error constraint")
        self.assertIn("1e-12", pass_text, "Pass condition must verify machine-precision Sybil neutrality")
        self.assertIn("0.0632", pass_text, "Pass condition must verify FWER-adjusted maximal tail threshold 0.0632")
        self.assertIn("LCB_FWER", fail_text, "Fail condition must declare unambiguous rejection via lower confidence bound")
        self.assertIn("> 1.0", fail_text, "Fail condition must trigger when LCB_FWER > 1.0")
        self.assertIn("Delta E*", fail_text, "Fail condition must evaluate paired Sybil excess Delta E*")
        self.assertIn("4.294", fail_text, "Fail condition must compute operative boundaries with t_FWER = 4.294")
        self.assertIn("retry_budget", str(crit_dict['parameters']), "Parameters must define retry budget")
        self.assertIn("B_max = 2 extensions", inconcl_text, "Inconclusive rule must specify finite retry budget B_max = 2")
        self.assertIn("INCONCLUSIVE_RETRY_BUDGET_EXHAUSTED", inconcl_text, "Inconclusive rule must define definitive termination status")
        self.assertIn("< 3.5 seconds", s1['cheapest_test'], "Cheapest test must be verifiable in < 3.5 seconds on CPU")

        # Programmatic Single-Look Ternary Classifier: constructs decision boundaries directly from estimates & SEs
        def evaluate_ternary_look(portfolio_mean, portfolio_se,
                                  sybil_mean, sybil_se,
                                  tail_p_hat, n_samples=5000,
                                  t_crit=4.294,
                                  epsilon_tol=0.02, se_max=0.015):
            portfolio_lcb = portfolio_mean - t_crit * portfolio_se
            portfolio_ucb = portfolio_mean + t_crit * portfolio_se
            sybil_lcb = sybil_mean - t_crit * sybil_se
            sybil_ucb = sybil_mean + t_crit * sybil_se

            tail_se = math.sqrt(tail_p_hat * (1.0 - tail_p_hat) / n_samples)
            tail_lcb = tail_p_hat - t_crit * tail_se
            tail_null_se = math.sqrt(0.05 * 0.95 / n_samples)
            tail_pass_threshold = 0.05 + t_crit * tail_null_se

            # Priority 1: FAIL check (triggers if ANY lower confidence bound exceeds null threshold)
            if portfolio_lcb > 1.0 or sybil_lcb > 0.0 or tail_lcb > 0.05:
                return "FAIL", {
                    "portfolio_lcb": portfolio_lcb, "portfolio_ucb": portfolio_ucb,
                    "sybil_lcb": sybil_lcb, "sybil_ucb": sybil_ucb,
                    "tail_lcb": tail_lcb, "tail_pass_threshold": tail_pass_threshold,
                    "n_samples": n_samples
                }
            # Priority 2: PASS check (requires ALL bounds within null threshold + tolerance)
            if (portfolio_lcb <= 1.0 and portfolio_ucb <= 1.0 + epsilon_tol and portfolio_se <= se_max and
                sybil_lcb <= 0.0 and sybil_ucb <= epsilon_tol and sybil_se <= se_max and
                tail_lcb <= 0.05 and tail_p_hat <= tail_pass_threshold):
                return "PASS", {
                    "portfolio_lcb": portfolio_lcb, "portfolio_ucb": portfolio_ucb,
                    "sybil_lcb": sybil_lcb, "sybil_ucb": sybil_ucb,
                    "tail_lcb": tail_lcb, "tail_pass_threshold": tail_pass_threshold,
                    "n_samples": n_samples
                }
            # Priority 3: INCONCLUSIVE check
            return "INCONCLUSIVE", {
                "portfolio_lcb": portfolio_lcb, "portfolio_ucb": portfolio_ucb,
                "sybil_lcb": sybil_lcb, "sybil_ucb": sybil_ucb,
                "tail_lcb": tail_lcb, "tail_pass_threshold": tail_pass_threshold,
                "n_samples": n_samples
            }

        # Programmatic Full Group-Sequential Retry Classifier: executes the full cycle initial look -> retry 1 -> retry 2
        def evaluate_sequential_retry_classifier(stages_data, t_crit=4.294,
                                                 epsilon_tol=0.02, se_max=0.015,
                                                 max_extensions=2):
            history = []
            max_looks = 1 + max_extensions
            for k, data in enumerate(stages_data, start=1):
                if k > max_looks:
                    break
                n_samples = data.get('n_samples', 5000 * (2 ** (k - 1)))
                verdict, details = evaluate_ternary_look(
                    portfolio_mean=data['portfolio_mean'],
                    portfolio_se=data['portfolio_se'],
                    sybil_mean=data['sybil_mean'],
                    sybil_se=data['sybil_se'],
                    tail_p_hat=data['tail_p_hat'],
                    n_samples=n_samples,
                    t_crit=t_crit,
                    epsilon_tol=epsilon_tol,
                    se_max=se_max
                )
                history.append({"stage": k, "n_samples": n_samples, "verdict": verdict, "details": details})
                if verdict in ("FAIL", "PASS"):
                    return verdict, k, history
            return "INCONCLUSIVE_RETRY_BUDGET_EXHAUSTED", len(history), history

        # Backward compatibility alias
        def evaluate_ternary_classifier(portfolio_mean, portfolio_se,
                                        sybil_mean, sybil_se,
                                        tail_p_hat, n_samples=5000,
                                        t_crit=4.294,
                                        epsilon_tol=0.02, se_max=0.015):
            verdict, _ = evaluate_ternary_look(portfolio_mean, portfolio_se,
                                               sybil_mean, sybil_se,
                                               tail_p_hat, n_samples,
                                               t_crit, epsilon_tol, se_max)
            return verdict

        # Counterexample 1: Portfolio wealth estimate where LCB_FWER > 1.0 (mean=1.025, SE=0.005 -> LCB = 1.0035 > 1.0)
        # Must evaluate unambiguously to FAIL, never PASS
        res_ce1 = evaluate_ternary_classifier(portfolio_mean=1.025, portfolio_se=0.005,
                                              sybil_mean=0.0, sybil_se=0.001,
                                              tail_p_hat=0.048)
        self.assertEqual(res_ce1, "FAIL", "Portfolio wealth with LCB_FWER > 1.0 must classify as FAIL")

        # Counterexample 2: Sybil excess estimate where LCB_FWER > 0.0 (mean=0.012, SE=0.002 -> LCB = 0.00341 > 0.0)
        # Must evaluate unambiguously to FAIL, never PASS
        res_ce2 = evaluate_ternary_classifier(portfolio_mean=0.995, portfolio_se=0.003,
                                              sybil_mean=0.012, sybil_se=0.002,
                                              tail_p_hat=0.048)
        self.assertEqual(res_ce2, "FAIL", "Sybil excess with LCB_FWER > 0.0 must classify as FAIL")

        # Counterexample 3: Maximal tail with P_hat_LCB_FWER > 0.05 (P_hat=0.068 -> LCB = 0.0527 > 0.05)
        # Must evaluate unambiguously to FAIL, never PASS
        res_ce3 = evaluate_ternary_classifier(portfolio_mean=0.995, portfolio_se=0.003,
                                              sybil_mean=0.0, sybil_se=0.001,
                                              tail_p_hat=0.068)
        self.assertEqual(res_ce3, "FAIL", "Maximal tail with P_hat_LCB_FWER > 0.05 must classify as FAIL")

        # Compliant Single-Look Run: LCB <= 1.0, UCB <= 1.02, LCB(Delta) <= 0, UCB(Delta) <= 0.02, tail compliant
        res_pass = evaluate_ternary_classifier(portfolio_mean=1.000, portfolio_se=0.003,
                                               sybil_mean=0.0, sybil_se=0.001,
                                               tail_p_hat=0.048)
        self.assertEqual(res_pass, "PASS", "Compliant supermartingale run must classify as PASS")

        # Sampling Gap: LCB <= 1.0, but UCB_FWER > 1.02 (mean=1.000, SE=0.008 -> UCB = 1.0344 > 1.02)
        res_inconcl = evaluate_ternary_classifier(portfolio_mean=1.000, portfolio_se=0.008,
                                                  sybil_mean=0.0, sybil_se=0.001,
                                                  tail_p_hat=0.048)
        self.assertEqual(res_inconcl, "INCONCLUSIVE", "Wide confidence interval spanning threshold must classify as INCONCLUSIVE")

        # Full Sequential Cycle Tests:
        # 1. Full Sequential PASS at Stage 1 (Initial Look, N=5000)
        seq_pass1_verdict, seq_pass1_stage, seq_pass1_hist = evaluate_sequential_retry_classifier([
            {"portfolio_mean": 1.000, "portfolio_se": 0.003, "sybil_mean": 0.0, "sybil_se": 0.001, "tail_p_hat": 0.048, "n_samples": 5000}
        ])
        self.assertEqual(seq_pass1_verdict, "PASS")
        self.assertEqual(seq_pass1_stage, 1)

        # 2. Full Sequential FAIL at Stage 1 (Definitive failure stops immediately without retry)
        seq_fail1_verdict, seq_fail1_stage, seq_fail1_hist = evaluate_sequential_retry_classifier([
            {"portfolio_mean": 1.025, "portfolio_se": 0.005, "sybil_mean": 0.0, "sybil_se": 0.001, "tail_p_hat": 0.048, "n_samples": 5000}
        ])
        self.assertEqual(seq_fail1_verdict, "FAIL")
        self.assertEqual(seq_fail1_stage, 1)

        # 3. Full Sequential Cycle: Initial Look (INCONCLUSIVE) -> Retry 1 (PASS at Stage 2, N=10000)
        # Look 1: SE=0.0055 -> UCB = 1.000 + 4.294 * 0.0055 = 1.0236 > 1.020 (INCONCLUSIVE)
        # Look 2: N=10000, SE = 0.0055 / sqrt(2) = 0.003889 -> UCB = 1.000 + 4.294 * 0.003889 = 1.0167 <= 1.020 (PASS)
        seq_retry1_verdict, seq_retry1_stage, seq_retry1_hist = evaluate_sequential_retry_classifier([
            {"portfolio_mean": 1.000, "portfolio_se": 0.0055, "sybil_mean": 0.0, "sybil_se": 0.001, "tail_p_hat": 0.048, "n_samples": 5000},
            {"portfolio_mean": 1.000, "portfolio_se": 0.0055 / math.sqrt(2), "sybil_mean": 0.0, "sybil_se": 0.001 / math.sqrt(2), "tail_p_hat": 0.048, "n_samples": 10000}
        ])
        self.assertEqual(seq_retry1_verdict, "PASS")
        self.assertEqual(seq_retry1_stage, 2)
        self.assertEqual(seq_retry1_hist[0]['verdict'], "INCONCLUSIVE")
        self.assertEqual(seq_retry1_hist[1]['verdict'], "PASS")

        # 4. Full Sequential Cycle: Initial Look -> Retry 1 -> PASS at Retry 2 (Stage 3, N=20000)
        # Look 1: SE=0.0075 -> UCB = 1.0322 > 1.020 (INCONCLUSIVE)
        # Look 2: SE=0.0075 / sqrt(2) = 0.005303 -> UCB = 1.0227 > 1.020 (INCONCLUSIVE)
        # Look 3: SE=0.0075 / 2 = 0.00375 -> UCB = 1.0161 <= 1.020 (PASS)
        seq_retry2_verdict, seq_retry2_stage, seq_retry2_hist = evaluate_sequential_retry_classifier([
            {"portfolio_mean": 1.000, "portfolio_se": 0.0075, "sybil_mean": 0.0, "sybil_se": 0.001, "tail_p_hat": 0.048, "n_samples": 5000},
            {"portfolio_mean": 1.000, "portfolio_se": 0.0075 / math.sqrt(2), "sybil_mean": 0.0, "sybil_se": 0.001 / math.sqrt(2), "tail_p_hat": 0.048, "n_samples": 10000},
            {"portfolio_mean": 1.000, "portfolio_se": 0.0075 / 2.0, "sybil_mean": 0.0, "sybil_se": 0.001 / 2.0, "tail_p_hat": 0.048, "n_samples": 20000}
        ])
        self.assertEqual(seq_retry2_verdict, "PASS")
        self.assertEqual(seq_retry2_stage, 3)
        self.assertEqual(seq_retry2_hist[0]['verdict'], "INCONCLUSIVE")
        self.assertEqual(seq_retry2_hist[1]['verdict'], "INCONCLUSIVE")
        self.assertEqual(seq_retry2_hist[2]['verdict'], "PASS")

        # 5. Full Sequential Cycle: Initial Look -> Retry 1 -> Retry 2 -> Exhaustion (INCONCLUSIVE_RETRY_BUDGET_EXHAUSTED)
        seq_exhaust_verdict, seq_exhaust_stage, seq_exhaust_hist = evaluate_sequential_retry_classifier([
            {"portfolio_mean": 1.015, "portfolio_se": 0.016, "sybil_mean": 0.0, "sybil_se": 0.001, "tail_p_hat": 0.048, "n_samples": 5000},
            {"portfolio_mean": 1.015, "portfolio_se": 0.016 / math.sqrt(2), "sybil_mean": 0.0, "sybil_se": 0.001 / math.sqrt(2), "tail_p_hat": 0.048, "n_samples": 10000},
            {"portfolio_mean": 1.015, "portfolio_se": 0.008, "sybil_mean": 0.0, "sybil_se": 0.001 / 2.0, "tail_p_hat": 0.048, "n_samples": 20000}
        ])
        self.assertEqual(seq_exhaust_verdict, "INCONCLUSIVE_RETRY_BUDGET_EXHAUSTED")
        self.assertEqual(seq_exhaust_stage, 3)
        self.assertEqual(len(seq_exhaust_hist), 3)

        # 6. Full Sequential Cycle: Initial Look (INCONCLUSIVE) -> Retry 1 uncovers violation (FAIL at Stage 2)
        # Look 1: mean=1.015, SE=0.004 -> LCB = 1.015 - 4.294 * 0.004 = 0.9978 <= 1.0 (INCONCLUSIVE)
        # Look 2: N=10000, SE = 0.004 / sqrt(2) = 0.002828 -> LCB = 1.015 - 4.294 * 0.002828 = 1.00286 > 1.0 (FAIL)
        seq_fail2_verdict, seq_fail2_stage, seq_fail2_hist = evaluate_sequential_retry_classifier([
            {"portfolio_mean": 1.015, "portfolio_se": 0.004, "sybil_mean": 0.0, "sybil_se": 0.001, "tail_p_hat": 0.048, "n_samples": 5000},
            {"portfolio_mean": 1.015, "portfolio_se": 0.004 / math.sqrt(2), "sybil_mean": 0.0, "sybil_se": 0.001 / math.sqrt(2), "tail_p_hat": 0.048, "n_samples": 10000}
        ])
        self.assertEqual(seq_fail2_verdict, "FAIL")
        self.assertEqual(seq_fail2_stage, 2)
        self.assertEqual(seq_fail2_hist[0]['verdict'], "INCONCLUSIVE")
        self.assertEqual(seq_fail2_hist[1]['verdict'], "FAIL")

        # 7. Active Group-Sequential FWER Critical Value Sensitivity Test:
        # With mean=1.000, SE=0.0048 at Look 1:
        # Under single-look t=4.044: UCB = 1.000 + 4.044 * 0.0048 = 1.01941 <= 1.020 (erroneous PASS without sequential adjustment)
        # Under group-sequential Bonferroni FWER t=4.294 (M=57): UCB = 1.000 + 4.294 * 0.0048 = 1.02061 > 1.020 (INCONCLUSIVE)
        # Proves programmatically that t_FWER = 4.294 actively prevents premature acceptance during sequential looks
        res_single_look_pass = evaluate_ternary_classifier(portfolio_mean=1.000, portfolio_se=0.0048,
                                                           sybil_mean=0.0, sybil_se=0.001,
                                                           tail_p_hat=0.048, t_crit=4.044)
        res_seq_fwer_inconcl = evaluate_ternary_classifier(portfolio_mean=1.000, portfolio_se=0.0048,
                                                           sybil_mean=0.0, sybil_se=0.001,
                                                           tail_p_hat=0.048, t_crit=4.294)
        self.assertEqual(res_single_look_pass, "PASS", "Single-look bound would accept marginally wide interval prematurely")
        self.assertEqual(res_seq_fwer_inconcl, "INCONCLUSIVE", "Operative group-sequential FWER bound must classify marginally wide interval as INCONCLUSIVE")

    def test_excluded_data_documented_and_verified(self):
        """Verify excluded data contains at least 20 records and all match direct objects."""
        records = self.excluded['records']
        self.assertTrue(len(records) >= 20)
        for r in records:
            sid = str(r['source_id'])
            self.assertIn(sid, self.direct_objects)
            self.assertEqual(r['epistemic_classification'], "EXCLUDED_NOOP")
            self.assertTrue(len(r['exclusion_reason']) > 10)

if __name__ == '__main__':
    unittest.main()
