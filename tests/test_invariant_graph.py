#!/usr/bin/env python3
import unittest
import json
import os

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

    def test_claim_count_in_range(self):
        """Verify claim count is between 30 and 50 as mandated by MIN-18."""
        self.assertTrue(30 <= len(self.claims) <= 50, f"Expected 30-50 claims, got {len(self.claims)}")

    def test_claim_fields_complete(self):
        """Verify every claim unit possesses all required constitutional fields."""
        required = [
            "claim_id", "source_id", "source_url", "exact_source_read_evidence",
            "epistemic_label", "statement", "assumptions", "null_test",
            "contradictions", "duplicates", "applications", "versions",
            "scheduler", "domain", "cluster"
        ]
        for c in self.claims:
            for field in required:
                self.assertIn(field, c, f"Claim {c.get('claim_id')} missing field {field}")
            self.assertIn(c['epistemic_label'], ["fact", "hypothesis", "derived", "user testimony"])
            self.assertTrue(len(c['exact_source_read_evidence']) >= 10)
            self.assertIn("null_hypothesis", c['null_test'])
            self.assertIn("test_procedure", c['null_test'])
            self.assertIn("rejection_threshold", c['null_test'])

    def test_graph_integrity(self):
        """Verify graph nodes and edges are non-empty and well-formed."""
        self.assertEqual(len(self.graph['nodes']), len(self.claims))
        self.assertTrue(len(self.graph['edges']) >= 30)
        self.assertIn("top_3_ranked_candidates", self.graph['graph_metadata'])
        self.assertEqual(len(self.graph['graph_metadata']['top_3_ranked_candidates']), 3)

    def test_falsification_specs(self):
        """Verify exactly 3 bounded falsification specs exist with required attributes."""
        specs = self.specs['specs']
        self.assertEqual(len(specs), 3)
        for s in specs:
            self.assertIn("spec_id", s)
            self.assertIn("target_invariant", s)
            self.assertIn("null_hypothesis", s)
            self.assertIn("falsification_procedure", s)
            self.assertIn("pass_fail_criteria", s)
            self.assertIn("cheapest_test", s)

    def test_excluded_data_documented(self):
        """Verify excluded data catalog is non-empty and contains valid rationale."""
        records = self.excluded['records']
        self.assertTrue(len(records) >= 10)
        for r in records:
            self.assertIn("source_id", r)
            self.assertIn("exclusion_reason", r)
            self.assertEqual(r['epistemic_classification'], "EXCLUDED_NOOP")

if __name__ == "__main__":
    unittest.main()
