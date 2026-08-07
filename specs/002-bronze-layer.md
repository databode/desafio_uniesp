# 002 — Bronze Layer

Status: Implemented

## Objective
Criar representação técnica em Parquet próxima da fonte.

## Requirements
- Ler CSV robustamente com strings.
- Preservar colunas originais.
- Adicionar `_ingested_at`, `_source_file`, `_row_hash`.
- Escrever `data/bronze/servidores.parquet`.

## Non-goals
Limpeza de negócio ou deduplicação.

## Inputs
Raw CSV.

## Outputs
Bronze Parquet e metadata JSON.

## Processing rules
Campos identificadores permanecem string.

## Acceptance criteria
Parquet possui mesma contagem de linhas e colunas originais + metadados.

## Tests
Integration fixture checks pipeline output.

## Implementation
- `src/uniesp_data_platform/pipeline.py::materialize_bronze`
- `src/uniesp_data_platform/assets/bronze.py`
