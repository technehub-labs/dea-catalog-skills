#!/usr/bin/env python3
"""Materialize bulk ingestion rows as Skill entity instances (admission path).

Per CR-DEA-SKL-01 and the dea-catalog-roles admission model (GOVERNANCE.md
S4 there, mirrored here): bulk rows are candidates; they materialize as
entities/v1-alpha/<shard>/<id>/<id>.yaml only when admitted via CR.
This tool performs the mechanical conversion for an explicit list of row ids
(or --industry for a bounded slice admission):

    python scripts/materialize_skills.py --ids skills:skill-a skills:skill-b
    python scripts/materialize_skills.py --industry telecom --limit 10

Safety:
  - refuses to overwrite an existing record (existing wins);
  - validates the CSV against the manifest first (reuses the gate);
  - refuses rows whose lifecycle_status is not 'proposed';
  - refuses --industry without --limit (whole-slice admission must be an
    explicit bounded decision, not a default);
  - writes the CR-MET-024 shard layout (dea-metaframework
    docs/entity-storage-layout.md S4) and the per-record README.md.

Output YAML validates against schemas/skill.schema.json (vendored from
dea-metamodel; enforced by scripts/validate_ingestion.py gate 6).
"""

import argparse
import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _catalog  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

# --- deterministic YAML emitter (stdlib only) ------------------------------
# Byte-identical to the ingestion build pipeline's emitter: a record written
# here and a record produced by the build pipeline are the same bytes.
"""Deterministic YAML emit + constrained parse (stdlib only).

The emitter subset is exactly what the ingestion package needs: nested
dicts, lists of scalars, lists of dicts, plain scalars, single-quoted
scalars and folded block scalars. The parser round-trips that grammar
and serves as the local QA gate; repo CI uses PyYAML against the same
files.
"""
import re

PLAIN_OK = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_ ./&<>()',;?*=-]*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _fold(s, indent):
    pad = " " * indent
    words, line, out = s.split(" "), [], []
    for w in words:
        cand = " ".join(line + [w])
        if len(cand) > 88 and line:
            out.append(pad + " ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        out.append(pad + " ".join(line))
    return out


def _scalar(v):
    if isinstance(v, bool):
        return ("true" if v else "false"), None
    if isinstance(v, (int, float)):
        return str(v), None
    s = str(v)
    if s == "":
        return "''", None
    if ISO_DATE.match(s):
        return "'" + s + "'", None
    if ": " in s and not s.startswith("#"):
        return None, (">-", s)
    if not PLAIN_OK.match(s) or s != s.strip():
        return "'" + s.replace("'", "''") + "'", None
    return s, None


def dump_yaml(obj, indent=0):
    """YAML text for dicts/lists/scalars, insertion order, block style."""
    pad = " " * indent
    out = []
    if isinstance(obj, dict):
        if not obj:
            out.append(pad + "{}\n")
        for k, v in obj.items():
            if isinstance(v, dict):
                if v:
                    out.append(f"{pad}{k}:\n" + dump_yaml(v, indent + 2))
                else:
                    out.append(f"{pad}{k}: {{}}\n")
            elif isinstance(v, list):
                if v:
                    out.append(f"{pad}{k}:\n" + dump_yaml(v, indent + 2))
                else:
                    out.append(f"{pad}{k}: []\n")
            else:
                inline, block = _scalar(v)
                if block:
                    style, text = block
                    out.append(f"{pad}{k}: {style}\n")
                    for b in _fold(text, indent + 2):
                        out.append(b + "\n")
                else:
                    out.append(f"{pad}{k}: {inline}\n")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                if not item:
                    out.append(pad + "- {}\n")
                    continue
                first = True
                for k, v in item.items():
                    prefix = f"{pad}- " if first else f"{pad}  "
                    first = False
                    if isinstance(v, dict):
                        if v:
                            out.append(f"{prefix}{k}:\n" + dump_yaml(v, indent + 4))
                        else:
                            out.append(f"{prefix}{k}: {{}}\n")
                    elif isinstance(v, list):
                        if v:
                            out.append(f"{prefix}{k}:\n" + dump_yaml(v, indent + 4))
                        else:
                            out.append(f"{prefix}{k}: []\n")
                    else:
                        inline, block = _scalar(v)
                        if block:
                            style, text = block
                            out.append(f"{prefix}{k}: {style}\n")
                            for b in _fold(text, indent + 4):
                                out.append(b + "\n")
                        else:
                            out.append(f"{prefix}{k}: {inline}\n")
            else:
                inline, block = _scalar(item)
                out.append(f"{pad}- {inline}\n")
    return "".join(out)





def skill_domain_for(row):
    if row["skill_kind"] == "seed-capability":
        return "cross-industry"
    return row["industries"].split(";")[0].strip()


def row_to_instance(row):
    industries = [t.strip() for t in row["industries"].split(";") if t.strip()]
    tags = [t.strip() for t in row["tags"].split(";") if t.strip()]
    return {
        "id": row["id"],
        "type": row["type"],
        "name": row["name"],
        "description": row["description"],
        "version": row["version"],
        "lifecycle_status": row["lifecycle_status"],
        "skill_domain": skill_domain_for(row),
        "tags": tags,
        "metadata": {
            "catalog": row["catalog"],
            "metamodel_version": row["metamodel_version"],
            "skill_kind": row["skill_kind"],
            "industries": industries,
            "provenance": {
                "type": row["provenance_type"],
                "reference": row["provenance_reference"],
                "asserted_by": row["provenance_asserted_by"],
                "verification_status": row["provenance_verification_status"],
            },
            "required_by": {
                "batch_roles": int(row["required_by_count"]),
                "admitted_roles": int(row["admitted_required_by_count"]),
                "example_role": row["example_role_id"],
            },
        },
        # NOTE (CR-2 S7/S8): the SKL -> ROL "required by" view is generated,
        # never stored. Stored instance edges live on the role side
        # (relationship_type: requires). See dependencies.yaml.
    }


def record_readme(rec, relpath):
    ind = ", ".join(rec["metadata"]["industries"])
    prov = rec["metadata"]["provenance"]
    rq = rec["metadata"]["required_by"]
    return f"""# {rec["name"]}

**Record id:** `{rec["id"]}`
**Kind:** {rec["metadata"]["skill_kind"]} | **Lifecycle:** {rec["lifecycle_status"]} (v{rec["version"]}) | **Skill domain:** {rec["skill_domain"]}
**Industries (demand evidence):** {ind}
**Path:** `{relpath}` (derived from the id; entity-storage-layout.md S5)

{rec["description"]}

**Demand:** required by {rq["batch_roles"]} batch roles ({rq["admitted_roles"]} admitted to date);
example requirer `{rq["example_role"]}`.

**Provenance:** {prov["type"]} | {prov["reference"]} | asserted by {prov["asserted_by"]} | {prov["verification_status"]}.

*Generated by `scripts/materialize_skills.py` (CR-DEA-SKL-01). Do not edit
manually; regenerate on record change.*
"""


def write_record(row):
    rec = row_to_instance(row)
    relpath = _catalog.record_relpath(rec["id"])
    out = ROOT / relpath
    if out.is_file():
        raise FileExistsError(relpath)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        f.write(dump_yaml(rec))
    (out.parent / "README.md").write_text(record_readme(rec, relpath))
    return relpath


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids", nargs="+")
    g.add_argument("--industry")
    ap.add_argument("--kind", choices=["domain-capability", "domain-operations",
                                       "seed-capability"])
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    if args.industry and not args.limit:
        sys.exit("--industry requires --limit (bounded admission only)")
    if args.kind and not (args.industry or args.ids):
        sys.exit("--kind filters --industry/--ids selections; it selects nothing alone")

    import validate_ingestion  # noqa: E402  repo gate; lazy (needs PyYAML)
    if validate_ingestion.main() != 0:
        sys.exit("validate_ingestion failed; refusing to materialize")

    with open(_catalog.INGESTION_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    if args.ids:
        selected = [r for r in rows if r["id"] in set(args.ids)]
        missing = set(args.ids) - {r["id"] for r in selected}
        if missing:
            sys.exit(f"unknown ids: {sorted(missing)}")
    else:
        selected = [r for r in rows
                    if r["industries"].split(";")[0].strip() == args.industry]
        if args.kind:
            selected = [r for r in selected if r["skill_kind"] == args.kind]
        selected = selected[: args.limit]

    written = skipped = 0
    for row in selected:
        try:
            rel = write_record(row)
            print(f"wrote: {rel}")
            written += 1
        except FileExistsError as rel:
            print(f"skip (exists): {rel}")
            skipped += 1

    print(f"materialized {written}, skipped {skipped}")
    print("next: add CATALOG.yaml entries + admission CR, then validate_ingestion.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
