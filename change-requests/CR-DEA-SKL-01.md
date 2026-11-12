# CR-DEA-SKL-01: Bulk Skill Ingestion Pipeline (v1-alpha)

| Field | Value |
|---|---|
| CR id | CR-DEA-SKL-01 |
| Owner | Emmanuel A. Otchere |
| Author | Emmanuel A. Otchere |
| Status | Proposed |
| Date | 2026-11-12 |
| Scope | dea-catalog-skills (schemas, ingestion, scripts, entities, industries, CATALOG.yaml, dependencies.yaml) |
| Metamodel | dea-metamodel v0.3.0 (`dea:entity-skill`) |
| Related | CR-DEA-ROL-05 (roles ingestion), CR-DEA-ROL-24 (roles companion: sharded layout), CR-MET-024 (entity storage layout), CR-2 S7/S8 (edge direction) |

## Objective

Establish the dea-catalog-skills ingestion pipeline: entity schemas vendored
verbatim from dea-metamodel v0.3.0, a 735-row candidate batch derived from the
SKL -> ROL "required by" demand asserted by the dea-catalog-roles 6000-role
ingestion batch (CR-DEA-ROL-05), the org-wide CR-MET-024 sharded entity layout,
gate-based validation, and a bounded admission path that materializes records.

## Background

The roles catalog admits roles via CR from the 6000-role batch; its role
records assert `requires` edges to `skills:` ids (canonical direction,
source role -> target skill, per CR-2 S7/S8). 718 distinct skills are
referenced by that batch; 17 further capabilities are asserted by seed roles.
This batch materializes those 735 candidates as Skill entities so role-side
references resolve. Demand evidence travels in `metadata` (not stored
relationships): `required_by.batch_roles`, `required_by.admitted_roles`
(1225 roles admitted to date) and `required_by.example_role`.

## Deliverables

| Artifact | Path | Notes |
|---|---|---|
| Skill schema (vendored) | `schemas/skill.schema.json` | dea-metamodel@0831aaf9d06f29ed3ba0e459fc685c726859e0c `schemas/entities/skill.json`, verbatim |
| Entity schema (vendored) | `schemas/entity.json` | free-form `metadata` envelope |
| Relationship instance schema (vendored) | `schemas/relationships/relationship-instance.json` | enum includes `requires`; there is no `required-by` (inverse views are generated, CR-2 S8) |
| Bulk batch | `ingestion/bulk-735-skills.csv` | 735 rows, 20 columns; ids byte-identical to the roles batch's `skills:` references |
| Manifest | `ingestion/manifest.yaml` | sha256, kind counts, edge accounting, layout rule |
| Gate script | `scripts/validate_ingestion.py` | 6 gates (below) |
| Materializer | `scripts/materialize_skills.py` | admission-bound, refuses overwrites, idempotent-skip |
| Catalog helpers | `scripts/_catalog.py` | `shard_for_id` / `record_relpath` (CR-MET-024; mirrors dea-catalog-metrics) |
| Entity records | `entities/v1-alpha/<shard>/<id>/<id>.yaml` | 735 candidate records + per-record README |
| Shard READMEs | `entities/v1-alpha/<shard>/README.md` | per-shard census vs the 800 trigger |
| CATALOG.yaml | `CATALOG.yaml` | 735 entries, id-derived sharded paths |
| dependencies.yaml | `dependencies.yaml` | SKL -> ROL "required by" model relationship, partially-resolvable |
| Industry registers | `industries/<facet>.yaml` | 12 facets + `seed-capabilities.yaml` |

## Layout (CR-MET-024)

GitHub truncates a directory listing at 1,000 entries; the org-wide shard
trigger is 800 tracked entries (CST-017). This catalog is therefore created
directly in the shard form (never a flat 735-file directory):

```
entities/v1-alpha/<shard>/<id>/<id>.yaml
entities/v1-alpha/0-9/skills:skill-5g-core-network/skills:skill-5g-core-network.yaml
```

Shard = first character of the record slug (`skills:skill-` prefix removed);
digit-leading slugs shard to `0-9`. Record ids are byte-identical to the
ingestion batch; the record path is derivable from the id alone
(entity-storage-layout.md S5). Worst shard at this baseline: `c` (101 records,
203 tracked entries); headroom to roughly 7,800 records at this distribution.

## Gate semantics (scripts/validate_ingestion.py)

1. **Manifest integrity** - CSV sha256, row count, kind counts vs manifest.
2. **Row schema** - id pattern `^skills:skill-[a-z0-9][a-z0-9-]*$`, type const
   `Skill`, name <= 200, description <= 2000, semver 0.1.0, `proposed` only,
   registered industry facets, integer counts, provenance enums, edge label.
3. **Uniqueness** - 735 unique ids.
4. **Edge accounting** - batch/resolvable/pending (12023 / 2473 / 9550).
5. **Layout census** - no directory at or above the 800-entry trigger; R5
   review WARN at 500+.
6. **Path integrity + schema** - every materialized record exists at its
   id-derived path, is a batch row, and validates against
   `schemas/skill.schema.json` (jsonschema in CI; registry-aware $refs).

## Admission path

Rows are candidates only (`lifecycle_status: proposed`, `version: 0.1.0`,
provenance discovery/manual, asserted by catalog-seed, unverified). Admission
proceeds by CR with recurrence evidence, mirroring the roles model
(CR-DEA-ROL-05 S4): `materialize_skills.py --ids ...` or
`--industry <facet> --limit N` materializes admitted rows at their shard
paths. Existing records win on id collision (the tool refuses overwrites);
CATALOG.yaml entries follow admission; lifecycle promotion to `active`
requires recurrence evidence across admitted roles (E1 -> E2 -> E3).

## Cross-catalog contract

Stored instance edges live on the role side (`relationship_type: requires`).
The generated inverse (SKL required-by ROL) is never stored (CR-2 S7/S8);
`dependencies.yaml` declares the model relationship only. Role-side
`skills:` references must resolve against this catalog's published ids; the
roles repo's `check_cross_catalog_refs.py` must probe id-derived shard paths
(companion change CR-DEA-ROL-24).

## Verification

```
python scripts/validate_ingestion.py
python scripts/materialize_skills.py --ids skills:skill-5g-core-network  # skip: exists
git ls-files entities/v1-alpha | wc -l   # 1470 yaml+md record files + shard READMEs
```

## References

- dea-metaframework `docs/entity-storage-layout.md` v1.2.0 (CR-MET-024)
- dea-catalog-metrics `scripts/_catalog.py` (reference shard implementation)
- technehub-labs/dea-catalog-roles: CR-DEA-ROL-05, CR-DEA-ROL-24
- dea-metamodel v0.3.0: `schemas/entities/skill.json`, CR-2 S7/S8
