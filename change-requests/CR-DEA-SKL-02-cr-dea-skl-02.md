# CR-DEA-SKL-02: Skills<->Roles Interlock Completion (7 Missing Skills)

**Status**: Landed (this PR)
**Layer**: Catalog content (interlock completion)
**Owner**: Emmanuel A. Otchere
**Date**: 2026-11-16
**Admission authority**: yes (bounded admission of the exact interlock gap, materialized through the CR-DEA-SKL-01 pipeline)
**Trigger**: The roles<->skills interlock: the roles catalog's 1,252 records reference **742** distinct `skills:skill-*` ids; the skills catalogue published only the 735 the build pipeline resolved (718 batch-referenced + 17 seed). 7 referenced skills had no record — every role→skill edge pointing at them was pending. Actors and stakeholders carry no direct skill references (roles is the consumer). This CR closes the gap to 742/742.
**Carrier**: Single PR on feature branch `feat/cr-skl-cat-02`. PR review, not direct push.
**Lands against**: `main`
**Depends on**: CR-DEA-SKL-01 (bulk ingestion pipeline); the roles catalogue's skill references (the citing records ARE the evidence).

## 1. What this CR admits

**7 Skill records** — the exact interlock gap (roles references them; no record existed):

| Skill | Citing roles records (evidence) | Industries |
|---|---|---|
| skills:skill-credit-risk-management | roles:role-credit-risk-manager | banking |
| skills:skill-data-protection | roles:role-data-protection-privacy-compliance-officer (+2) | legal-regulatory, mining, public-sector, technology |
| skills:skill-experience-management | roles:role-patient-experience-manager | health, public-sector |
| skills:skill-policy-analysis | roles:role-policy-analyst | public-sector |
| skills:skill-procurement-management | roles:role-procurement-manager | manufacturing, public-sector |
| skills:skill-public-finance-management | roles:role-public-finance-manager | public-sector |
| skills:skill-service-design | roles:role-service-designer | consulting, entertainment, healthcare, public-sector, technology |

Provenance per record: discovery, asserted_by catalog-seed, verification_status unverified (the file's standing convention), provenance_reference = the citing roles record — **the abstraction's link to its evidence is the citing roles record itself** (repository-verifiable). Records are candidates (`lifecycle_status: proposed`, v0.1.0) per the admission model; canonical promotion follows the standing evidence-gated step.

## 2. Pipeline changes (recorded, per the interlock)

1. **CSV renamed + extended**: `ingestion/bulk-735-skills.csv` → `ingestion/bulk-742-skills.csv` (+7 rows in the exact build format; manifest sha256 updated).
2. **Slice registry extended**: `scripts/validate_ingestion.py` SLICE_IDS += `banking`, `health`, `public-sector` — the roles-taxonomy facets the interlock introduces (the citing roles records carry these industries; the build's 12 slices didn't include them). Manifest per_slice updated.
3. `scripts/_catalog.py` CSV path constant updated for the rename.
4. Manifest edges accounting updated: batch_required_by 12023 → 12032, resolvable_now 2473 (unchanged — no new role admissions), pending 9550 → 9559... and after this admission the 9 citing edges become resolvable at the role side on the roles' next admission pass.

## 3. Verification

- `validate_ingestion.py`: 742 rows OK; 742 records materialized; census max dir 103 (< 800).
- `materialize_skills.py --ids` (the 7): wrote the 7 records + READMEs at the sharded layout; existing-instances-win rule respected (0 skipped collisions).
- CATALOG.yaml (bespoke index): 742 listed == 742 records; entities counter updated.
- Roles interlock check: 742/742 distinct `skills:skill-*` references in dea-catalog-roles now resolve against published ids.

## 4. NOT-List

- NOT a canonical admission: records stay `proposed` v0.1.0 (candidates); the evidence-gated canonical step follows the standing model.
- NOT a change to the materialize/validate semantics beyond the slice-registry extension the interlock requires.
- NOT a change on the roles side: role records' references were already correct; the skills side now satisfies them.
- No actor/stakeholder changes (they carry no direct skill references).
