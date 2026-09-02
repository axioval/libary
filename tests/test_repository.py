from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContracts(unittest.TestCase):
    def snapshots(self):
        return sorted((ROOT / "packages").glob("*/expected/*.json"))

    def flatten_rules(self, folder):
        return folder["rules"] + [
            rule for child in folder["folders"] for rule in self.flatten_rules(child)
        ]

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

    def test_accessibility_uses_release_bound_ifc_entities(self):
        project = (ROOT / "PklProject").read_text()
        definitions = (
            ROOT / "packages/accessibility-din-18040-1/definitions.pkl"
        ).read_text()
        snapshot = json.loads(
            (
                ROOT
                / "packages/accessibility-din-18040-1/expected/definitions.json"
            ).read_text()
        )

        self.assertIn("openbim.ifc@0.2.1", project)
        self.assertIn('import "@ifc/versions/Ifc4.pkl" as ifc4', definitions)
        self.assertIn('import "../../vendor/schema/schema/adapters/Ifc.pkl"', definitions)
        for entity, definition_id in (
            ("IfcSpace", "axioval:ifc4.space"),
            ("IfcDoor", "axioval:ifc4.door"),
            ("IfcRamp", "axioval:ifc4.ramp"),
        ):
            self.assertIn(
                f'ifcAdapter.entityExternalName(ifc4.entity("{entity}"))',
                definitions,
            )
            external_name = snapshot["objectTypes"][definition_id]["externalNames"][0]
            self.assertEqual(external_name["name"], entity)
            self.assertEqual(
                external_name["typeSystem"],
                "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4",
            )
        self.assertNotIn('name = "IfcSpace"', definitions)
        self.assertNotIn('name = "IfcDoor"', definitions)
        self.assertNotIn('name = "IfcRamp"', definitions)
        self.assertIn("ifc4TemplateTypeSystem", definitions)
        self.assertIn('name = "HandicapAccessible"', definitions)
        self.assertIn('name = "Pset_DoorCommon"', definitions)

    def test_packages_cite_sources_without_copying_normative_prose(self):
        forbidden = "Ausreichend groß ist eine Fläche von"
        for readme in sorted((ROOT / "packages").glob("*/README.md")):
            text = readme.read_text()
            self.assertIn("## Structured provenance", text)
            self.assertNotIn(forbidden, text)

    def test_documents_have_localized_metadata_and_owned_sources(self):
        for path in self.snapshots():
            document = json.loads(path.read_text())
            with self.subTest(document=path.relative_to(ROOT)):
                for field in ("name", "description"):
                    text = document["package"][field]
                    self.assertTrue(text["default"].strip())
                    self.assertTrue(text["translations"]["de"].strip())
                self.assertTrue(document["sources"])
                for source_id, source in document["sources"].items():
                    self.assertEqual(source_id, source["id"])

    def test_every_rule_has_structured_provenance(self):
        for path in sorted((ROOT / "packages").glob("*/expected/ruleset.json")):
            document = json.loads(path.read_text())
            for rule in self.flatten_rules(document["root"]):
                requirement_citations = any(
                    requirement["citations"] for requirement in rule["requirements"]
                )
                with self.subTest(package=path.parent.parent.name, rule=rule["id"]):
                    self.assertTrue(
                        rule["citations"]
                        or rule["parameterCitations"]
                        or requirement_citations
                    )

    def test_accessibility_parameter_provenance_is_exact(self):
        document = json.loads(
            (
                ROOT / "packages/accessibility-din-18040-1/expected/ruleset.json"
            ).read_text()
        )
        rules = {rule["id"]: rule for rule in self.flatten_rules(document["root"])}
        din = "urn:din:18040-1:2010-10"
        policy = "axioval:accessibility.project-profile"
        for rule_id in (
            "meeting-two-wheelchairs-1800",
            "meeting-wheelchair-person-1500",
            "turning-maneuvering-1500",
        ):
            citations = rules[rule_id]["parameterCitations"]
            by_parameters = {
                tuple(item["parameterIds"]): item["citation"] for item in citations
            }
            self.assertEqual(
                by_parameters[("width_metres", "length_metres")]["sourceId"], din
            )
            self.assertEqual(
                by_parameters[("width_metres", "length_metres")]["locators"],
                [{"kind": "clause", "value": "4.3.2"}],
            )
            self.assertEqual(by_parameters[("height_metres",)]["sourceId"], policy)
        door = rules["accessible-door-clear-opening-900"]
        self.assertNotIn("4.6", door["tags"])
        citation = door["parameterCitations"][0]["citation"]
        self.assertEqual(citation["sourceId"], din)
        self.assertEqual(
            citation["locators"],
            [
                {"kind": "clause", "value": "4.3.3.2"},
                {"kind": "table", "value": "1"},
                {"kind": "item", "value": "row 1"},
            ],
        )
        intent = rules["accessible-door-intent"]["parameterCitations"]
        self.assertEqual(len(intent), 1)
        self.assertEqual(intent[0]["parameterIds"], ["property", "expected"])
        self.assertEqual(intent[0]["citation"]["sourceId"], policy)

    def test_fire_rules_remain_project_policy(self):
        document = json.loads(
            (ROOT / "packages/fire-safety/expected/ruleset.json").read_text()
        )
        rules = self.flatten_rules(document["root"])
        policy = "axioval:fire-safety.project-policy"
        for rule in rules:
            with self.subTest(rule=rule["id"]):
                sources = {item["sourceId"] for item in rule["citations"]}
                sources.update(
                    item["citation"]["sourceId"] for item in rule["parameterCitations"]
                )
                self.assertEqual(sources, {policy})
        route = next(
            rule for rule in rules if rule["id"] == "example-escape-route-1200x2000"
        )
        self.assertEqual(route["citations"], [])
        self.assertEqual(len(route["parameterCitations"]), 1)
        self.assertEqual(
            route["parameterCitations"][0]["parameterIds"],
            ["width_metres", "height_metres"],
        )
        self.assertEqual(route["parameterCitations"][0]["citation"]["sourceId"], policy)

    def test_openings_rules_have_targetable_groups_requirements_and_image(self):
        ruleset = json.loads(
            (ROOT / "packages/openings-penetrations/expected/ruleset.json").read_text()
        )
        rules = self.flatten_rules(ruleset["root"])
        expected_groups = {
            "opening-cuts-host": {"openings", "penetrated-elements"},
            "service-fits-with-25mm-allowance": {
                "openings",
                "penetrating-elements",
            },
            "no-host-clash-outside-opening": {
                "openings",
                "penetrated-elements",
                "penetrating-elements",
            },
            "opening-quantities-match-geometry": {"openings"},
            "opening-has-service-or-fill": {
                "filling-elements",
                "openings",
                "penetrating-elements",
            },
            "fire-boundary-opening-protected": {
                "openings",
                "penetrated-elements",
            },
        }
        # Each current openings requirement addresses every role in its rule scope.
        expected_requirement_targets = expected_groups
        self.assertEqual({rule["id"] for rule in rules}, set(expected_groups))
        seen_groups = set()
        for rule in rules:
            with self.subTest(rule=rule["id"]):
                groups = rule["applicability"]["groups"]
                self.assertEqual(set(groups), expected_groups[rule["id"]])
                self.assertEqual(len(rule["requirements"]), 1)
                for group_id, group in groups.items():
                    self.assertEqual(group_id, group["id"])
                    self.assertIn("de", group["name"]["translations"])
                    seen_groups.add(group_id)
                for requirement in rule["requirements"]:
                    self.assertIn("de", requirement["statement"]["translations"])
                    self.assertEqual(
                        set(requirement["targetGroups"]),
                        expected_requirement_targets[rule["id"]],
                    )
                    self.assertTrue(requirement["citations"])
                    self.assertEqual(
                        {item["sourceId"] for item in requirement["citations"]},
                        {"axioval:openings.project-policy"},
                    )
                self.assertTrue(rule["explanatoryImages"])
                image = rule["explanatoryImages"][0]
                self.assertEqual(
                    image["path"], "assets/opening-coordination-groups.svg"
                )
                self.assertIn("de", image["alternativeText"]["translations"])
                self.assertIn("de", image["caption"]["translations"])
        service = next(
            rule for rule in rules if rule["id"] == "service-fits-with-25mm-allowance"
        )
        service_sources = {
            tuple(item["parameterIds"]): item["citation"]["sourceId"]
            for item in service["parameterCitations"]
        }
        self.assertEqual(
            service_sources,
            {
                ("side_clearance_metres",): "axioval:openings.project-policy",
                ("end_clearance_metres",): "axioval:openings.project-policy",
            },
        )
        quantity = next(
            rule for rule in rules if rule["id"] == "opening-quantities-match-geometry"
        )
        quantity_sources = {
            tuple(item["parameterIds"]): item["citation"]["sourceId"]
            for item in quantity["parameterCitations"]
        }
        self.assertEqual(
            quantity_sources,
            {
                ("width",): "urn:buildingsmart:ifc:IFC4-ADD2-TC1",
                ("height",): "urn:buildingsmart:ifc:IFC4-ADD2-TC1",
                ("depth",): "urn:buildingsmart:ifc:IFC4-ADD2-TC1",
                ("tolerance_metres",): "axioval:openings.project-policy",
            },
        )
        protected = next(
            rule for rule in rules if rule["id"] == "fire-boundary-opening-protected"
        )
        protected_sources = {
            tuple(item["parameterIds"]): item["citation"]["sourceId"]
            for item in protected["parameterCitations"]
        }
        self.assertEqual(
            protected_sources,
            {
                ("property",): "urn:buildingsmart:ifc:IFC4-ADD2-TC1",
                ("expected",): "axioval:openings.project-policy",
            },
        )
        self.assertEqual(
            seen_groups,
            {
                "filling-elements",
                "openings",
                "penetrated-elements",
                "penetrating-elements",
            },
        )

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
