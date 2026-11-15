# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### CR-DEA-SKL-02: Skills<->Roles Interlock Completion (7 Missing Skills)

The roles catalog references 742 distinct skills; 735 were published. This CR admits the exact 7-record gap through the CR-DEA-SKL-01 pipeline (CSV renamed+extended to bulk-742; manifest sha256/rows/kinds/edges updated; slice registry extended with the roles-taxonomy facets banking/health/public-sector; materialize_skills.py materialized the 7 at the sharded layout; bespoke index at 742). Evidence per record = the citing roles record (repository-verifiable); records stay proposed v0.1.0 candidates. Interlock now 742/742.

### CR-DEA-SKL-01: Bulk Skill Ingestion Pipeline (735 records)

Roles-style bulk ingestion: CSV + manifest + materialize_skills.py; 735 Skill candidates at the sharded layout (see the landed CR for the full record).
