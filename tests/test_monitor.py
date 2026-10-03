import tempfile
import unittest
from pathlib import Path

from integrity_watch.monitor import build_manifest, compare_manifests, load_manifest, save_manifest


class MonitorTests(unittest.TestCase):
    def test_detects_added_changed_and_missing_files(self):
        baseline = {"same.txt": "a" * 64, "changed.txt": "b" * 64, "missing.txt": "c" * 64}
        current = {"same.txt": "a" * 64, "changed.txt": "d" * 64, "added.txt": "e" * 64}

        self.assertEqual(
            compare_manifests(baseline, current),
            {"added": ["added.txt"], "changed": ["changed.txt"], "missing": ["missing.txt"]},
        )

    def test_manifest_hashes_regular_files_and_skips_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.txt").write_text("hello", encoding="utf-8")
            manifest = build_manifest(root)

        self.assertEqual(len(manifest), 1)
        self.assertEqual(len(manifest["sample.txt"]), 64)

    def test_round_trips_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "baseline.json"
            expected = {"folder/sample.txt": "f" * 64}
            save_manifest(expected, path)

            self.assertEqual(load_manifest(path), expected)

    def test_rejects_invalid_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "baseline.json"
            path.write_text('{"file.txt":"not-a-hash"}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_manifest(path)


if __name__ == "__main__":
    unittest.main()
