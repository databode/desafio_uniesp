# 007 — Orchestration

Status: Implemented

## Objective
Modelar o fluxo como assets Dagster com lineage visual.

## Requirements
- Assets: source, raw, bronze, silver, gold model/tables, semantic views, semantic ready.
- Job `uniesp_full_refresh`.
- Metadata útil: paths, row counts, checks/report.

## Non-goals
Observabilidade própria, schedules, sensors, deployment remoto.

## Acceptance criteria
`python -m dagster dev -m uniesp_data_platform.definitions` carrega definitions.

## Implementation
- `src/uniesp_data_platform/definitions.py`
- `src/uniesp_data_platform/assets/*.py`
