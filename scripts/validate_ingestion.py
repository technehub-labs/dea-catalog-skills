#!/usr/bin/env python3
"""Validate the bulk skills ingestion batch against its manifest.

Gates (mirrors dea-catalog-roles scripts/validate_ingestion.py, CR-DEA-ROL-05 S3):
  1. manifest integrity: CSV sha256, row count, kind counts;
  2. row schema: id pattern, type const, name/description limits, semver,
     proposed-only lifecycle, registered slice ids, provenance enums;
  3. uniqueness: 735 unique ids;
  4. edge accounting: batch/resolvable/pending counts vs the manifest;
  5. layout census: every directory under the CR-MET-024 shard trigger (800);
  6. path integrity: each materialized record exists at its id-derived path
     (entity-storage-layout.md S5) and validates against the vendored schema.

Exit non-zero on the first gate that fails.
"""
import collections
import csv
import hashlib
import json
import pathlib
import re
import sys

try:
    import yaml
    _HAVE_YAML = True
except ImportError:
    _HAVE_YAML = False

try:
    from jsonschema import Draft7Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT7
except ImportError:
    Draft7Validator = None

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _catalog  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
ID_RE = re.compile(r"^skills:skill-[a-z0-9][a-z0-9-]*$")
SLICE_IDS = {
    "telecom", "technology", "entertainment", "media", "finance", "mining",
    "transport", "manufacturing", "healthcare", "audit", "legal-regulatory",
    "consulting",
}
KINDS = {"domain-capability", "domain-operations", "seed-capability"}
PROV_TYPES = {"discovery", "manual"}
SHARD_TRIGGER = 800  # entity-storage-layout.md S4 / CST-017


def fail(msg):
    print(f"FAIL {msg}")


def build_validator():
    if Draft7Validator is None:
        return None
    resources = []
    for p in (ROOT / "schemas").rglob("*.json"):
        contents = json.loads(p.read_text())
        resources.append((contents.get("$id", p.name),
                           Resource.from_contents(contents, default_specification=DRAFT7)))
    registry = Registry().with_resources(resources)
    skill_schema = json.loads(_catalog.SCHEMA_PATH.read_text())
    return Draft7Validator(skill_schema, registry=registry)


def main():
    if not _HAVE_YAML:
        sys.exit("PyYAML required: pip install pyyaml")
    manifest = yaml.safe_load(_catalog.MANIFEST.read_text())

    # gate 1: manifest integrity
    data = _catalog.INGESTION_CSV.read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
        fail("CSV sha256 does not match the manifest (silent edit?)")
        return 1
    with open(_catalog.INGESTION_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != manifest["rows"]:
        fail(f"row count {len(rows)} != manifest {manifest['rows']}")
        return 1
    kinds = collections.Counter(r["skill_kind"] for r in rows)
    if dict(kinds) != manifest["kinds"]:
        fail(f"kind counts {dict(kinds)} != manifest {manifest['kinds']}")
        return 1

    # gate 2: row schema
    problems = []
    for r in rows:
        rid = r["id"]
        if not ID_RE.match(rid):
            problems.append(f"{rid}: id pattern")
        if r["type"] != "Skill":
            problems.append(f"{rid}: type const")
        if not (1 <= len(r["name"]) <= 200):
            problems.append(f"{rid}: name length")
        if len(r["description"]) > 2000:
            problems.append(f"{rid}: description length")
        if r["version"] != "0.1.0":
            problems.append(f"{rid}: version")
        if r["lifecycle_status"] != "proposed":
            problems.append(f"{rid}: lifecycle must be proposed")
        if r["skill_kind"] not in KINDS:
            problems.append(f"{rid}: skill_kind")
        facets = [x for x in r["industries"].split(";") if x]
        if r["skill_kind"] == "seed-capability":
            if any(x not in SLICE_IDS | {"general"} for x in facets):
                problems.append(f"{rid}: industry facet")
        elif not facets or facets[0] not in SLICE_IDS:
            problems.append(f"{rid}: primary slice not registered")
        for col in ("required_by_count", "admitted_required_by_count"):
            if not r[col].isdigit():
                problems.append(f"{rid}: {col} not an integer")
        if int(r["admitted_required_by_count"]) > int(r["required_by_count"]):
            problems.append(f"{rid}: admitted requirers exceed batch requirers")
        if r["provenance_type"] not in PROV_TYPES:
            problems.append(f"{rid}: provenance type")
        if r["provenance_verification_status"] != "unverified":
            problems.append(f"{rid}: verification status")
        if r["relationship_type"] != "required_by":
            problems.append(f"{rid}: demand edge label")
    if problems:
        for p in problems[:20]:
            fail(p)
        return 1

    # gate 3: uniqueness
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        fail("duplicate ids in batch")
        return 1

    # gate 4: edge accounting
    batch_edges = sum(int(r["required_by_count"]) for r in rows)
    resolvable = sum(int(r["admitted_required_by_count"]) for r in rows)
    exp = manifest["edges"]
    if (batch_edges, resolvable, batch_edges - resolvable) != (
            exp["batch_required_by"], exp["resolvable_now"], exp["pending"]):
        fail(f"edge accounting mismatch: {batch_edges}/{resolvable}/{batch_edges - resolvable}")
        return 1

    # gate 5: layout census
    for d, c in sorted(_catalog.census().items()):
        if 500 <= c < SHARD_TRIGGER:
            print(f"WARN {d}: {c} tracked entries (R5 review band, 500+)")
    over = [f"{d}: {c}" for d, c in _catalog.census().items() if c >= SHARD_TRIGGER]
    if over:
        for o in over:
            fail(f"CST-017 shard trigger breach: {o}")
        return 1

    # gate 6: path integrity + schema
    validator = build_validator()
    materialized = list(_catalog.iter_record_yaml_paths())
    csv_ids = {r["id"] for r in rows}
    for rec in _catalog.load_skills():
        if rec["id"] not in csv_ids:
            fail(f"materialized record {rec['id']} is not a batch row")
            return 1
        expected = ROOT / _catalog.record_relpath(rec["id"])
        if not expected.is_file():
            fail(f"path integrity: {rec['id']} not at {expected}")
            return 1
        if validator is not None:
            errs = sorted(validator.iter_errors(rec), key=lambda e: list(e.absolute_path))
            for err in errs:
                loc = ".".join(str(x) for x in err.absolute_path) or "<root>"
                fail(f"{rec['id']} [{loc}]: {err.message}")
            if errs:
                return 1

    print(f"validate_ingestion: {len(rows)} rows OK; {len(materialized)} records materialized; "
          f"census max dir {max(_catalog.census().values(), default=0)} (< {SHARD_TRIGGER})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
