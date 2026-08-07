from __future__ import annotations

from dagster import asset

from ..config import get_settings
from ..pipeline import materialize_silver


@asset(description="Clean, typed and quality-profiled servidores layer.")
def silver_servidores(context, bronze_servidores: dict) -> dict:
    result = materialize_silver(bronze_servidores, get_settings())
    context.add_output_metadata({
        "output_path": str(result["path"]),
        "row_count": result["row_count"],
        "valor_parse_success": result["valor_parse_success"],
        "data_admissao_parse_success": result["data_admissao_parse_success"],
        "quality_report_path": str(result["quality_report_path"]),
    })
    return result
