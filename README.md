# Axioval Specifications

Bilingual, vendor-neutral validation templates and rulesets for the Axioval ecosystem.

## Included disciplines

- **Accessibility:** DIN 18040-1 focused movement, encounter, turning, route, and door-clearance requirements.
- **Fire safety:** compartment boundaries, protected penetrations, fire-door metadata, and escape-route geometry contracts.
- **Openings and penetrations:** service/opening association, installation clearance, host cuts, clashes, and fire-protection coordination.

The packages contain concrete policy data, not executable code. Geometric checks reference trusted Axioval capability IDs and fail closed when an application cannot provide exact evidence.

## Use

```bash
git clone --recurse-submodules https://github.com/axioval/specifications.git
PATH="$HOME/.local/bin:$PATH" ./scripts/check.sh
```

See each package README for scope, model prerequisites, and standards references.
