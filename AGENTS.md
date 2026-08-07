# AGENTS.md — uniesp-data-platform

This repository is the shareable codebase for the UNIESP MBA Data Platform Demo.

## Rules

- Keep the architecture Source → Raw → Bronze → Silver → Gold → Semantic → Analytics explicit.
- Do not commit generated data, original source files, local `.env`, DuckDB databases, or Parquet outputs.
- Dashboard code must consume only semantic DuckDB views.
- Do not invent business semantics: `valor_vantagem` is not salary/remuneration unless official documentation proves it.
- Relevant behavior changes must update the matching spec under `specs/`.
- Technical names, code, identifiers and filenames stay in English.
