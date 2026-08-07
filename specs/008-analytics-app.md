# 008 — Analytics App

Status: Implemented

## Objective
Criar dashboard didático consumindo somente a semantic layer.

## Requirements
- Overview cards.
- Municípios, unidades gestoras, cargos.
- Data Quality.
- About/Architecture.
- Não consultar CSV/Raw/Bronze/Silver.
- Não exibir rankings individuais, nomes de pessoas ou CPF/CNPJ.

## Non-goals
BI enterprise, autenticação, API.

## Inputs
DuckDB semantic views.

## Outputs
Streamlit app.

## Acceptance criteria
App importa/compila e usa somente `semantic.*` queries.

## Implementation
- `app/streamlit_app.py`
