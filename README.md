# Axioval Specifications

Bilingual, vendor-neutral validation templates and rulesets for the Axioval ecosystem.

## Included disciplines

- **Accessibility:** DIN 18040-1 focused movement, encounter, turning, route, and door-clearance requirements.
- **Fire safety:** compartment boundaries, protected penetrations, fire-door metadata, and escape-route geometry contracts.
- **Openings and penetrations:** service/opening association, installation clearance, host cuts, clashes, and fire-protection coordination.

The packages contain concrete policy data, not executable code. Geometric checks reference trusted Axioval capability IDs and fail closed when an application cannot provide exact evidence. Rules may also name targetable applicability groups, bind localized requirements to those groups, and reference localized package-contained explanatory images.

## Use

```bash
git clone --recurse-submodules https://github.com/axioval/libary.git
PATH="$HOME/.local/bin:$PATH" ./scripts/check.sh
python3 scripts/build_mcs.py
```

The builder writes one deterministic, verified `.mcs` archive per package plus
`dist/SHA256SUMS`. CI keeps these as short-lived artifacts. A release tag must be
exactly `v<SemVer>`, and that version must equal every package manifest version.
The release workflow creates or resumes a draft, uploads the complete asset set,
attests the listed checksums, and only then publishes the immutable
[GitHub Release](https://github.com/axioval/libary/releases). Generated archives
are never committed.

See each package README for scope, model prerequisites, and standards references.
