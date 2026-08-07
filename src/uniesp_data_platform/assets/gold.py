from __future__ import annotations

from dagster import asset

from ..config import get_settings
from ..pipeline import materialize_gold


@asset(description="Writes all Gold Parquet tables from Silver.")
def gold_model(context, silver_servidores: dict) -> dict:
    result = materialize_gold(silver_servidores, get_settings())
    context.add_output_metadata({name: meta["row_count"] for name, meta in result["tables"].items()})
    return result


@asset(description="Gold municipality dimension.")
def dim_municipio(context, gold_model: dict) -> dict:
    meta = gold_model["tables"]["dim_municipio"]
    context.add_output_metadata(meta)
    return meta


@asset(description="Gold management unit dimension.")
def dim_unidade_gestora(context, gold_model: dict) -> dict:
    meta = gold_model["tables"]["dim_unidade_gestora"]
    context.add_output_metadata(meta)
    return meta


@asset(description="Gold position/cargo dimension.")
def dim_cargo(context, gold_model: dict) -> dict:
    meta = gold_model["tables"]["dim_cargo"]
    context.add_output_metadata(meta)
    return meta


@asset(description="Gold matrícula dimension; not a confirmed unique person dimension and not exposed in dashboard.")
def dim_matricula(context, gold_model: dict) -> dict:
    meta = gold_model["tables"]["dim_matricula"]
    context.add_output_metadata(meta)
    return meta


@asset(description="Gold fact table at source record/advantage row grain.")
def fct_vantagens(context, gold_model: dict, dim_municipio: dict, dim_unidade_gestora: dict, dim_cargo: dict, dim_matricula: dict) -> dict:
    meta = gold_model["tables"]["fct_vantagens"]
    context.add_output_metadata(meta)
    return meta


@asset(description="Gold municipality aggregate mart.")
def mart_vantagens_municipio(context, gold_model: dict, fct_vantagens: dict, dim_municipio: dict) -> dict:
    meta = gold_model["tables"]["mart_vantagens_municipio"]
    context.add_output_metadata(meta)
    return meta


@asset(description="Gold management unit aggregate mart.")
def mart_vantagens_unidade(context, gold_model: dict, fct_vantagens: dict, dim_unidade_gestora: dict) -> dict:
    meta = gold_model["tables"]["mart_vantagens_unidade"]
    context.add_output_metadata(meta)
    return meta


@asset(description="Gold cargo aggregate mart.")
def mart_vantagens_cargo(context, gold_model: dict, fct_vantagens: dict, dim_cargo: dict) -> dict:
    meta = gold_model["tables"]["mart_vantagens_cargo"]
    context.add_output_metadata(meta)
    return meta
