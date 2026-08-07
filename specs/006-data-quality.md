# 006 — Data Quality

Status: Implemented

## Objective
Gerar checks leves e relatório consumível, distinguindo erros técnicos de warnings semânticos.

## Requirements
- Required columns present.
- Row count > 0.
- `ano_mes` valid.
- `valor_vantagem` parse success.
- `data_admissao` parse success.
- Not-null for município and unidade gestora.
- Warning for future admission dates.
- Warning for cargo descriptions outside the deterministic `codigo - descricao` pattern.
- Candidate key duplicate findings documented.

## Error checks
Falham contrato técnico essencial e devem ser tratados como erro de materialização/qualidade: arquivo vazio, colunas obrigatórias ausentes, parse técnico essencial impossível, campos essenciais nulos.

## Warning checks
Dados suspeitos, mas semanticamente desconhecidos, não devem bloquear o MVP sem regra de negócio: datas futuras e cargos fora do padrão.

## Non-goals
Great Expectations, uniqueness constraints inventadas, bloqueio por warnings sem regra de negócio, correção automática de valores estranhos.

## Outputs
`data/metadata/data_quality_report.json` and `semantic.vw_data_quality`.

## Acceptance criteria
Report contains check statuses, severity groups and profiling findings.

## Implementation
- `src/uniesp_data_platform/pipeline.py::build_quality_report`
- `src/uniesp_data_platform/quality/checks.py`
