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
        """Verify claim fields (assumptions, contradictions, rejection thresholds, applications) are relevant and non-boilerplate."""
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

    def test_direct_object_read_exact_evidence(self):
        """Verify exact_source_read_evidence is an exact, verbatim character-by-character substring of GitHub direct object."""
        for c in self.claims:
            sid = str(c['source_id'])
            self.assertIn(sid, self.direct_objects, f"Source ID {sid} missing from direct objects cache")
            d_obj = self.direct_objects[sid]
            body = d_obj['body']
            ev = c['exact_source_read_evidence']
            self.assertIn(ev, body, f"Verbatim evidence mismatch in {c['claim_id']} (source {sid})")
            self.assertTrue(len(ev) >= 50, f"Evidence too short in {c['claim_id']}")

    def test_direct_object_urls_and_ids(self):
        """Verify source_url and source_sha256 strictly match GitHub direct objects."""
        for c in self.claims:
            sid = str(c['source_id'])
            expected_url = f"https://github.com/pashamango/minutta-rp-pr-cycle-lab/issues/168#issuecomment-{sid}"
            self.assertEqual(c['source_url'], expected_url)
            d_obj = self.direct_objects[sid]
            expected_sha = hashlib.sha256(d_obj['body'].encode('utf-8')).hexdigest()
            self.assertEqual(c['source_sha256'], expected_sha)

    def test_canonical_duplicate_lineage(self):
        """Verify canonical deduplication, strict acyclicity of parent chains and forest, and valid merge rules."""
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
        # In the parent forest, directed edges are child -> parent
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

    def test_graph_relations_strictly_typed(self):
        """Verify that all graph relations are strictly typed and eliminate ambiguous relations."""
        allowed_relations = {'refines', 'generalizes', 'supports', 'contradicts', 'duplicates', 'maps_to_canonical'}
        self.assertTrue(len(self.graph['edges']) >= 45)
        for edge in self.graph['edges']:
            rel = edge['relation']
            self.assertIn(rel, allowed_relations, f"Disallowed relation '{rel}' found in edge")
            self.assertNotEqual(rel, 'refines_or_deduplicates', "Ambiguous relation 'refines_or_deduplicates' must not exist")

    def test_cluster_counts_consistency(self):
        """Verify cluster counts are strictly 10 / 16 / 19 across all artifacts."""
        expected_counts = {'Cluster-1': 10, 'Cluster-2': 16, 'Cluster-3': 19}
        actual_counts = dict(Counter(c['cluster_id'] for c in self.claims))
        self.assertEqual(actual_counts, expected_counts)
        self.assertEqual(self.graph['graph_metadata']['cluster_counts'], expected_counts)

    def test_top_three_falsification_specs_and_reproducible_ranking(self):
        """Verify all 6 canonical invariants are evaluated objectively, and top 3 emerge from reproducible rubric."""
        rubric = self.specs['metadata']['scoring_rubric']
        w = rubric['weights']
        all_evals = self.specs['all_canonical_evaluations']

        # 1. All 6 canonical invariants must be evaluated
        self.assertEqual(len(all_evals), 6, "All 6 canonical invariants must be evaluated")
        eval_ids = {e['canonical_invariant_id'] for e in all_evals}
        expected_ids = {'CANONICAL-01', 'CANONICAL-02', 'CANONICAL-03', 'CANONICAL-04', 'CANONICAL-05', 'CANONICAL-06'}
        self.assertEqual(eval_ids, expected_ids)

        # 2. Check each candidate's score components and dynamically calculate composite score
        calculated_scores = []
        for e in all_evals:
            cid = e['canonical_invariant_id']
            c = e['component_scores']
            justifications = e['component_justifications']
            for axis in ['C1_rigor_and_falsifiability', 'C2_anti_sybil_and_grounding', 'C3_cross_domain_generality', 'C4_test_cost_efficiency']:
                self.assertIn(axis, c)
                self.assertTrue(0.0 <= c[axis] <= 10.0)
                self.assertIn(axis, justifications)
                self.assertTrue(len(justifications[axis]) >= 20, f"Justification for {cid} on {axis} must be substantive")

            computed_s = (
                w['C1_rigor_and_falsifiability'] * c['C1_rigor_and_falsifiability'] +
                w['C2_anti_sybil_and_grounding'] * c['C2_anti_sybil_and_grounding'] +
                w['C3_cross_domain_generality'] * c['C3_cross_domain_generality'] +
                w['C4_test_cost_efficiency'] * c['C4_test_cost_efficiency']
            )
            self.assertAlmostEqual(e['composite_score'], computed_s, places=1)
            calculated_scores.append((computed_s, cid, e))

        # 3. Dynamic sorting of all 6 canonical invariants
        calculated_scores.sort(key=lambda x: x[0], reverse=True)
        ranked_ids = [item[1] for item in calculated_scores]

        # Verify that top 3 ranks strictly match CANONICAL-01, CANONICAL-03, CANONICAL-05
        self.assertEqual(ranked_ids[0], 'CANONICAL-01')
        self.assertEqual(ranked_ids[1], 'CANONICAL-03')
        self.assertEqual(ranked_ids[2], 'CANONICAL-05')

        # Verify ranks 4, 5, 6
        self.assertEqual(ranked_ids[3], 'CANONICAL-06')
        self.assertEqual(ranked_ids[4], 'CANONICAL-02')
        self.assertEqual(ranked_ids[5], 'CANONICAL-04')

        # 4. Verify exactly 3 falsification specs correspond to the top 3 ranked invariants
        specs = self.specs['specs']
        self.assertEqual(len(specs), 3)
        expected_spec_anchors = {"CLAIM-011", "CLAIM-001", "CLAIM-003"}
        actual_spec_anchors = {s['anchor_claim_id'] for s in specs}
        self.assertEqual(actual_spec_anchors, expected_spec_anchors)

        for s in specs:
            self.assertIn("spec_id", s)
            self.assertIn("canonical_invariant_id", s)
            self.assertIn(s['canonical_invariant_id'], {'CANONICAL-01', 'CANONICAL-03', 'CANONICAL-05'})
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

if __name__ == "__main__":
    unittest.main()
