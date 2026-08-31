from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContracts(unittest.TestCase):
    def snapshots(self):
        return sorted((ROOT / "packages").glob("*/expected/*.json"))

    def test_three_disciplines_are_independent_packages(self):
        packages = {
            path.parent.name for path in (ROOT / "packages").glob("*/axioval.json")
        }
        self.assertEqual(
            packages,
            {"accessibility-din-18040-1", "fire-safety", "openings-penetrations"},
        )

    def test_every_localized_text_has_english_and_german(self):
        self.assertTrue(self.snapshots(), "normalized snapshots are missing")

        def walk(value, context):
            if isinstance(value, dict):
                if "default" in value and "translations" in value:
                    self.assertIsInstance(value["default"], str, context)
                    self.assertTrue(value["default"].strip(), context)
                    self.assertIn("de", value["translations"], context)
                    self.assertTrue(value["translations"]["de"].strip(), context)
                for key, child in value.items():
                    walk(child, f"{context}.{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, f"{context}[{index}]")

        for path in self.snapshots():
            walk(json.loads(path.read_text()), str(path.relative_to(ROOT)))

    def test_accessibility_dimensions_are_concrete(self):
        text = (ROOT / "packages/accessibility-din-18040-1/ruleset.pkl").read_text()
        for value in ("1.8", "1.5", "1.2", "0.9"):
            self.assertIn(f"value = {value}", text)
        for capability in (
            "free-floor-rectangle",
            "minimum-clear-route",
            "minimum-clear-opening",
        ):
            self.assertIn(
                capability,
                (
                    ROOT / "packages/accessibility-din-18040-1/definitions.pkl"
                ).read_text(),
            )

    def test_packages_cite_sources_without_copying_normative_prose(self):
        forbidden = "Ausreichend groß ist eine Fläche von"
        for readme in sorted((ROOT / "packages").glob("*/README.md")):
            text = readme.read_text()
            self.assertIn("## Sources", text)
            self.assertNotIn(forbidden, text)

    def test_schema_is_pinned_not_copied(self):
        self.assertTrue((ROOT / ".gitmodules").is_file())
        self.assertTrue((ROOT / "vendor/schema/schema/Definitions.pkl").is_file())
        copied = list((ROOT / "packages").glob("**/Types.pkl"))
        self.assertEqual(copied, [])

    def test_every_capability_has_an_explicit_support_status(self):
        support = json.loads((ROOT / "capabilities.json").read_text())
        declared = set()
        for path in (ROOT / "packages").glob("*/expected/definitions.json"):
            document = json.loads(path.read_text())
            declared.update(
                item["capability"] for item in document["definitions"].values()
            )
        self.assertEqual(set(support), declared)
        self.assertLessEqual(set(support.values()), {"builtin", "host-required"})
        self.assertEqual(
            {
                capability
                for capability, status in support.items()
                if status == "builtin"
            },
            {
                "axioval:capability.free-floor-rectangle",
                "axioval:capability.property-exists",
                "axioval:capability.property-value-equals",
            },
        )


if __name__ == "__main__":
    unittest.main()
