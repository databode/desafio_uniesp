from __future__ import annotations

from dagster import AssetSelection, Definitions, define_asset_job, load_assets_from_modules

from .assets import bronze, gold, ingestion, semantic, silver

all_assets = load_assets_from_modules([ingestion, bronze, silver, gold, semantic])

uniesp_full_refresh = define_asset_job(
    name="uniesp_full_refresh",
    selection=AssetSelection.all(),
    description="Materialize the complete Source to Raw to Bronze to Silver to Gold to Semantic flow.",
)

defs = Definitions(assets=all_assets, jobs=[uniesp_full_refresh])
