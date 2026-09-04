import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cas", ROOT / "storage/tools/cas.py")
cas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cas)


class PublishTests(unittest.TestCase):
    def test_ref_updates_only_after_verified_publish(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "artifact"
            source.mkdir()
            (source / "report.txt").write_text("verified\n", encoding="utf-8")
            result = cas.publish(root / "cas", source, "report", "tasks/TASK-1")
            self.assertEqual((root / "cas/refs/tasks/TASK-1").read_text().strip(),
                             result["root_sha256"])
            self.assertEqual(result["files"], 1)


if __name__ == "__main__":
    unittest.main()
