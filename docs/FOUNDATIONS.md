# Foundations: Skill Catalog

This document records the method the catalogue follows: cardinal scope,
exclusions, admission criteria, allocation, cross-catalogue policy, and the
decision register. The record documentation standard
([RECORD-STANDARD.md](RECORD-STANDARD.md)) and the schema projection carry
the operational contract.

## 1. Cardinal scope

**Skill** — A capability an individual Actor possesses or must develop. Distinct from Business Capability, which belongs to the enterprise, not a person.

## 2. What is deliberately excluded

Boundaries against sibling entity types are governed by the metamodel
definitions; anything that is not a skill record
belongs to its owning catalogue (see the metamodel's `catalog_repo`
allocations).

## 3. Admission criteria and evidence ladder

1. The record describes a skill per the metamodel definition.
2. At least one evidence source verifiably exists at admission time
   (`repository-path`, `system-of-record`, or `published-document`).
3. Relationship instances are asserted only against canonical target ids
   that exist; absence is honest (no local substitutes).

Evidence ladder (asserted in `provenance.ladder_passage`):
candidate → corroborated → reviewed → canonical.

## 4. Allocation

`dea:entity-skill` (alias `SKL`), layer L3 / L3-people-skills-culture, pinned against
OpenDEAM v0.8.0. Validated remotely by `validate-allocation.yml`
and locally by Gate 2. Upstream pins live in `dependencies.yaml`.

## 5. Cross-catalogue reference policy

1. Crosswalks and references are recorded on the asserting record's side,
   as typed relationship instances (metamodel relationship-instance
   contract).
2. Assertions wait for canonical targets: no scheme invention where a
   sibling id scheme does not exist.
3. Gates never resolve remote repositories; vendored registry snapshots
   carry the offline contract where a specific target family is asserted.

## 6. Decision-points register

| # | Decision | Status |
|---|---|---|
| D-1 | Methodology-first bring-up: no records before the kit and population CR | Adopted (CR-SKL-CAT-01) |
| D-2 | Hybrid pointer: identity keys for the regenerator + `metamodel:` allocation block for the root-model validator | Adopted (CR-SKL-CAT-01) |
| D-3 | Record ids take the `dea:skill-<slug>` form (information-classes `dea:`-prefix precedent) | Adopted (CR-SKL-CAT-01) |
| D-4 | Admission ladder: candidate → corroborated → reviewed → canonical | Adopted (CR-SKL-CAT-01) |
| D-5 | Evidence-only admission: no record without a verifiable source; population plans document the wait | Adopted (CR-SKL-CAT-01) |
| D-6 | `CATALOG.yaml` is committed, not ignored (template deviation): the freshness gate diffs the committed index | Adopted (CR-SKL-CAT-01) |

## 7. Population plan

Initial population is evidence-gated. Candidate seed sources are named in
the population CR; where none are verifiable today, the catalogue stays at
zero canonical records with this section recording why and what would
unlock population.
