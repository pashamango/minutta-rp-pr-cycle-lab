import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("validate", ROOT / "tools" / "validate-vhp-manifest.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestVHPManifest(unittest.TestCase):
    def setUp(self):
        with open(ROOT / "examples" / "vhp-manifest.json", encoding="utf-8") as stream:
            self.manifest = json.load(stream)

    def test_reference_manifest_is_valid(self):
        self.assertTrue(module.validate(self.manifest))

    def test_rejects_missing_git_commit(self):
        self.manifest["sources"]["github"]["commitSha"] = "not-a-sha"
        with self.assertRaises(ValueError):
            module.validate(self.manifest)

    def test_rejects_traversal_artifact(self):
        self.manifest["artifacts"][0]["path"] = "../secret.txt"
        with self.assertRaises(ValueError):
            module.validate(self.manifest)

    def test_rejects_automatic_merge(self):
        self.manifest["policy"]["autoMerge"] = True
        with self.assertRaises(ValueError):
            module.validate(self.manifest)


if __name__ == "__main__":
    unittest.main()
