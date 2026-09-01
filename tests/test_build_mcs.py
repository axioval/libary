from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build_mcs


class BuildMCSTests(unittest.TestCase):
    def test_discovers_stable_release_names(self) -> None:
        discovered = [
            build_mcs.artifact_name(json.loads(path.read_text(encoding="utf-8")))
            for path in build_mcs.manifests(ROOT / "packages")
        ]
        self.assertEqual(
            discovered,
            [
                "accessibility-din-18040-1-0.1.0.mcs",
                "fire-safety-0.1.0.mcs",
                "openings-penetrations-0.1.0.mcs",
            ],
        )

    def test_rejects_unsafe_package_identity(self) -> None:
        with self.assertRaises(ValueError):
            build_mcs.artifact_name({"id": "org.example/escape", "version": "0.1.0"})
        for version in ("1.0.0-01", "1.0.0-alpha..1", "1.0.0-"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                build_mcs.artifact_name(
                    {"id": "axioval:specification.example", "version": version}
                )

    def test_rejects_symlinked_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool = root / "mcs.py"
            tool.symlink_to(ROOT / "scripts/build_mcs.py")
            with self.assertRaisesRegex(ValueError, "tool must"):
                build_mcs.build(root, root / "dist", tool)

    def test_release_version_must_match_every_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "packages/example"
            package.mkdir(parents=True)
            (package / "axioval.json").write_text(
                json.dumps({"id": "axioval:specification.example", "version": "1.2.3"}),
                encoding="utf-8",
            )
            for version in ("latest", "1.2.4"):
                with self.subTest(version=version), self.assertRaises(ValueError):
                    build_mcs.build(
                        root,
                        root / "dist",
                        ROOT / "scripts/build_mcs.py",
                        release_version=version,
                    )
                self.assertFalse((root / "dist").exists())

    def test_release_workflow_is_retry_safe(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        for required in (
            "concurrency:",
            "gh release view",
            "--clobber",
            "--release-version",
            "published immutable release already exists",
        ):
            with self.subTest(required=required):
                self.assertIn(required, workflow)
        ordered_steps = (
            "name: Prepare draft and upload assets",
            "name: Attest checksums",
            "name: Publish immutable release",
        )
        self.assertEqual(
            [workflow.index(step) for step in ordered_steps],
            sorted(workflow.index(step) for step in ordered_steps),
        )

    def test_rejects_repository_without_manifests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "dist"
            with self.assertRaisesRegex(ValueError, "no package manifests"):
                build_mcs.build(root, output, ROOT / "scripts/build_mcs.py")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
