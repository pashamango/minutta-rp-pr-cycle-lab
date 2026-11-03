#!/usr/bin/env python3
import unittest
import json
import os
import hashlib
import re
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

        # 4. Field-Specific Fixture Concordance: rigorous verification of domain relevance,
        # verbatim evidence grounding, counter-mechanisms, measurable procedure variables, and threshold concordance.
        FIELD_SPECIFIC_FIXTURES = {
            'CLAIM-001': {'ev_st': 'φ', 'ass': 'simplex', 'cont': 'in-sample', 'tp': 'normalize', 'rt': 'held-out', 'app': 'triadic'},
            'CLAIM-002': {'ev_st': 'adaptive', 'ass': 'variants', 'cont': 'architectures', 'tp': 'selection', 'rt': 'statistically', 'app': 'evidence-contract'},
            'CLAIM-003': {'ev_st': 'status', 'ass': 'exposes', 'cont': 'transport', 'tp': 'synthetic', 'rt': 'discordance', 'app': 'cross-host'},
            'CLAIM-004': {'ev_st': 'search', 'ass': 'evidence', 'cont': 'parallel', 'tp': 'scheduler', 'rt': 'expected', 'app': 'conserved'},
            'CLAIM-005': {'ev_st': 'ordered', 'ass': 'cognitive', 'cont': 'reversed', 'tp': 'pre-register', 'rt': 'forward', 'app': 'phase-ordered'},
            'CLAIM-006': {'ev_st': '1:φ:φ²', 'ass': 'capacity', 'cont': 'measured', 'tp': 'ablation', 'rt': 'confidence', 'app': 'ablation'},
            'CLAIM-007': {'ev_st': 'valid', 'ass': 'log-transformed', 'cont': 'selective', 'tp': 'evaluate', 'rt': 'positive', 'app': 'additive'},
            'CLAIM-008': {'ev_st': 'evidence', 'ass': 'evidence', 'cont': 'conflating', 'tp': 'simulate', 'rt': 'growth', 'app': 'information-theoretic'},
            'CLAIM-009': {'ev_st': 'organizational', 'ass': 'identity', 'cont': 'exchanging', 'tp': 'validate', 'rt': 'privilege', 'app': 'three-identity'},
            'CLAIM-010': {'ev_st': 'weights', 'ass': 'resource', 'cont': 'applying', 'tp': 'conversion', 'rt': 'dimensional', 'app': 'distribution'},
            'CLAIM-011': {'ev_st': 'richest', 'ass': 'ensemble', 'cont': 'dynamically', 'tp': 'evidence', 'rt': 'portfolio', 'app': 'admissible'},
            'CLAIM-012': {'ev_st': 'weight', 'ass': 'hypothesis', 'cont': 'hypothesis', 'tp': 'pure-noise', 'rt': 'active', 'app': 'tree-structured'},
            'CLAIM-013': {'ev_st': 'ratio', 'ass': 'evaluation', 'cont': 'attempting', 'tp': 'proposed', 'rt': 'non-invariance', 'app': 'measurement'},
            'CLAIM-014': {'ev_st': 'mixture', 'ass': 'evidence', 'cont': 'spawning', 'tp': 'simulate', 'rt': 'branch', 'app': 'subagent'},
            'CLAIM-015': {'ev_st': 'report', 'ass': 'subject', 'cont': 'consuming', 'tp': 'existing', 'rt': 'unsigned', 'app': 'zero-trust'},
            'CLAIM-016': {'ev_st': 'valid', 'ass': 'evidence', 'cont': 'evidence', 'tp': 'duplicated', 'rt': 'presence', 'app': 'git-like'},
            'CLAIM-017': {'ev_st': 'report', 'ass': 'content-addressable', 'cont': 'claiming', 'tp': 'publish', 'rt': 'transition', 'app': 'handoff'},
            'CLAIM-018': {'ev_st': 'conserved', 'ass': 'empirical', 'cont': 're-submitting', 'tp': 'synthetic', 'rt': 're-use', 'app': 'systems'},
            'CLAIM-019': {'ev_st': 'provenance', 'ass': 'lineage', 'cont': 'assigning', 'tp': 'synthetic', 'rt': 'linear', 'app': 'provenance-strength'},
            'CLAIM-020': {'ev_st': 'provenance', 'ass': 'auditing', 'cont': 'operations', 'tp': 'synthetic', 'rt': 'non-zero', 'app': 'zero-side-effect'},
            'CLAIM-021': {'ev_st': 'evidence', 'ass': 'empirical', 'cont': 'treating', 'tp': 'evidence', 'rt': 'multi-use', 'app': 'resource'},
            'CLAIM-022': {'ev_st': 'consumer', 'ass': 'cryptographic', 'cont': 'verifying', 'tp': 'executor', 'rt': 'acceptance', 'app': 'two-coordinate'},
            'CLAIM-023': {'ev_st': 'golden', 'ass': 'multi-agent', 'cont': 'ensembles', 'tp': 'generate', 'rt': 'coordination', 'app': 'multi-agent'},
            'CLAIM-024': {'ev_st': 'golden', 'ass': 'combinations', 'cont': 'aggregated', 'tp': 'construct', 'rt': 'variation', 'app': 'decentralized'},
            'CLAIM-025': {'ev_st': 'golden', 'ass': 'characterizing', 'cont': 'claiming', 'tp': 'synthetic', 'rt': 'misclassification', 'app': 'two-parameter'},
            'CLAIM-026': {'ev_st': 'provenance', 'ass': 'combining', 'cont': 'multiplying', 'tp': 'synthetic', 'rt': 'empirical', 'app': 'dependence-aware'},
            'CLAIM-027': {'ev_st': 'evidence', 'ass': 'security', 'cont': 'delegated', 'tp': 'four-cell', 'rt': 'capability', 'app': 'object-capability'},
            'CLAIM-028': {'ev_st': 'evidence', 'ass': 'capability', 'cont': 'intersection', 'tp': 'settlement', 'rt': 'intersection', 'app': 'capability'},
            'CLAIM-029': {'ev_st': 'authority', 'ass': 'downstream', 'cont': 'derived', 'tp': 'paper/spec-only', 'rt': 'confidence', 'app': 'epistemic'},
            'CLAIM-030': {'ev_st': 'authorization', 'ass': 'multi-dimensional', 'cont': 'mutation', 'tp': 'caveats', 'rt': 'join/meet', 'app': 'algebraic'},
            'CLAIM-031': {'ev_st': 'crdt', 'ass': 'cross-host', 'cont': 'discarding', 'tp': 'paper/spec', 'rt': 'remote', 'app': 'cross-host'},
            'CLAIM-032': {'ev_st': 'averaging', 'ass': 'emergence', 'cont': 'simulated', 'tp': 'initial', 'rt': 'kolmogorov-smirnov', 'app': 'dynamical'},
            'CLAIM-033': {'ev_st': 'monotone', 'ass': 'mailbox', 'cont': 'out-of-order', 'tp': 'paper/spec-only', 'rt': 'rollback', 'app': 'decentralized'},
            'CLAIM-034': {'ev_st': 'recurrence', 'ass': 'iterative', 'cont': 'resource', 'tp': 'positive', 'rt': 'spectral', 'app': 'dynamical'},
            'CLAIM-035': {'ev_st': 'monotone', 'ass': 'distributed', 'cont': 'superseded', 'tp': 'spec-only', 'rt': 'superseded', 'app': 'decentralized'},
            'CLAIM-036': {'ev_st': 'causal', 'ass': 'mechanism', 'cont': 'substituting', 'tp': 'claim-units', 'rt': 'mutual', 'app': 'goal-directed'},
            'CLAIM-037': {'ev_st': 'task', 'ass': 'complexity', 'cont': 'difficulty', 'tp': 'matched', 'rt': 'ranking', 'app': 'prioritization'},
            'CLAIM-038': {'ev_st': 'bc-ur', 'ass': 'air-gapped', 'cont': 'sequential', 'tp': 'existing', 'rt': 'decoding', 'app': 'air-gapped'},
            'CLAIM-039': {'ev_st': 'observer-relative', 'ass': 'radical', 'cont': 'allocating', 'tp': 'blinded', 'rt': 'priority', 'app': 'high-risk'},
            'CLAIM-040': {'ev_st': 'fountain', 'ass': 'redundancy', 'cont': 'multi-agent', 'tp': 'observation', 'rt': 'marginal', 'app': 'anti-inflationary'},
            'CLAIM-041': {'ev_st': 'brier', 'ass': 'governance', 'cont': 'value-preference', 'tp': 'identical', 'rt': 'calibration', 'app': 'epistemic'},
            'CLAIM-042': {'ev_st': 'value', 'ass': 'storage', 'cont': 'combinations', 'tp': 'provenance', 'rt': 'mathematical', 'app': 'linear-algebraic'},
            'CLAIM-043': {'ev_st': 'static', 'ass': 'problem', 'cont': 'claiming', 'tp': 'deadline', 'rt': 'policy', 'app': 'hierarchical'},
            'CLAIM-044': {'ev_st': 'redundancy', 'ass': 'network', 'cont': 'scientific', 'tp': 'evidence', 'rt': 'novelty', 'app': 'two-tier'},
            'CLAIM-045': {'ev_st': 'source', 'ass': 'complete', 'cont': 'minting', 'tp': 'duplicates', 'rt': 'credited', 'app': 'three-dimensional'},
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

        PROCEDURE_METRICS = [
            't-test', 'p-value', 'percentile', 'monte carlo', 'rank', 'norm', 'exit', 'hash', 'signal',
            'weight', 'e-value', 'brier', 'trace', 'depth', 'metric', 'divergence', 'error', 'mean',
            'difference', 'ratio', 'drift', 'score', 'rate', 'delta', 'bound', 'threshold', 'spectral',
            'dimension', 'entropy', 'cost', 'count', 'budget', 'evidence', 'distribution', 'sample',
            'variance', 'covariance', 'permutation', 'simulation', 'frequency', 'probability', 'bits',
            'capacity', 'loss', 'step', 'interval', 'schema', 'matrix', 'predicate', 'resolution',
            'parsing', 'aci', 'partial order', 'terminal', 'outcome', 'reject', 'authority', 'cell',
            'sweep', 'dag', 'tree', 'measure', 'ablation', 'held-out', 'kraft', 'null'
        ]

        THRESHOLD_BOUNDS = [
            '<', '>', '=', '>=', '<=', '!=', 'p <', 'p >=', 'delta', 'drift', 'rank', 'percentile',
            'discordance', 'growth', 'accepted', 'fails', 'exceeds', 'outside', 'bound', 'zero',
            'inconsistency', 'rate', 'divergence', 'drop', 'elevation', 'widening', 'decay',
            'not subset', 'covers zero', 'includes zero', 'violating', 'accepted', 'positive'
        ]

        claims_by_id = {c['claim_id']: c for c in self.claims}
        for cid, fix in FIELD_SPECIFIC_FIXTURES.items():
            c = claims_by_id[cid]
            ev = c['exact_source_read_evidence'].lower()
            st = c['statement'].lower()
            ass = ' '.join(c['assumptions']).lower()
            cont = ' '.join(c['contradictions']).lower()
            tp = c['null_test']['test_procedure'].lower()
            rt = c['null_test']['rejection_threshold'].lower()
            app = ' '.join(c['applications']).lower()

            # 1. Statement and verbatim evidence must share direct domain grounding
            self.assertIn(fix['ev_st'], ev, f"{cid} verbatim evidence missing domain anchor '{fix['ev_st']}'")
            self.assertIn(fix['ev_st'], st, f"{cid} statement missing domain anchor '{fix['ev_st']}'")

            # 2. Assumptions must contain required domain concept
            self.assertIn(fix['ass'], ass, f"{cid} assumptions missing required domain concept '{fix['ass']}'")

            # 3. Contradictions must contain required concept AND explicit refutational marker
            self.assertIn(fix['cont'], cont, f"{cid} contradictions missing domain counter-mechanism '{fix['cont']}'")
            self.assertTrue(any(m in cont for m in REFUTATIONAL_MARKERS),
                            f"{cid} contradictions lack explicit refutational markers")

            # 4. Test procedure must contain required concept AND declare measurable metrics/variables
            self.assertIn(fix['tp'], tp, f"{cid} test_procedure missing operational step '{fix['tp']}'")
            self.assertTrue(any(m in tp for m in PROCEDURE_METRICS),
                            f"{cid} test_procedure lacks measurable operational metrics")

            # 5. Rejection threshold must contain required concept AND quantitative decision bounds
            self.assertIn(fix['rt'], rt, f"{cid} rejection_threshold missing decision concept '{fix['rt']}'")
            self.assertTrue(any(b in rt for b in THRESHOLD_BOUNDS),
                            f"{cid} rejection_threshold lacks quantitative decision bounds")

            # 6. Procedure-Threshold Concordance: variables tested in procedure must correspond to threshold tokens
            rt_tokens = set(re.findall(r'[a-zA-Z]{4,}', rt)) - {'from', 'with', 'that', 'this', 'have', 'more', 'over', 'than', 'only', 'under', 'between'}
            tp_tokens = set(re.findall(r'[a-zA-Z]{4,}', tp))
            self.assertTrue(bool(rt_tokens.intersection(tp_tokens)),
                            f"{cid} procedure-threshold concordance failed: no shared variable between procedure and threshold")

            # 7. Applications must contain domain concept
            self.assertIn(fix['app'], app, f"{cid} applications missing domain concept '{fix['app']}'")

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

        # 5. Executable Bounded Decision Criteria Verification for FALSIF-SPEC-001 (Resolving QA Rework Defect 3)
        s1 = next(s for s in specs if s['spec_id'] == 'FALSIF-SPEC-001')
        self.assertIn("Doob's optional stopping theorem", s1['formulation'],
                      "FALSIF-SPEC-001 formulation must specify Doob's optional stopping theorem")
        self.assertIn("bounded horizon T_max", s1['formulation'],
                      "FALSIF-SPEC-001 formulation must specify supermartingale property on bounded horizon")
        self.assertIn("T_max = 500", s1['null_hypothesis'])
        self.assertIn("m = 100", s1['null_hypothesis'])

        proc_text = ' '.join(s1['falsification_procedure'])
        self.assertIn("SeedSequence(20261102)", proc_text, "FALSIF-SPEC-001 must declare deterministic seed policy")
        self.assertIn("T_max = 500", proc_text, "FALSIF-SPEC-001 procedure must specify bounded horizon T_max = 500")
        self.assertIn("N = 5,000", proc_text, "FALSIF-SPEC-001 procedure must specify finite sample trajectory N = 5,000")
        self.assertIn("stopping time family", proc_text.lower(), "FALSIF-SPEC-001 procedure must specify stopping time family T")
        self.assertIn("UCB_0.999", proc_text, "FALSIF-SPEC-001 procedure must specify Studentized upper confidence bound UCB_0.999")
        self.assertIn("alpha = 10^-3", proc_text, "FALSIF-SPEC-001 procedure must specify alpha = 10^-3")

        pass_text = s1['pass_fail_criteria']['pass_condition']
        fail_text = s1['pass_fail_criteria']['fail_condition']
        self.assertIn("epsilon_MC", pass_text, "Pass condition must account for Monte Carlo error tolerance")
        self.assertIn("<= 0.05", pass_text, "Pass condition must bound Monte Carlo error tolerance <= 0.05")
        self.assertIn("Ville", pass_text, "Pass condition must evaluate Ville's maximal inequality bound")
        self.assertIn("1e-12", pass_text, "Pass condition must verify machine-precision Sybil neutrality")
        self.assertIn("LCB_0.999", fail_text, "Fail condition must declare unambiguous rejection via lower confidence bound")
        self.assertIn("> 1.0", fail_text, "Fail condition must trigger when LCB_0.999 > 1.0")
        self.assertIn("< 3.5 seconds", s1['cheapest_test'], "Cheapest test must be verifiable in < 3.5 seconds on CPU")

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
