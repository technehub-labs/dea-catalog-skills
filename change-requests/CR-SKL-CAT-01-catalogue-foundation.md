# CR-SKL-CAT-01: Skill Catalogue Foundation

| Field | Value |
|---|---|
| **CR** | CR-SKL-CAT-01 |
| **Title** | Skill catalogue foundation (kit bring-up) |
| **Status** | Landed |
| **Layer** | Catalogue (L3) |
| **Programme** | Org-wide catalog advancement |
| **Repository** | `technehub-labs/dea-catalog-skills` |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-11-02 |
| **Depends on** | dea-metaframework catalog-kit generator CR |
| **Trigger** | Org-wide catalog advancement programme: advance this repository from initial state to the reputable-foundation standard with initial entities to follow under evidence-only admission. |

## 1. Executive summary

This CR lands the standard catalogue kit (the CR-IA-CAT-01..03 standard,
machine-generated): hybrid pointer pinned to OpenDEAM v0.8.0,
dependency manifest, schema projection (copied-and-narrowed) with the
catalogue-instance layer, vendored relationship-instance contract, fixtures,
gates 1-6, three CI workflows, FOUNDATIONS with the decision register, the
record documentation standard, README contract, and CONTRIBUTING. No
records are admitted; population is evidence-gated (CR-SKL-CAT-02).

## 2. Scope

In scope: everything under `metamodel-pointer.yaml`, `dependencies.yaml`,
`schemas/`, `scripts/`, `docs/`, `.github/workflows/`, `README.md`,
`CONTRIBUTING.md`, `CHANGELOG.md`, this CR and the register. The template
`ci.yml` is superseded by the three named workflows. `CATALOG.yaml` is
committed (template `.gitignore` deviation, D-6).

Out of scope: record population; metamodel changes; sibling catalogues.

## 3. Acceptance criteria

1. All six local gates print `Findings: 0`.
2. `validate-against-model` passes against OpenDEAM v0.8.0.
3. Authorship gate conformant.
4. `CATALOG.yaml` regenerated and committed (0 entities).

## 4. NOT-list

1. No records admitted.
2. No vocabulary widened beyond the metamodel.
3. No remote resolution in any gate.
