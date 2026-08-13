# dea-catalog-skills

> DEA catalog for **Skill** — OpenDEAM v0.3.0 (ADR-0003).

## Skill (`SKL`)

- **Entity id:** `dea:entity-skill`
- **Allocation:** L3 · L3-people-skills-culture
- **Status:** proposed

A capability an individual Actor possesses or must develop. Distinct from Business Capability, which belongs to the enterprise, not a person.

## Relationships (from the OpenDEAM model)

- **SKL → ROL** — required by (dependency, 0..N:0..N)

## Allocation contract

This repo's `metamodel-pointer.yaml` is validated in CI against the pinned
OpenDEAM root model (`v0.3.0`) via the reusable
`validate-against-model.yml` workflow. Drift fails CI.

Content (entity instances) lands when the entity promotes from
`proposed` to `planned`/`scaffold` per the model lifecycle.

## License

Apache 2.0 — see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).
