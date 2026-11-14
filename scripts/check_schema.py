#!/usr/bin/env python3
"""Gate 4: the catalogue schema is a faithful projection of the metamodel
schema, and every record validates against it.

Expected values are embedded from dea-metamodel v1.0.0 by the kit
generator; bump them in the same CR that bumps metamodel_pin in
dependencies.yaml. Never widen a normative enum locally.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator
from referencing import Registry, Resource

REPO = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO / "schemas" / "entity.schema.json"
REL_SCHEMA_PATH = REPO / "schemas" / "relationship-instance.schema.json"
REL_SCHEMA_URI = f"https://technehub-labs.github.io/dea-catalog-skills/schemas/relationship-instance.schema.json"
FIXTURE_VALID = REPO / "schemas" / "fixtures" / "example-valid.yaml"
FIXTURE_INVALID = REPO / "schemas" / "fixtures" / "example-invalid.yaml"
RECORD_GLOB = "entities/v1-alpha/**/*.yaml"

EXPECTED_TYPE_CONST = "Skill"
EXPECTED_LIFECYCLE_ENUM = ["proposed", "planned", "active", "deprecated", "retired"]
EXPECTED_REQUIRED = ["id", "type", "name", "version", "lifecycle_status"]
EXPECTED_ID_PATTERN = "^dea:skill-[a-z0-9-]+$"



def build_validator() -> Draft7Validator:
    schema = json.load(SCHEMA_PATH.open(encoding="utf-8"))
    rel_schema = json.load(REL_SCHEMA_PATH.open(encoding="utf-8"))
    registry = Registry().with_resource(REL_SCHEMA_URI, Resource.from_contents(rel_schema))
    return Draft7Validator(schema, registry=registry)


def check_projection() -> list[str]:
    if not SCHEMA_PATH.exists():
        return ["entity.schema.json is missing"]
    schema = json.load(SCHEMA_PATH.open(encoding="utf-8"))
    props = schema.get("properties") or {}
    findings: list[str] = []
    if schema.get("type") != "object":
        findings.append("type is not object")
    if schema.get("additionalProperties") is not False:
        findings.append("additionalProperties is not false")
    if schema.get("required") != EXPECTED_REQUIRED:
        findings.append(f"required is {schema.get('required')!r}")
    if props.get("type", {}).get("const") != EXPECTED_TYPE_CONST:
        findings.append("type const mismatch")
    if props.get("lifecycle_status", {}).get("enum") != EXPECTED_LIFECYCLE_ENUM:
        findings.append("lifecycle_status enum mismatch")
    if props.get("id", {}).get("pattern") != EXPECTED_ID_PATTERN:
        findings.append("id pattern mismatch")
    for field, expected in {}.items():
        got = (props.get(field) or {}).get("enum")
        if got != expected:
            findings.append(f"{field} enum drift")
    rel = props.get("relationships")
    if not rel or "$ref" not in (rel.get("items") or {}):
        findings.append("relationships items must $ref relationship-instance.schema.json")
    return findings


def main() -> int:
    findings = check_projection()
    if findings:
        for f in findings:
            print(f"FAIL: {f}")
        print(f"Findings: {len(findings)}")
        return 1

    validator = build_validator()

    if FIXTURE_VALID.exists():
        doc = yaml.safe_load(FIXTURE_VALID.read_text(encoding="utf-8"))
        errs = sorted(validator.iter_errors(doc), key=str)
        if errs:
            findings.append("valid fixture does not validate: " + "; ".join(e.message for e in errs[:3]))
    else:
        findings.append("valid fixture is missing")

    if FIXTURE_INVALID.exists():
        doc = yaml.safe_load(FIXTURE_INVALID.read_text(encoding="utf-8"))
        errs = sorted(validator.iter_errors(doc), key=str)
        if not errs:
            findings.append("invalid fixture validates (it must not)")
    else:
        findings.append("invalid fixture is missing")

    records = sorted(glob.glob(str(REPO / RECORD_GLOB), recursive=True))
    records = [r for r in records if "/research/" not in r and "/retired/" not in r]
    for f in records:
        doc = yaml.safe_load(open(f, encoding="utf-8")) or {}
        errs = sorted(validator.iter_errors(doc), key=str)
        if errs:
            findings.append(f"{Path(f).relative_to(REPO)}: " + "; ".join(e.message for e in errs[:3]))

    if findings:
        for f in findings:
            print(f"FAIL: {f}")
        print(f"Findings: {len(findings)}")
        return 1

    print(f"OK: projection faithful; {len(records)} record(s) validate; fixtures behave")
    print("Findings: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
