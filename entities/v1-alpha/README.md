# v1-alpha Skill catalog entries

This directory holds the authoritative `v1-alpha` Skill catalog records for
dea-catalog-skills.

**Layout: CR-MET-024 shard form** (org-wide entity-storage-layout spec,
`dea-metaframework/docs/entity-storage-layout.md` S4): GitHub truncates a
directory listing at 1,000 entries, the shard trigger is 800, and the remedy
shards on the first character of the record slug. Every record lands at

```
entities/v1-alpha/<shard>/<id>/<id>.yaml      e.g.
entities/v1-alpha/0-9/skills:skill-5g-core-network/skills:skill-5g-core-network.yaml
```

with a per-record `README.md` (S2.3 README-per-folder rule) and a per-shard
`README.md`. The record path is derivable from the id alone (S5
path-integrity contract): shard = first character of the id with the
`skills:skill-` prefix removed (`0-9` fallback for digit-leading slugs).

## Shard map (CR-DEA-SKL-01 baseline: 735 records)

| Shard | Records |
|---|---|
| `0-9` | 2 |
| `a` | 47 |
| `b` | 12 |
| `c` | 101 |
| `d` | 30 |
| `e` | 38 |
| `f` | 41 |
| `g` | 14 |
| `h` | 13 |
| `i` | 41 |
| `k` | 2 |
| `l` | 30 |
| `m` | 56 |
| `n` | 24 |
| `o` | 20 |
| `p` | 83 |
| `q` | 8 |
| `r` | 36 |
| `s` | 61 |
| `t` | 52 |
| `u` | 2 |
| `v` | 8 |
| `w` | 14 |

Worst-case directory: shard `c` with 101 records
(102 directory entries incl. the shard README); permanently under the 800-entry
trigger; headroom to roughly 7,800 records at this distribution before a
second shard level is required.

## Governance

Records are candidates (`lifecycle_status: proposed`, provenance discovery /
manual, asserted_by catalog-seed, verification unverified) per CR-DEA-SKL-01.
Admission proceeds by CR with recurrence evidence (E1 -> E2 -> E3); the
materializer (`scripts/materialize_skills.py`) is bound to the admission
path and refuses overwrites. CI gates: `scripts/validate_ingestion.py`
(manifest sha256, row schema, uniqueness, edge accounting, layout census,
path integrity, schema validation).
