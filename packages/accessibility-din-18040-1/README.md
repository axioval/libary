# Accessibility / Barrierefreiheit

Bilingual DIN 18040-1 focused templates and concrete rules for movement areas, encounters, turning, straight route segments, and accessible openings.

## Model prerequisites

Assign the documented classification codes to the spaces, route segments, and doors for which each use case is expected. This is deliberate: IFC geometry alone cannot prove whether encounters or changes of direction are expected.

Applications must provide exact free-space, route, and opening evidence. Missing geometry, incomplete obstacle coverage, or unsupported capabilities are **not evaluated**, never passed.

## Release-bound IFC entities

Import the exact IFC release and lower its typed entity reference through the
pinned MCS adapter:

```pkl
import "@ifc/versions/Ifc4.pkl" as ifc4
import "../../vendor/schema/schema/adapters/Ifc.pkl" as ifcAdapter

externalNames {
  ifcAdapter.entityExternalName(ifc4.entity("IfcDoor"))
}
```

The project-level `PklProject` owns the `@ifc` dependency and its checksum lock.
Do not substitute the package transport URI for the semantic IFC type-system
identity; the adapter preserves `reference.externalTypeSystem`.

The three movement-area rules evaluate a conservative 2.00 m-high box. DIN 18040-1 clause 4.3.2 supplies the horizontal dimensions only; 2.00 m is an Axioval execution envelope, not a DIN threshold. It may over-report overhead obstructions but cannot create a false geometric pass.

## Structured provenance

- DIN 18040-1:2010-10 is declared in the ruleset source catalog. Horizontal
  movement dimensions cite clause 4.3.2 at the exact parameters.
- The 0.90 m clear door width cites clause 4.3.3.2, Table 1, row 1. The former
  informal `4.6` tag was incorrect and has been removed.
- Each 2.00 m evaluation height cites the Axioval example project profile, not
  DIN. The accessible-door property convention is project-profile provenance.
- IFC object mappings cite the release provenance from `openbim.ifc@0.2.1` and
  lower its typed IFC4 entity references through the pinned MCS adapter.
- `Pset_DoorCommon` and `HandicapAccessible` remain explicit authored template
  names because `openbim.ifc@0.2.1` deliberately does not bundle PSD/QTO
  occurrences. They must not be presented as package-validated references.

Citations are declarative provenance only. They neither execute checks nor
assert legal force, statutory applicability, conformance, or compliance.
Normative wording is not reproduced.

## Deutsch

Die horizontalen Bewegungsmaße verweisen parameterbezogen auf Abschnitt 4.3.2.
Die lichte Türbreite verweist auf Abschnitt 4.3.3.2, Tabelle 1, Zeile 1. Die
Prüfhöhe von 2,00 m und die IFC-Modellierungskonventionen stammen dagegen aus
dem bearbeitbaren Axioval-Beispielprofil. Zitate sind reine Herkunftsangaben;
sie führen keine Prüfung aus und begründen keine Rechts- oder Normkonformität.
