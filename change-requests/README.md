# Change Requests — dea-catalog-skills

| CR | Title | Status | Notes |
|---|---|---|---|
| [CR-DEA-SKL-01](CR-DEA-SKL-01.md) | Bulk Skill Ingestion Pipeline (735 records) | Landed (PR #2) | Roles-style bulk ingestion: CSV + manifest + materialize_skills.py; 735 Skill candidates at the sharded layout. |
| [CR-DEA-SKL-02](CR-DEA-SKL-02-cr-dea-skl-02.md) | Skills<->Roles Interlock Completion (7 Missing Skills) | **Landed (this PR)** | 7 interlock-gap skills admitted via the CR-DEA-SKL-01 pipeline (citing-roles evidence; slice registry extended banking/health/public-sector); 742/742 roles refs resolve. |
