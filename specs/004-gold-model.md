# 004 — Gold Model

Status: Implemented

## Objective
Modelar dados para analytics com dimensões, fato e marts simples, sem afirmar chaves de pessoa não comprovadas.

## Requirements
- Criar `dim_municipio`, `dim_unidade_gestora`, `dim_cargo`, `dim_matricula`.
- Criar `fct_vantagens` no grain registro fonte/vantagem.
- Usar `fct_vantagens` para evitar sugerir que a fact esteja no grain de pessoa/servidor único.
- Documentar que cada linha representa um registro do arquivo fonte contendo um `valor_vantagem`.
- Criar marts por município, unidade e cargo.
- Não expor nomes de pessoas ou CPF/CNPJ em Gold dimensional de matrícula nem no dashboard.
- Usar `matricula_key` como surrogate key técnica da dimensão matrícula; não tratar como pessoa.

## Non-goals
Star schema enterprise completo, deduplicação não comprovada, dimensão de pessoa/servidor único.

## Inputs
Silver Parquet.

## Outputs
Parquets em `data/gold/`.

## Acceptance criteria
Gold materializa e é carregável pelo DuckDB.

## Implementation
- `src/uniesp_data_platform/pipeline.py::materialize_gold`
- `src/uniesp_data_platform/assets/gold.py`

## Semantic note
Profiling agregado mostrou que `matricula` não é uma chave de pessoa confiável: há matrículas em múltiplas unidades, matrículas associadas a múltiplos nomes e nomes associados a múltiplas matrículas. Por isso, o MVP usa `dim_matricula` e a métrica `matriculas_distintas`, não uma métrica de servidores únicos.

`dim_cargo` tem grain de combinação observada de classificação de cargo: `codigo_cargo`, `descricao_cargo_limpa`, `descricao_cargo` original e `tipo_cargo`. A cardinalidade alta vem da diversidade textual/códigos do source; incluir `descricao_cargo` original não infla a cardinalidade em relação a `codigo_cargo + descricao_cargo_limpa + tipo_cargo`, e `tipo_cargo` é mantido porque a mesma descrição pode ocorrer em tipos diferentes.
