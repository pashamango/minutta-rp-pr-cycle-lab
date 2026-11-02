import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class TestVHPManifest(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / "docs/vhp-manifest.schema.json").read_text())
        self.example = json.loads((ROOT / "docs/examples/vhp-manifest.json").read_text())

    def test_schema_and_example_are_valid_json(self):
        self.assertEqual(self.schema["$id"], "https://mindrock.capital/schemas/vhp-manifest-v1.json")
        self.assertEqual(self.example["schema"], "vhp-manifest/v1")

    def test_example_contains_required_handoff_coordinates(self):
        source = self.example["source"]
        self.assertRegex(source["linear"]["issue_id"], r"^[A-Z]+-[0-9]+$")
        self.assertRegex(source["github"]["commit_sha"], r"^[0-9a-f]{40}$")
        self.assertTrue(self.example["verification"]["clean_checkout"])
        self.assertTrue(self.example["approval"]["required"])
        self.assertFalse(self.example["approval"]["merge_allowed"])

    def test_artifact_paths_are_relative_and_digested(self):
        for artifact in self.example["artifacts"]:
            self.assertFalse(artifact["path"].startswith("/"))
            self.assertNotIn("..", Path(artifact["path"]).parts)
            self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
