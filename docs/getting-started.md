# Getting Started

1. Create a virtual environment.
2. Install the project with dev dependencies.
3. Configure `.env` with `SOURCE_FILE_PATH` and optional `DATA_ROOT`.
4. Run `python scripts/run_pipeline.py` for a quick full refresh.
5. Run `python -m dagster dev -m uniesp_data_platform.definitions` for the asset graph.
6. Run `python -m streamlit run app/streamlit_app.py` for analytics.

See `README.md` for Windows-first commands.
