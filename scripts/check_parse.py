#!/usr/bin/env python3
"""Gate 1: every tracked YAML and JSON file must parse.

Runs the whole tree, not just entities: the catalogue's pointer, schema,
and documentation must parse even before records exist, and a record that
lands with malformed YAML should fail here rather than downstream.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    bad = 0
    checked = 0

    for pattern in ("**/*.yaml", "**/*.yml"):
        for f in glob.glob(str(REPO / pattern), recursive=True):
            if "/.git/" in f:
                continue
            checked += 1
            try:
                yaml.safe_load(open(f, encoding="utf-8"))
            except Exception as exc:
                print(f"FAIL: {Path(f).relative_to(REPO)} does not parse as YAML: {exc}")
                bad += 1

    for f in glob.glob(str(REPO / "**/*.json"), recursive=True):
        if "/.git/" in f:
            continue
        checked += 1
        try:
            json.load(open(f, encoding="utf-8"))
        except Exception as exc:
            print(f"FAIL: {Path(f).relative_to(REPO)} does not parse as JSON: {exc}")
            bad += 1

    print(f"Files checked: {checked}")
    print(f"Findings: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
