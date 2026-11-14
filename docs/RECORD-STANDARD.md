# Record Documentation Standard (CR-SKL-CAT-01)

Every canonical Skill record must satisfy this standard. Gate 6
(`scripts/check_record_documentation.py`) enforces the machine-checkable
subset; steward review enforces the rest.

## 1. Record file

One record per subtree: `entities/v1-alpha/<id>/<id>.yaml`, where `<id>` is
the canonical id (`dea:skill-<slug>`). Obligations beyond the schema:

1. `name` is the real name as consumers know it.
2. `description` states what the record is and its consuming purpose — not
   a restatement of the name.
3. `evidence.sources` cites at least one verifiable source; `rationale`
   says why it justifies admission.
4. `provenance.ladder_passage` records passage to canonical with quoted
   dates and authorship-bearing actors (AUT rules).
5. Relationship instances are asserted only against canonical targets, or
   the README carries an explicit `Deferred:` note.

## 2. YAML conventions

- Dates single-quoted so they stay strings.
- Apostrophes escaped (`''`) in single-quoted prose; double quotes when the
  prose contains a colon.

## 3. Per-record README

Sections: `# <Name>` + verbatim definition blockquote, `## Identity`,
`## Evidence`, `## Classification-or-relationships`, `## Provenance`,
`## Governance`. The definition blockquote must equal the record's
`description` verbatim (Gate 6 checks).

## 4. Change discipline

Record changes land through CRs; a record edit regenerates `CATALOG.yaml`
in the same PR. Retired records move to `retired/`, never deleted.
