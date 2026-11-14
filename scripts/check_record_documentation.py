#!/usr/bin/env python3
"""Gate 5: record documentation standard.

Validates every canonical record against the machine-checkable subset of
docs/RECORD-STANDARD.md. Until records exist, exits clean.
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
RECORD_GLOB = "entities/v1-alpha/**/*.yaml"

REQUIRED_SECTIONS = (
    "## Identity",
    "## Evidence",
    "## Classification-or-relationships",
    "## Provenance",
    "## Governance",
)
KNOWN_SOURCE_KINDS = {"repository-path", "system-of-record", "published-document"}


def check_record(path: Path) -> list[str]:
    findings: list[str] = []
    rel = path.relative_to(REPO)
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    description = str(doc.get("description") or "").strip()
    if len(description) < 40:
        findings.append(f"{rel}: description is too thin to satisfy the standard (>= 40 chars)")

    evidence = doc.get("evidence") or {}
    rationale = str(evidence.get("rationale") or "").strip()
    if len(rationale) < 20:
        findings.append(f"{rel}: evidence.rationale is too thin (>= 20 chars)")
    sources = evidence.get("sources") or []
    if not sources:
        findings.append(f"{rel}: no evidence sources")
    for s in sources:
        if s.get("kind") not in KNOWN_SOURCE_KINDS:
            findings.append(f"{rel}: evidence source kind {s.get('kind')!r} is not known")

    rels = doc.get("relationships") or []

    readme = path.parent / "README.md"
    if not readme.exists():
        findings.append(f"{rel}: per-record README.md is missing")
        return findings

    text = readme.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            findings.append(f"{readme.relative_to(REPO)}: missing section {section!r}")

    blockquotes = [ln[2:].strip() for ln in text.splitlines() if ln.startswith("> ")]
    if not blockquotes:
        findings.append(f"{readme.relative_to(REPO)}: no definition blockquote")
    elif blockquotes[0] != description:
        findings.append(f"{readme.relative_to(REPO)}: definition blockquote does not match record description verbatim")

    if not rels:
        relsec = text.split("## Classification-or-relationships", 1)[-1]
        if "Deferred:" not in relsec:
            findings.append(f"{rel}: no relationship instances and no explicit deferral in README")

    return findings


def main() -> int:
    records = sorted(glob.glob(str(REPO / RECORD_GLOB), recursive=True))
    records = [Path(r) for r in records if "/research/" not in r and "/retired/" not in r]
    print(f"Record count: {len(records)}")

    findings: list[str] = []
    for path in records:
        findings.extend(check_record(path))

    if findings:
        for f in findings:
            print(f"FAIL: {f}")
        print(f"Findings: {len(findings)}")
        return 1

    print("OK: documentation standard satisfied" + (f" ({len(records)} records)" if records else " (no records yet)"))
    print("Findings: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
