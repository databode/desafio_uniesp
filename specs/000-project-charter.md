# 000 — Project Charter

Status: Implemented

## Problem
Demonstrar uma plataforma de dados completa usando um dataset simples.

## Users
- MBA students
- Instructor / presenter
- Data Engineer

## Goals
Construir um vertical slice: `CSV → Lake → Transform → Semantic → Dashboard`.

## Non-goals
Production scalability, distributed processing, HA, authentication, enterprise governance, Cloud deployment.

## Definition of Done
1. apontar para o CSV; 2. iniciar Dagster; 3. visualizar a pipeline; 4. executar full refresh; 5. visualizar Raw → Bronze → Silver → Gold → Semantic; 6. acompanhar Data Quality; 7. iniciar Streamlit; 8. visualizar insights derivados exclusivamente da semantic layer.

## Implementation
- `src/uniesp_data_platform/`
- `app/streamlit_app.py`
- `semantic/*.yml`

## Tests
- `tests/unit/`
- `tests/integration/`
