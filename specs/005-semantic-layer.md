# 005 — Semantic Layer

Status: Implemented

## Objective
Expor views estáveis em DuckDB para consumo analítico, com nomes semanticamente honestos.

## Requirements
- Criar `data/semantic/uniesp.duckdb`.
- Criar schemas `gold` e `semantic`.
- Views: `vw_overview`, `vw_municipios`, `vw_unidades_gestoras`, `vw_cargos`, `vw_evolucao_mensal`, `vw_data_quality`.
- Métricas preservam nome `valor_vantagem`.
- Expor `matriculas_distintas` quando contar identificadores `matricula`; não expor contagem de servidores únicos sem chave de pessoa confirmada.
- `vw_evolucao_mensal` deve ser apresentada como comparação entre competências, não tendência histórica.

## Non-goals
Instalar plataforma semântica externa, afirmar quantidade de pessoas únicas.

## Inputs
Gold Parquet e DQ report.

## Outputs
DuckDB queryable e YAML semântico.

## Acceptance criteria
Streamlit consulta apenas `semantic.*` e smoke test consulta as views.

## Implementation
- `src/uniesp_data_platform/pipeline.py::materialize_semantic`
- `semantic/semantic-model.yml`
- `semantic/metrics.yml`
