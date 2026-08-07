from __future__ import annotations

from dagster import asset

from ..config import get_settings
from ..pipeline import materialize_semantic


@asset(description="DuckDB schemas/tables/views that expose the semantic layer.")
def semantic_views(
    context,
    gold_model: dict,
    fct_vantagens: dict,
    mart_vantagens_municipio: dict,
    mart_vantagens_unidade: dict,
    mart_vantagens_cargo: dict,
) -> dict:
    result = materialize_semantic(gold_model, get_settings())
    context.add_output_metadata({"duckdb_path": result["duckdb_path"], "semantic_views": ", ".join(result["semantic_views"])})
    return result


@asset(description="Final marker asset for a fully queryable semantic layer.")
def semantic_ready(context, semantic_views: dict) -> dict:
    context.add_output_metadata(semantic_views)
    return semantic_views
