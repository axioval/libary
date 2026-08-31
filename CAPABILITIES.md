# Capability support / Unterstützte Fähigkeiten

Every capability is categorized in `capabilities.json`.

- `builtin`: implemented by the source-neutral Axioval engine and exactness-tested.
- `host-required`: a host must provide exact evidence; otherwise evaluation is refused.

Jede Fähigkeit ist in `capabilities.json` eingeordnet. `builtin` ist in der neutralen Engine implementiert. `host-required` benötigt einen exakten Nachweis des Hosts; fehlt er, wird die Prüfung nicht ausgeführt und niemals als bestanden gewertet.
