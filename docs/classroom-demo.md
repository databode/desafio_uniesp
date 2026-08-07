# Classroom Demo Script

## 1 — Source: recebemos um arquivo

"Este é nosso sistema fonte. Ele é simples, mas contém dados reais de domínio, formatos locais e questões de privacidade."

## 2 — Perguntar aos alunos

"Por que não conectar o dashboard diretamente nesse CSV?"

Use a pergunta para motivar contratos, rastreabilidade, qualidade e desacoplamento entre produção e consumo.

## 3 — Mostrar arquitetura

Explique a responsabilidade de cada camada:

```text
SOURCE → RAW → BRONZE → SILVER → GOLD → SEMANTIC → CONSUMPTION
```

- **Source**: recebemos um arquivo.
- **Raw**: primeiro preservamos aquilo que recebemos.
- **Bronze**: transformamos em uma representação técnica eficiente.
- **Silver**: limpamos, tipamos e aplicamos qualidade.
- **Gold**: organizamos pensando em analytics.
- **Semantic**: definimos o contrato que consumidores enxergam.
- **Streamlit**: o dashboard deixa de conhecer a implementação interna.
- **Dagster**: o orchestrator entende dependências, executa e observa o pipeline.

> Data Platform != uma tecnologia. A plataforma é o conjunto de responsabilidades, contratos, dados, execução e consumo.

## 4 — Abrir Dagster

Execute:

```bash
python -m dagster dev -m uniesp_data_platform.definitions
```

Mostre o asset graph e as dependências. Reforce que Dagster coordena assets; ele não é uma camada de dados.

## 5 — Materializar pipeline

Materialize `uniesp_full_refresh` ou todos os assets:

```text
Raw → Bronze → Silver → Gold → Semantic
```

## 6 — Mostrar Data Quality

Abra o metadata JSON ou `semantic.vw_data_quality`. Discuta:

- parsers de `valor_vantagem` e datas;
- candidate keys não únicas;
- 2 datas futuras de admissão;
- cargos fora do padrão esperado.

Mensagem didática: Data Quality não significa alterar automaticamente todo dado estranho. A plataforma detecta, registra e classifica. Correção só deve ocorrer quando houver regra de negócio ou contrato técnico claro.

## 7 — Abrir Streamlit

```bash
python -m streamlit run app/streamlit_app.py
```

Mostre overview, municípios, unidades, cargos, comparação entre competências e DQ.

Não apresente `matriculas_distintas` como pessoas distintas. É apenas contagem de identificadores `matricula` observados.

## 8 — Explicar semantic layer

Mostre que Streamlit consulta `semantic.*`, não CSV/Raw/Bronze/Silver/Gold diretamente. Esse é o desacoplamento entre consumidores e modelo físico.

## 9 — Relacionar com enterprise

Analogia de responsabilidades, sem afirmar equivalência funcional completa:

| Demo local | Possível equivalente enterprise |
|---|---|
| CSV | APIs, bancos, arquivos, streams |
| Filesystem | ADLS / S3 / GCS |
| Parquet | Parquet / Delta / Iceberg |
| Python / DuckDB | Spark / Databricks / warehouses |
| Dagster | Dagster / Airflow / outros orchestrators |
| DuckDB Semantic | Lakehouse/Warehouse/Semantic platforms |
| Streamlit | Power BI / Tableau / Looker / applications |

Feche com a ideia central: a sofisticação do MVP está na clareza dos contratos, não na quantidade de ferramentas.
