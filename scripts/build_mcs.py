#!/usr/bin/env python3
"""Build deterministic release artifacts from every Axioval package manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

IDENTITY = re.compile(r"axioval:specification\.([a-z0-9]+(?:[.-][a-z0-9]+)*)")
_CORE_NUMBER = r"(?:0|[1-9][0-9]*)"
_PRERELEASE_ID = r"(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
_BUILD_ID = r"[0-9A-Za-z-]+"
SEMVER = re.compile(
    rf"{_CORE_NUMBER}\.{_CORE_NUMBER}\.{_CORE_NUMBER}"
    rf"(?:-{_PRERELEASE_ID}(?:\.{_PRERELEASE_ID})*)?"
    rf"(?:\+{_BUILD_ID}(?:\.{_BUILD_ID})*)?"
)


def manifests(packages: Path) -> list[Path]:
    return sorted(packages.glob("*/axioval.json"))


def artifact_name(manifest: dict[str, Any]) -> str:
    package_id = manifest.get("id")
    version = manifest.get("version")
    identity = IDENTITY.fullmatch(package_id) if isinstance(package_id, str) else None
    if (
        identity is None
        or not isinstance(version, str)
        or not SEMVER.fullmatch(version)
    ):
        raise ValueError("manifest id/version cannot form a safe release filename")
    return f"{identity.group(1)}-{version}.mcs"


def _run(tool: Path, operation: str, package: Path, archive: Path, root: Path) -> None:
    command = [sys.executable, str(tool), operation]
    if operation == "pack":
        command.extend([str(package), str(archive), "--repository-root", str(root)])
    else:
        command.append(str(archive))
    subprocess.run(command, check=True, cwd=root)


def build(
    root: Path,
    output: Path,
    tool: Path,
    *,
    release_version: str | None = None,
) -> list[Path]:
    root = root.resolve()
    if tool.is_symlink():
        raise ValueError("tool must be a regular non-symlink file")
    tool = tool.resolve()
    if not tool.is_file() or output.is_symlink() or output.exists():
        raise ValueError("tool must exist and output directory must be absent")
    output.parent.mkdir(parents=True, exist_ok=True)
    package_manifests = manifests(root / "packages")
    if not package_manifests:
        raise ValueError("no package manifests found")
    packages: list[tuple[Path, str, dict[str, Any]]] = []
    for manifest_path in package_manifests:
        metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
        packages.append((manifest_path.parent, artifact_name(metadata), metadata))
    if release_version is not None:
        if SEMVER.fullmatch(release_version) is None:
            raise ValueError("release version must be exact SemVer")
        mismatches = [
            package.name
            for package, _, metadata in packages
            if metadata.get("version") != release_version
        ]
        if mismatches:
            raise ValueError(
                f"release version {release_version!r} does not match packages: "
                + ", ".join(mismatches)
            )
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    artifacts: list[Path] = []
    try:
        for package, filename, _ in packages:
            archive = temporary / filename
            _run(tool, "pack", package, archive, root)
            _run(tool, "verify", package, archive, root)
            artifacts.append(archive)
        checksum_lines = [
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in sorted(artifacts)
        ]
        (temporary / "SHA256SUMS").write_text("".join(checksum_lines), encoding="ascii")
        os.replace(temporary, output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return [output / path.name for path in artifacts]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--tool", type=Path)
    parser.add_argument(
        "--release-version",
        help="require exact SemVer and matching version in every package manifest",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    tool = args.tool or root / "vendor/schema/scripts/mcs.py"
    artifacts = build(root, output, tool, release_version=args.release_version)
    for artifact in artifacts:
        print(artifact)
    print(output / "SHA256SUMS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
