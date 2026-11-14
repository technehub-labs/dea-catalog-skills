#!/usr/bin/env python3
"""Gate 3: records-directory posture.

Records may not appear before the schema and documentation gates exist;
every record that lands carries the canonical identifier form and type.
Population is gated on the population CR (CR-SKL-CAT-02+).
"""

from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
RECORD_GLOB = "entities/v1-alpha/**/*.yaml"

REQUIRED_POPULATION_GATES = (
    "scripts/check_schema.py",
    "scripts/check_record_documentation.py",
)

CANONICAL_ID = re.compile(r"dea:skill-[a-z0-9-]+")


def main() -> int:
    records = sorted(glob.glob(str(REPO / RECORD_GLOB), recursive=True))
    records = [r for r in records if "/research/" not in r and "/retired/" not in r]
    print(f"Record count: {len(records)}")

    if not records:
        print("  OK: no records admitted; population is gated on the population CR")
        print("Findings: 0")
        return 0

    missing = [g for g in REQUIRED_POPULATION_GATES if not (REPO / g).exists()]
    if missing:
        print("Records are present but the population gates are incomplete:")
        for g in missing:
            print(f"  - FAIL: {g} is missing")
        print(f"Findings: {len(missing)}")
        return 1

    findings: list[str] = []
    for f in records:
        doc = yaml.safe_load(open(f, encoding="utf-8")) or {}
        rid = doc.get("id") or ""
        if not CANONICAL_ID.fullmatch(rid):
            findings.append(f"{Path(f).relative_to(REPO)}: id {rid!r} is not a canonical Skill id")
        rtype = doc.get("type") or ""
        if rtype != "Skill":
            findings.append(f"{Path(f).relative_to(REPO)}: type {rtype!r} is not 'Skill'")

    if findings:
        print("Posture findings:")
        for f in findings:
            print(f"  - FAIL: {f}")
        print(f"Findings: {len(findings)}")
        return 1

    print(f"  OK: {len(records)} record(s) carry canonical identifiers and type")
    print("Findings: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
