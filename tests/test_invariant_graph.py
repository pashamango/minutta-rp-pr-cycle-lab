#!/usr/bin/env python3
import unittest
import json
import os
import hashlib
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

        # 4. Semantic Fixture Concordance: programmatic verification of claim-specific relevance
        SEMANTIC_FIXTURES = {
            'CLAIM-001': ['simplex', 'dirichlet', 'permutation'],
            'CLAIM-002': ['search budget', 'selection'],
            'CLAIM-003': ['process', 'exit', 'wrapper', 'kernel'],
            'CLAIM-004': ['e-process', 'capital', 'conserved'],
            'CLAIM-005': ['context', 'behavior', 'value'],
            'CLAIM-006': ['future', '50%'],
            'CLAIM-007': ['log', 'wealth'],
            'CLAIM-008': ['evidence bits', 'accounting'],
            'CLAIM-009': ['credential', 'principal', 'runtime'],
            'CLAIM-010': ['resource', 'allocation', 'measure'],
            'CLAIM-011': ['portfolio', 'simplex'],
            'CLAIM-012': ['kraft', 'prefix', 'tree'],
            'CLAIM-013': ['ratio', 'scale', 'measurement'],
            'CLAIM-014': ['branch', 'split', 'capital'],
            'CLAIM-015': ['shared memory', 'cryptographic'],
            'CLAIM-016': ['dag', 'merge'],
            'CLAIM-017': ['git', 'commit'],
            'CLAIM-018': ['linear', 'resource'],
            'CLAIM-019': ['ancestry', 'algebra', 'strength'],
            'CLAIM-020': ['shadow', 'provenance'],
            'CLAIM-021': ['consumable', 'reusable'],
            'CLAIM-022': ['digest', 'issuer'],
            'CLAIM-023': ['composition', 'group'],
            'CLAIM-024': ['convex', 'linear', 'stability'],
            'CLAIM-025': ['bias', 'group'],
            'CLAIM-026': ['mixture', 'disjoint'],
            'CLAIM-027': ['capability', 'delegation', 'scope'],
            'CLAIM-028': ['attenuation', 'lattice'],
            'CLAIM-029': ['scope', 'derivation'],
            'CLAIM-030': ['semilattice', 'policy'],
            'CLAIM-031': ['token', 'permission'],
            'CLAIM-032': ['equilibrium', 'interaction'],
            'CLAIM-033': ['monotonic', 'mailbox'],
            'CLAIM-034': ['attractor', 'rebalancing'],
            'CLAIM-035': ['supersession', 'revocation'],
            'CLAIM-036': ['cause', 'purpose'],
            'CLAIM-037': ['utility', 'difficulty'],
            'CLAIM-038': ['fountain', 'qr'],
            'CLAIM-039': ['absurd', 'hypothesis'],
            'CLAIM-040': ['redundancy', 'availability'],
            'CLAIM-041': ['brier', 'forecast'],
            'CLAIM-042': ['rank', 'matrix'],
            'CLAIM-043': ['complexity', 'decomposition'],
            'CLAIM-044': ['resilience', 'novelty'],
            'CLAIM-045': ['orthogonal', 'target']
        }

        for c in self.claims:
            cid = c['claim_id']
            full_text = ' '.join(
                c['assumptions'] +
                c['contradictions'] +
                [c['null_test']['null_hypothesis'], c['null_test']['test_procedure'], c['null_test']['rejection_threshold']] +
                c['applications']
            ).lower()

            req = SEMANTIC_FIXTURES.get(cid, [])
            for concept in req:
                self.assertIn(concept, full_text, f"Claim {cid} fails semantic fixture: missing concept '{concept}' in tailored fields")

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

        # 2. Score Band Compliance Verification (Resolving Defect MIN-18-QA-01)
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

                # Criterion compliance rules from IDEIR-v1
                just_text = justifications[axis].lower()
                if axis == 'C2_anti_sybil_and_grounding':
                    if score >= 8.5:
                        self.assertTrue(any(term in just_text for term in ['cryptographic', 'kernel', 'anti-sybil', 'simplex']),
                                        f"{cid} C2 score >= 8.5 requires cryptographic, kernel, or simplex anti-sybil binding")
                    else:
                        self.assertTrue(any(term in just_text for term in ['heuristic', 'permutation', 'semantic']),
                                        f"{cid} C2 score < 8.5 documents heuristic/permutation matching")
                elif axis == 'C3_cross_domain_generality':
                    if score >= 9.0:
                        self.assertTrue(any(term in just_text for term in ['universal', 'multi-agent', 'scientific', 'settlement']),
                                        f"{cid} C3 score >= 9.0 requires universal cross-domain coverage")
                    else:
                        self.assertTrue(any(term in just_text for term in ['domain-specific', 'specialized', 'runtime', 'limited transfer']),
                                        f"{cid} C3 score < 9.0 documents domain specialization or limited transfer")
                elif axis == 'C4_test_cost_efficiency':
                    if score >= 9.5:
                        self.assertTrue(any(term in just_text for term in ['< 3.5s', '< 2.0s', '< 1.5s', '< 1.0s', 'ultra-low-cost']),
                                        f"{cid} C4 score >= 9.5 requires test time < 3.5s")

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
