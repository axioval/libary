#!/usr/bin/env python3
"""Fail-closed validation for every concrete Axioval package."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "vendor/schema"
sys.path.insert(0, str(SCHEMA / "scripts"))

import validate as schema_validate
from contracts import bind_ruleset, validate_definition_document


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def evaluate(module: Path) -> dict:
    executable = shutil.which("pkl")
    if executable is None:
        fail("pkl is not installed or not on PATH")
    process = subprocess.run(
        [
            executable,
            "eval",
            "-f",
            "json",
            "--root-dir",
            str(ROOT),
            "--allowed-modules",
            "file:,pkl:",
            "--allowed-resources",
            "file:,prop:",
            "--timeout",
            "10",
            str(module),
        ],
        cwd=module.parent,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "NO_COLOR": "1"},
    )
    if process.returncode:
        fail(f"{module.relative_to(ROOT)}: Pkl evaluation failed\n{process.stderr}")
    try:
        value = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        fail(f"{module.relative_to(ROOT)} did not render JSON: {error}")
    if type(value) is not dict:
        fail(f"{module.relative_to(ROOT)} did not render an object")
    return value


def snapshot(module: Path, value: dict, update: bool) -> None:
    path = module.parent / "expected" / f"{module.stem}.json"
    rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if update:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)
    elif not path.is_file():
        fail(
            f"missing snapshot {path.relative_to(ROOT)}; run scripts/validate.py --update"
        )
    elif path.read_text() != rendered:
        fail(
            f"stale snapshot {path.relative_to(ROOT)}; run scripts/validate.py --update"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update", action="store_true", help="rewrite normalized snapshots"
    )
    args = parser.parse_args()

    if not (SCHEMA / "schema/Definitions.pkl").is_file():
        fail("vendor/schema is missing; clone with --recurse-submodules")
    expected_version = (ROOT / ".pkl-version").read_text().strip()
    executable = shutil.which("pkl")
    if executable is None:
        fail("pkl is not installed or not on PATH")
    version = subprocess.run(
        [executable, "--version"], text=True, capture_output=True, check=True
    ).stdout
    if not version.startswith(f"Pkl {expected_version} "):
        fail(f"expected Pkl {expected_version}, got {version.strip()}")

    manifests = sorted((ROOT / "packages").glob("*/axioval.json"))
    if len(manifests) < 3:
        fail("expected at least three discipline package manifests")

    package_ids: set[str] = set()
    for manifest_path in manifests:
        manifest = schema_validate.validate_manifest(
            json.loads(manifest_path.read_text()), manifest_path
        )
        if manifest["id"] in package_ids:
            fail(f"duplicate package id {manifest['id']}")
        package_ids.add(manifest["id"])
        rules_module = schema_validate.local_module(
            manifest_path.parent, manifest["entrypoint"]
        )
        definition_modules = [
            schema_validate.local_module(manifest_path.parent, entry)
            for entry in manifest["definitionEntrypoints"]
        ]
        rules = evaluate(rules_module)
        metadata = rules.get("package", {})
        if (
            rules.get("schemaVersion") != manifest["schemaVersion"]
            or metadata.get("id") != manifest["id"]
            or metadata.get("version") != manifest["version"]
        ):
            fail(f"{manifest_path.relative_to(ROOT)} disagrees with evaluated package")
        definitions = []
        for module in definition_modules:
            value = evaluate(module)
            validate_definition_document(value, str(module.relative_to(ROOT)))
            definitions.append(value)
            snapshot(module, value, args.update)
        bind_ruleset(
            rules,
            definitions,
            str(rules_module.relative_to(ROOT)),
            asset_root=manifest_path.parent,
        )
        snapshot(rules_module, rules, args.update)

    subprocess.run(
        [executable, "eval", "PklProject"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(f"validated {len(manifests)} bilingual discipline package(s)")


if __name__ == "__main__":
    main()
