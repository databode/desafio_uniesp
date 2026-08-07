# Troubleshooting

## `SOURCE_FILE_PATH must point...`

Crie `.env` a partir de `.env.example` e informe o caminho real do CSV.

## `No module named dagster/duckdb/pyarrow/streamlit`

Instale as dependências:

```bash
python -m pip install -e ".[dev]"
```

## Dagster ou Streamlit não estão no PATH

Use os módulos Python:

```bash
python -m dagster dev -m uniesp_data_platform.definitions
python -m streamlit run app/streamlit_app.py
```

## Semantic database not found

Execute primeiro:

```bash
python scripts/run_pipeline.py
```

## Dados parecem antigos

Apague os arquivos gerados em `data/` ou rode novamente o full refresh. O pipeline é determinístico para a mesma fonte.
