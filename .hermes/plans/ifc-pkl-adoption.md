# IFC Pkl adoption plan

## Goal

Replace the accessibility package's hand-authored IFC entity identities with release-bound references from `openbim.ifc@0.2.1`, lowered through the canonical MCS IFC adapter.

## Constraints

- Preserve normalized rule meaning, IDs, applicability, and parameter values.
- Keep the MCS schema vendored only as the pinned `vendor/schema` submodule.
- Do not copy IFC catalogs into this repository.
- Keep package network permissions host/path-scoped and verify dependency locks from a cold cache.
- IFC PSD/QTO occurrences are not bundled by `openbim.ifc@0.2.1`; `Pset_DoorCommon` and `HandicapAccessible` therefore remain explicit local definitions rather than falsely claiming package ownership.

## Workstreams

1. Pin `vendor/schema` to reviewed MCS `307ce080…`, which provides the one-way IFC entity adapter and locks IFC `0.2.1`.
2. Add the hosted IFC package dependency and checksum lock at the library project root.
3. Import IFC4 and lower `IfcSpace`, `IfcDoor`, and `IfcRamp` through `schema/adapters/Ifc.pkl`.
4. Use package release provenance for the IFC source/citations while retaining explicit template occurrence names.
5. Harden validation for package/projectpackage imports, scoped network resources, and deterministic cold lock resolution.
6. Regenerate snapshots, build deterministic `.mcs` archives, and prove rule semantics are unchanged apart from corrected IFC identity/provenance.

## Validation

- RED source/integration contract first.
- `./scripts/check.sh` with Pkl 0.32.1 and a cold package cache.
- Snapshot diff limited to intended IFC source/type-system changes.
- Two archive builds byte-identical and verified.
- `git diff --check`, clean exact commit, immutable review before landing.

## Rollback

The implementation is isolated in a detached worktree. The canonical checkout remains untouched until exact-commit review passes.

## Status

- MCS `main` published at `307ce0805b7ae782d0c39a98b6442a4e6b9325c8`; validate and Pages workflows passed.
- RED contract was observed failing before the package dependency/import change.
- Library now pins `openbim.ifc@0.2.1`, verifies the lock cold, delegates Pkl evaluation to the schema sandbox, and uses typed IFC4 entities for `IfcSpace`, `IfcDoor`, and `IfcRamp`.
- All packages moved to `0.1.1` because immutable `v0.1.0` exists and this repository releases packages atomically.
- Full check: 18 tests and three bilingual packages pass; Markdown lint is clean.
- Two release builds are byte-identical. Accessibility artifact SHA-256: `9dafb0e592797d603fe228c706a35ce73a51debf464d7b6aa102d2501d9fdcbd`.
- Pending: exact commit, immutable review, safe landing, CI, and optional `v0.1.1` release publication.
