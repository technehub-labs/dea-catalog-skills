# Contributing to dea-catalog-skills

## Change control

Every change lands through a change request (CR) in `change-requests/`
carried by a pull request against `main`. CR format follows the house
pattern (metadata table, numbered sections, out-of-scope list, verifiable
acceptance criteria); every CR registers a row in `change-requests/README.md`.

## Workflow

1. Branch: `feat/CR-SKL-CAT-NN-short-title`.
2. Implement; regenerate the index when entity content changes.
3. Run the gates locally (README §Local validation). All must print `Findings: 0`.
4. Open a pull request; CI runs the same gates plus the allocation
   validator and the authorship gate.
5. Verify checks are green before merge.

## Authorship cardinal rule

Every authorship-bearing field carries `Emmanuel A. Otchere` or
`TechNeHub Labs` — never an agent or tool name (AUT-001..003 gate).

## Pointer and index discipline

`metamodel-pointer.yaml` allocation changes go through the root model.
`CATALOG.yaml` is machine-generated; regenerate, never hand-edit.
