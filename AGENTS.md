# Axioval specifications

This repository owns concrete, vendor-neutral rule definition packages and rulesets. It consumes the canonical Axioval MCS schema from `vendor/schema` and must not add executable package code or privileged trust.

## Layout

- `packages/` contains independently installable discipline rulesets. Every package has its own manifest, definitions, rules, and generated JSON snapshots.
- `scripts/` validates all packages with the pinned MCS binder and atomically builds verified `.mcs` release artifacts plus `SHA256SUMS`.
- `tests/` enforces localization, source citation, repository structure, fail-closed authoring contracts, and release-artifact discovery.
- `vendor/schema` is the intentionally stable checkout path for the pinned `axioval/mcs` submodule. Do not copy schema modules into this repository.

## Rules

- Default localized text is English; every user-facing field also provides German (`de`).
- Requirements from standards are parameterized and cited. Do not reproduce copyrighted normative prose.
- Sources are owned by each ruleset/definition document. Attach provenance at the
  narrowest useful point, especially exact parameter IDs; cite editable example
  values as `projectPolicy`, not as regulation or standard content.
- Citations are declarative only. They never change applicability, evidence,
  verdicts, legal force, or compliance status; free-text tags are not citations.
- Geometry rules name trusted capability IDs and concrete dimensions. Missing runtime capabilities or evidence must fail closed.
- IFC concepts use IFC4 ADD2 TC1 names verified against the buildingSMART PSD/QTO catalog.
- Multi-population rules use named applicability groups; every requirement targets
  existing group IDs in the same rule.
- Explanatory images stay inside their package, include English and German
  alternative text/captions, and pass the pinned schema's content checks.
- A rule package is policy data only. It never executes package-supplied code.

## Validation

Run `./scripts/check.sh`. Commit regenerated `expected/*.json` snapshots whenever Pkl source changes.
