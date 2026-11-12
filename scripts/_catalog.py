"""Shared catalog loading for the skills gate scripts (CR-DEA-SKL-01).

Mirrors dea-catalog-metrics scripts/_catalog.py (CR-MET-016). The layout is
the org-wide CR-MET-024 shard form
(dea-metaframework/docs/entity-storage-layout.md S4):
entities/v1-alpha/<shard>/<id>/<id>.yaml.
"""
from __future__ import annotations

import collections
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).parent.parent
ENTITIES_DIR = BASE / "entities"
ENTITIES_ROOT = ENTITIES_DIR / "v1-alpha"
SCHEMA_PATH = BASE / "schemas" / "skill.schema.json"
INGESTION_CSV = BASE / "ingestion" / "bulk-735-skills.csv"
MANIFEST = BASE / "ingestion" / "manifest.yaml"

ID_PREFIX = "skills:skill-"


def shard_for_id(skill_id: str) -> str:
    """The CR-MET-024 shard directory for a skill id.

    The slug is the id with the `skills:skill-` prefix removed. Lowercase
    ASCII letters shard to a single-letter directory; every other
    character (digit-leading slugs) shards to the `0-9` bucket. This is
    the only layout rule: the record path must stay derivable from the
    id alone (entity-storage-layout.md S5).
    """
    slug = skill_id.removeprefix(ID_PREFIX)
    ch = slug[:1]
    return ch if ch.isalpha() and ch.isascii() and ch.islower() else "0-9"


def record_relpath(skill_id: str) -> str:
    """The id-derived repository-relative path of a record file."""
    return f"entities/v1-alpha/{shard_for_id(skill_id)}/{skill_id}/{skill_id}.yaml"


def iter_record_yaml_paths():
    """Every Skill record file in the sharded tree, sorted by path."""
    for path in sorted(ENTITIES_ROOT.rglob("*.yaml")):
        if path.parent.name.startswith(ID_PREFIX):
            yield path


@lru_cache(maxsize=1)
def load_skills() -> tuple:
    """Every Skill record, in path order."""
    import yaml  # repo CI dependency, imported lazily
    return tuple(yaml.safe_load(p.read_text()) for p in iter_record_yaml_paths())


def census() -> dict:
    """Entry census per directory, as a GitHub listing counts them
    (CST-017 fails at 800+ tracked entries: files AND subdirectories)."""
    counts = collections.Counter()
    if not ENTITIES_ROOT.is_dir():
        return counts
    for path in ENTITIES_ROOT.rglob("*"):
        counts[str(path.parent.relative_to(BASE))] += 1
        if path.is_dir():
            counts[str(path.relative_to(BASE))] += 0  # ensure key exists
    return dict(counts)
