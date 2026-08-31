# Accessibility / Barrierefreiheit

Bilingual DIN 18040-1 focused templates and concrete rules for movement areas, encounters, turning, straight route segments, and accessible openings.

## Model prerequisites

Assign the documented classification codes to the spaces, route segments, and doors for which each use case is expected. This is deliberate: IFC geometry alone cannot prove whether encounters or changes of direction are expected.

Applications must provide exact free-space, route, and opening evidence. Missing geometry, incomplete obstacle coverage, or unsupported capabilities are **not evaluated**, never passed.

The three movement-area rules evaluate a conservative 2.00 m-high box. DIN 18040-1 clause 4.3.2 supplies the horizontal dimensions only; 2.00 m is an Axioval execution envelope, not a DIN threshold. It may over-report overhead obstructions but cannot create a false geometric pass.

## Sources

- [DIN 18040-1:2010-10](https://www.dinmedia.de/en/standard/din-18040-1/133692028), especially clauses 4.3.2 and 4.6. Thresholds are encoded as parameters; normative wording is not reproduced.
- [buildingSMART IFC 4 ADD2 TC1](https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/) PSD/QTO catalog for IFC object and property identities.

## Deutsch

Die Regeln unterscheiden Begegnung, Richtungswechsel, geradlinige Wege und Türöffnungen über explizite Klassifikationen. Fehlende oder unvollständige Geometrie darf nicht als bestandene Prüfung gewertet werden.
