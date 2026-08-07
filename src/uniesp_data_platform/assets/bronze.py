from __future__ import annotations

from dagster import asset

from ..config import get_settings
from ..pipeline import materialize_bronze


@asset(description="Technical Parquet representation preserving source columns as strings.")
def bronze_servidores(context, raw_servidores: dict) -> dict:
    result = materialize_bronze(raw_servidores, get_settings())
    context.add_output_metadata({"output_path": str(result["path"]), "row_count": result["row_count"], "column_count": result["column_count"]})
    return result
