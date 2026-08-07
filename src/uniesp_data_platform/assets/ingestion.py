from __future__ import annotations

from dagster import asset

from ..config import get_settings
from ..pipeline import materialize_raw


@asset(description="Official servidores CSV source metadata; no data copied here.")
def source_servidores(context) -> dict:
    settings = get_settings()
    source = settings.source_file_path
    if not source.exists():
        raise FileNotFoundError(source)
    metadata = {"source_path": str(source), "file_size_bytes": source.stat().st_size}
    context.add_output_metadata(metadata)
    return metadata


@asset(description="Immutable raw copy of the official CSV plus ingestion metadata.")
def raw_servidores(context, source_servidores: dict) -> dict:
    result = materialize_raw(get_settings())
    context.add_output_metadata({"raw_file": str(result["path"]), "row_count": result["row_count"], "checksum_sha256": result["checksum_sha256"]})
    return result
