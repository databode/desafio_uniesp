# 003 — Silver Layer

Status: Implemented

## Objective
Criar camada limpa, tipada e validada.

## Requirements
- Trim/normalização de whitespace preservando acentos.
- Parse `valor_vantagem` pt-BR e ponto de milhar sem vírgula (`1.700` → `1700`).
- Parse `data_admissao` DD/MM/YYYY.
- Parse `ano_mes` YYYYMM e criar `competencia_date`.
- Preservar `matricula` e `codigo_unidade_gestora` como string.
- Extrair `codigo_cargo` e `descricao_cargo_limpa` quando padrão `digits - text` existir.
- Não deduplicar.

## Non-goals
Inferir salário/remuneração ou regras de negócio inexistentes.

## Inputs
Bronze Parquet.

## Outputs
Silver Parquet e report DQ JSON.

## Acceptance criteria
Parsers passam testes unitários e pipeline real não perde linhas.

## Implementation
- `src/uniesp_data_platform/utils/parsing.py`
- `src/uniesp_data_platform/pipeline.py::materialize_silver`
- `src/uniesp_data_platform/assets/silver.py`

## Tests
- `tests/unit/test_parsing.py`
- `tests/integration/test_pipeline.py`
