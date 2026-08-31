# Axioval specifications

This repository owns concrete, vendor-neutral rule definition packages and rulesets. It consumes the canonical Axioval schema from `vendor/schema` and must not add executable package code or privileged trust.

## Layout

- `packages/` contains independently installable discipline rulesets. Every package has its own manifest, definitions, rules, and generated JSON snapshots.
- `scripts/` validates all packages with the pinned schema binder.
- `tests/` enforces localization, source citation, repository structure, and fail-closed authoring contracts.
- `vendor/schema` is a pinned Git submodule. Do not copy schema modules into this repository.

## Rules

- Default localized text is English; every user-facing field also provides German (`de`).
- Requirements from standards are parameterized and cited. Do not reproduce copyrighted normative prose.
- Geometry rules name trusted capability IDs and concrete dimensions. Missing runtime capabilities or evidence must fail closed.
- IFC concepts use IFC4 ADD2 TC1 names verified against the buildingSMART PSD/QTO catalog.
- A rule package is policy data only. It never executes package-supplied code.

## Validation

Run `./scripts/check.sh`. Commit regenerated `expected/*.json` snapshots whenever Pkl source changes.
