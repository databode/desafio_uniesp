# Data Model

## Grain

The safe MVP grain is one source record / `valor_vantagem` row. Candidate keys were not unique in profiling, so the pipeline does not deduplicate.

`fct_vantagens` intentionally avoids a person/server grain in its name. Each row is one source record representing a reported `valor_vantagem`, not a confirmed unique person.

## Gold tables

- `dim_municipio(municipio_key, nome_municipio)`
- `dim_unidade_gestora(unidade_gestora_key, codigo_unidade_gestora, descricao_unidade_gestora, nome_municipio)`
- `dim_cargo(cargo_key, codigo_cargo, descricao_cargo_limpa, descricao_cargo, tipo_cargo)` — one observed cargo classification combination; `tipo_cargo` is part of the grain because the same cargo description can appear under different cargo types.
- `dim_matricula(matricula_key, matricula)` — matrícula source identifier; not a confirmed unique person dimension.
- `fct_vantagens` — fact at source-record/vantagem grain with exact decimal string/cents for `valor_vantagem`.
- `mart_vantagens_municipio`, `mart_vantagens_unidade`, `mart_vantagens_cargo`.

## Semantic views

- `semantic.vw_overview`
- `semantic.vw_municipios`
- `semantic.vw_unidades_gestoras`
- `semantic.vw_cargos`
- `semantic.vw_evolucao_mensal` — comparison between two competencies, not a historical trend.
- `semantic.vw_data_quality`

## Privacy and semantic caveat

The dashboard does not expose names, CPF/CNPJ or individual rankings. `matriculas_distintas` is a count of distinct source matrícula identifiers and must not be presented as distinct people.
