# UNIESP MBA — Mini Data Platform

Este repositório demonstra uma mini plataforma moderna de dados, pequena o suficiente para rodar localmente e clara o suficiente para explicar em sala.

```text
Source → Raw → Bronze → Silver → Gold → Semantic → Analytics
```

## Componentes

| Responsabilidade | Tecnologia |
|---|---|
| Source | CSV |
| Data Lake | Local filesystem |
| Storage format | Parquet |
| Processing | Python / Pandas / PyArrow |
| Orchestration | Dagster |
| Data Quality | Python + report JSON + Dagster metadata |
| Semantic Layer | DuckDB |
| Analytics | Streamlit |

## O que estamos construindo?

Um vertical slice educacional:

1. Dagster lê a fonte configurada.
2. Raw preserva o arquivo original.
3. Bronze converte para Parquet técnico.
4. Silver limpa, tipa e valida.
5. Gold cria dimensões, fato e marts.
6. DuckDB cria schemas `gold` e `semantic`.
7. Streamlit consome somente views `semantic.*`.

## Instalação — Windows primeiro

```powershell
cd path\to\uniesp-data-platform
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
copy .env.example .env
notepad .env
```

Configure no `.env`:

```env
SOURCE_FILE_PATH=/absolute/path/to/servidores-2026.csv
DATA_ROOT=./data
```

Comandos cross-platform equivalentes:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

## Executar a pipeline via CLI

```bash
python scripts/run_pipeline.py
```

## Iniciar Dagster

Use o módulo Python para não depender do diretório de scripts estar no `PATH`:

```bash
python -m dagster dev -m uniesp_data_platform.definitions
```

Abra a URL exibida pelo Dagster no terminal. A porta padrão costuma ser `3000`, mas use sempre a URL impressa pela execução local.

Na UI, materialize o job/asset selection `uniesp_full_refresh` para ver:

```text
source_servidores → raw_servidores → bronze_servidores → silver_servidores → gold → semantic_ready
```

## Iniciar Streamlit

Depois de gerar `data/semantic/uniesp.duckdb`:

```bash
python -m streamlit run app/streamlit_app.py
```

Abra a URL exibida pelo Streamlit. A porta padrão costuma ser `8501`, mas use a URL real do terminal.

## Executar testes

```bash
python -m pytest
```

## Privacidade

O dashboard não mostra rankings individuais, nomes de pessoas ou CPF/CNPJ. As análises são agregadas por município, unidade gestora, tipo/cargo e qualidade dos dados.

## Semântica importante

A coluna `valor_vantagem` não foi renomeada para salário/remuneração porque não há documentação oficial no workspace que autorize essa interpretação.

`matriculas_distintas` conta identificadores `matricula` distintos. Isso não deve ser apresentado como quantidade de pessoas ou servidores únicos, porque nenhuma chave natural de pessoa foi confirmada no profiling.

## Data Quality didática

O relatório separa erros técnicos de warnings. Datas futuras e cargos fora do padrão são warnings: a plataforma detecta e registra, mas não corrige automaticamente sem regra de negócio.
