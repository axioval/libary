# Fire safety / Brandschutz

Bilingual fire-safety templates and concrete coordination rules for compartment boundaries, rated doors, protected penetrations, and escape routes.

## Scope

The package checks model evidence and coordination invariants. It is not a complete building-code ruleset. Building class, occupancy, state building regulations, special-building regulations, and an approved fire-safety concept remain project inputs.

The included 1.20 m × 2.00 m escape-route envelope is an **example project policy** selected by an explicit classification code. Replace it where the applicable regulation or fire-safety concept requires another value.

## Structured provenance

- Every coordination rule cites the document-owned Axioval example
  `projectPolicy` source. The 1.20 m × 2.00 m envelope is cited at its exact
  width and height parameters.
- IFC object, property, and property-set mappings cite the document-owned
  buildingSMART IFC4 ADD2 TC1 source in `definitions.pkl`.
- Replace the example policy source and values with the approved project
  fire-safety concept and applicable requirements before project use.

The citations record provenance only. They do not turn the package into a
building-code ruleset and do not assert regulatory compliance.

## Deutsch

Jede Koordinationsregel verweist auf die bearbeitbare beispielhafte
Projektvorgabe. Die Fluchtwegbreite und -höhe sind ihren Parametern direkt
zugeordnet. IFC-Zuordnungen verweisen in `definitions.pkl` auf buildingSMART.
Diese Herkunftsangaben ersetzen weder Brandschutzkonzept noch Rechtsprüfung und
begründen keine Konformitätsaussage.
