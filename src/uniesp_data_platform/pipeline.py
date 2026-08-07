from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from .config import Settings, ensure_data_dirs, get_settings
from .utils.parsing import (
    clean_string,
    decimal_to_cents,
    parse_ano_mes,
    parse_cargo,
    parse_date_ddmmyyyy,
    parse_valor_vantagem,
    row_hash,
)

EXPECTED_COLUMNS = [
    "nome_municipio",
    "codigo_unidade_gestora",
    "descricao_unidade_gestora",
    "cpf_cnpj",
    "nome_servidor",
    "tipo_cargo",
    "descricao_cargo",
    "valor_vantagem",
    "data_admissao",
    "matricula",
    "ano_mes",
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f, delimiter=";"))


def read_csv_strings(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype="string", keep_default_na=False)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def materialize_raw(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    ensure_data_dirs(settings)
    source = settings.source_file_path
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    raw_dir = settings.raw_dir / "servidores"
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / source.name
    shutil.copy2(source, target)

    metadata = {
        "asset": "raw_servidores",
        "source_file": str(source),
        "raw_file": str(target),
        "file_size_bytes": source.stat().st_size,
        "checksum_sha256": file_sha256(source),
        "ingestion_timestamp": utc_now(),
        "row_count": count_csv_rows(source),
        "raw_organization": "source_file_copy",
    }
    metadata_path = settings.metadata_dir / "raw_servidores.json"
    write_json(metadata_path, metadata)
    return {"path": target, "metadata_path": metadata_path, **metadata}


def materialize_bronze(raw: dict[str, Any] | None = None, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    ensure_data_dirs(settings)
    raw = raw or materialize_raw(settings)
    raw_path = Path(raw["path"])
    df = read_csv_strings(raw_path)
    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected CSV columns: {list(df.columns)}")

    ingested_at = utc_now()
    df["_ingested_at"] = ingested_at
    df["_source_file"] = raw_path.name
    df["_row_hash"] = [row_hash(row, EXPECTED_COLUMNS) for row in df.to_dict("records")]

    output = settings.bronze_dir / "servidores.parquet"
    df.to_parquet(output, index=False, engine="pyarrow")
    metadata = {
        "asset": "bronze_servidores",
        "input_path": str(raw_path),
        "output_path": str(output),
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "source_columns": EXPECTED_COLUMNS,
    }
    write_json(settings.metadata_dir / "bronze_servidores.json", metadata)
    return {"path": output, **metadata}


def materialize_silver(bronze: dict[str, Any] | None = None, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    ensure_data_dirs(settings)
    bronze = bronze or materialize_bronze(settings=settings)
    df = pd.read_parquet(bronze["path"], engine="pyarrow")

    for col in EXPECTED_COLUMNS:
        df[col] = df[col].map(clean_string).astype("string")

    parsed_values = df["valor_vantagem"].map(parse_valor_vantagem)
    df["valor_vantagem_decimal"] = parsed_values.map(lambda x: None if x[0] is None else format(x[0], "f")).astype("string")
    df["valor_vantagem_cents"] = parsed_values.map(lambda x: decimal_to_cents(x[0])).astype("Int64")
    df["valor_vantagem_format"] = parsed_values.map(lambda x: x[1]).astype("string")

    dates = df["data_admissao"].map(parse_date_ddmmyyyy)
    df["data_admissao_date"] = pd.to_datetime(dates, errors="coerce")

    ano = df["ano_mes"].map(parse_ano_mes)
    df["ano_mes"] = ano.map(lambda x: x[0]).astype("string")
    df["competencia_date"] = pd.to_datetime(ano.map(lambda x: x[1]), errors="coerce")

    cargo = df["descricao_cargo"].map(parse_cargo)
    df["codigo_cargo"] = cargo.map(lambda x: x[0]).astype("string")
    df["descricao_cargo_limpa"] = cargo.map(lambda x: x[1]).astype("string")
    df["cargo_pattern_valid"] = cargo.map(lambda x: x[2]).astype("boolean")

    output = settings.silver_dir / "servidores.parquet"
    df.to_parquet(output, index=False, engine="pyarrow")
    report = build_quality_report(df, bronze_path=Path(bronze["path"]))
    report_path = settings.metadata_dir / "data_quality_report.json"
    write_json(report_path, report)
    metadata = {
        "asset": "silver_servidores",
        "input_path": str(bronze["path"]),
        "output_path": str(output),
        "row_count": int(len(df)),
        "valor_parse_success": int(df["valor_vantagem_decimal"].notna().sum()),
        "data_admissao_parse_success": int(df["data_admissao_date"].notna().sum()),
        "quality_report_path": str(report_path),
    }
    write_json(settings.metadata_dir / "silver_servidores.json", metadata)
    return {"path": output, "quality_report_path": report_path, **metadata}


def build_quality_report(df: pd.DataFrame, bronze_path: Path) -> dict[str, Any]:
    today = pd.Timestamp(date.today())
    candidate_keys = {
        "matricula+ano_mes": ["matricula", "ano_mes"],
        "cpf_cnpj+ano_mes": ["cpf_cnpj", "ano_mes"],
        "matricula+codigo_unidade_gestora+ano_mes": ["matricula", "codigo_unidade_gestora", "ano_mes"],
        "cpf_cnpj+codigo_unidade_gestora+ano_mes": ["cpf_cnpj", "codigo_unidade_gestora", "ano_mes"],
    }
    key_report = {}
    for name, cols in candidate_keys.items():
        counts = df.groupby(cols, dropna=False).size()
        key_report[name] = {
            "distinct": int(len(counts)),
            "duplicate_keys": int((counts > 1).sum()),
            "max_rows_per_key": int(counts.max()) if len(counts) else 0,
        }

    error_checks = {
        "required_columns_present": set(EXPECTED_COLUMNS).issubset(df.columns),
        "row_count_greater_than_zero": len(df) > 0,
        "ano_mes_valid": bool(df["competencia_date"].notna().all()),
        "valor_vantagem_parse_success": bool(df["valor_vantagem_decimal"].notna().all()),
        "data_admissao_parse_success": bool(df["data_admissao_date"].notna().all()),
        "codigo_unidade_gestora_not_null": bool(df["codigo_unidade_gestora"].notna().all()),
        "nome_municipio_not_null": bool(df["nome_municipio"].notna().all()),
    }
    warning_checks = {
        "data_admissao_no_future_dates": bool((df["data_admissao_date"] <= today).all()),
        "descricao_cargo_pattern_valid": bool(df["cargo_pattern_valid"].fillna(False).all()),
    }
    checks = {**error_checks, **warning_checks}
    return {
        "generated_at": utc_now(),
        "bronze_path": str(bronze_path),
        "row_count": int(len(df)),
        "required_columns": EXPECTED_COLUMNS,
        "null_counts": {col: int(df[col].isna().sum()) for col in EXPECTED_COLUMNS},
        "duplicate_full_rows": int(df[EXPECTED_COLUMNS].duplicated().sum()),
        "valor_vantagem_formats": {str(k): int(v) for k, v in Counter(df["valor_vantagem_format"].dropna()).items()},
        "valor_vantagem_parse_failures": int(df["valor_vantagem_decimal"].isna().sum()),
        "data_admissao_parse_failures": int(df["data_admissao_date"].isna().sum()),
        "future_data_admissao_count": int((df["data_admissao_date"] > today).sum()),
        "cargo_pattern_counts": {"valid": int(df["cargo_pattern_valid"].sum()), "invalid": int((~df["cargo_pattern_valid"].fillna(False)).sum())},
        "candidate_keys": key_report,
        "error_checks": error_checks,
        "warning_checks": warning_checks,
        "checks": checks,
        "overall_status": "error" if not all(error_checks.values()) else "warning" if not all(warning_checks.values()) else "passed",
    }


def _dimension(df: pd.DataFrame, cols: list[str], key_name: str) -> pd.DataFrame:
    dim = df[cols].drop_duplicates().sort_values(cols, na_position="last").reset_index(drop=True)
    dim.insert(0, key_name, range(1, len(dim) + 1))
    return dim


def materialize_gold(silver: dict[str, Any] | None = None, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    ensure_data_dirs(settings)
    silver = silver or materialize_silver(settings=settings)
    df = pd.read_parquet(silver["path"], engine="pyarrow")

    dim_municipio = _dimension(df, ["nome_municipio"], "municipio_key")
    dim_unidade = _dimension(df, ["codigo_unidade_gestora", "descricao_unidade_gestora", "nome_municipio"], "unidade_gestora_key")
    dim_cargo = _dimension(df, ["codigo_cargo", "descricao_cargo_limpa", "descricao_cargo", "tipo_cargo"], "cargo_key")
    # Privacy-aware local dimension at matrícula grain. It is not a confirmed unique person dimension.
    dim_matricula = _dimension(df, ["matricula"], "matricula_key")

    fact = df[[
        "ano_mes",
        "competencia_date",
        "matricula",
        "cpf_cnpj",
        "nome_municipio",
        "codigo_unidade_gestora",
        "descricao_unidade_gestora",
        "codigo_cargo",
        "descricao_cargo_limpa",
        "descricao_cargo",
        "tipo_cargo",
        "data_admissao_date",
        "valor_vantagem_decimal",
        "valor_vantagem_cents",
        "_row_hash",
    ]].copy()
    fact = fact.merge(dim_municipio, on=["nome_municipio"], how="left")
    fact = fact.merge(dim_unidade, on=["codigo_unidade_gestora", "descricao_unidade_gestora", "nome_municipio"], how="left")
    fact = fact.merge(dim_cargo, on=["codigo_cargo", "descricao_cargo_limpa", "descricao_cargo", "tipo_cargo"], how="left")
    fact = fact.merge(dim_matricula, on=["matricula"], how="left")
    fact = fact[[
        "ano_mes",
        "competencia_date",
        "matricula_key",
        "municipio_key",
        "unidade_gestora_key",
        "cargo_key",
        "tipo_cargo",
        "data_admissao_date",
        "valor_vantagem_decimal",
        "valor_vantagem_cents",
        "_row_hash",
    ]]

    outputs = {
        "dim_municipio": dim_municipio,
        "dim_unidade_gestora": dim_unidade,
        "dim_cargo": dim_cargo,
        "dim_matricula": dim_matricula,
        "fct_vantagens": fact,
        "mart_vantagens_municipio": fact.merge(dim_municipio, on="municipio_key").groupby(["ano_mes", "nome_municipio"], as_index=False).agg(
            quantidade_registros=("_row_hash", "count"), valor_vantagem_cents=("valor_vantagem_cents", "sum"), matriculas_distintas=("matricula_key", "nunique")
        ),
        "mart_vantagens_unidade": fact.merge(dim_unidade, on="unidade_gestora_key").groupby(["ano_mes", "nome_municipio", "codigo_unidade_gestora", "descricao_unidade_gestora"], as_index=False).agg(
            quantidade_registros=("_row_hash", "count"), valor_vantagem_cents=("valor_vantagem_cents", "sum"), matriculas_distintas=("matricula_key", "nunique")
        ),
        "mart_vantagens_cargo": fact.merge(dim_cargo, on="cargo_key", suffixes=("", "_dim")).groupby(["ano_mes", "tipo_cargo_dim", "codigo_cargo", "descricao_cargo_limpa"], as_index=False).agg(
            quantidade_registros=("_row_hash", "count"), valor_vantagem_cents=("valor_vantagem_cents", "sum"), matriculas_distintas=("matricula_key", "nunique")
        ).rename(columns={"tipo_cargo_dim": "tipo_cargo"}),
    }

    paths = {}
    for name, table in outputs.items():
        path = settings.gold_dir / f"{name}.parquet"
        table.to_parquet(path, index=False, engine="pyarrow")
        paths[name] = str(path)

    metadata = {
        "asset": "gold_model",
        "input_path": str(silver["path"]),
        "tables": {name: {"path": path, "row_count": int(len(outputs[name]))} for name, path in paths.items()},
    }
    write_json(settings.metadata_dir / "gold_model.json", metadata)
    return {"paths": paths, **metadata}


def materialize_semantic(gold: dict[str, Any] | None = None, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    ensure_data_dirs(settings)
    gold = gold or materialize_gold(settings=settings)
    db_path = settings.duckdb_path
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))
    try:
        con.execute("CREATE SCHEMA gold")
        con.execute("CREATE SCHEMA semantic")
        for table, path in gold["paths"].items():
            con.execute(f"CREATE TABLE gold.{table} AS SELECT * FROM read_parquet(?)", [Path(path).as_posix()])

        con.execute(
            """
            CREATE VIEW semantic.vw_overview AS
            SELECT
              COUNT(*)::BIGINT AS quantidade_registros,
              COUNT(DISTINCT matricula_key)::BIGINT AS matriculas_distintas,
              COUNT(DISTINCT municipio_key)::BIGINT AS municipios_distintos,
              COUNT(DISTINCT unidade_gestora_key)::BIGINT AS unidades_gestoras_distintas,
              SUM(CAST(valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_total,
              AVG(CAST(valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_medio,
              MEDIAN(CAST(valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_mediano,
              MAX(ano_mes) AS ultima_competencia
            FROM gold.fct_vantagens
            """
        )
        con.execute(
            """
            CREATE VIEW semantic.vw_municipios AS
            SELECT m.nome_municipio,
                   COUNT(*)::BIGINT AS quantidade_registros,
                   COUNT(DISTINCT f.matricula_key)::BIGINT AS matriculas_distintas,
                   SUM(CAST(f.valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_total,
                   AVG(CAST(f.valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_medio
            FROM gold.fct_vantagens f
            JOIN gold.dim_municipio m USING (municipio_key)
            GROUP BY 1
            """
        )
        con.execute(
            """
            CREATE VIEW semantic.vw_unidades_gestoras AS
            SELECT u.nome_municipio, u.codigo_unidade_gestora, u.descricao_unidade_gestora,
                   COUNT(*)::BIGINT AS quantidade_registros,
                   COUNT(DISTINCT f.matricula_key)::BIGINT AS matriculas_distintas,
                   SUM(CAST(f.valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_total,
                   AVG(CAST(f.valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_medio
            FROM gold.fct_vantagens f
            JOIN gold.dim_unidade_gestora u USING (unidade_gestora_key)
            GROUP BY 1,2,3
            """
        )
        con.execute(
            """
            CREATE VIEW semantic.vw_cargos AS
            SELECT c.tipo_cargo, c.codigo_cargo, c.descricao_cargo_limpa,
                   COUNT(*)::BIGINT AS quantidade_registros,
                   COUNT(DISTINCT f.matricula_key)::BIGINT AS matriculas_distintas,
                   SUM(CAST(f.valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_total,
                   AVG(CAST(f.valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_medio
            FROM gold.fct_vantagens f
            JOIN gold.dim_cargo c USING (cargo_key)
            GROUP BY 1,2,3
            """
        )
        con.execute(
            """
            CREATE VIEW semantic.vw_evolucao_mensal AS
            SELECT ano_mes,
                   COUNT(*)::BIGINT AS quantidade_registros,
                   COUNT(DISTINCT matricula_key)::BIGINT AS matriculas_distintas,
                   SUM(CAST(valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_total,
                   AVG(CAST(valor_vantagem_decimal AS DECIMAL(18,2))) AS valor_vantagem_medio
            FROM gold.fct_vantagens
            GROUP BY 1
            ORDER BY 1
            """
        )
        report_path = settings.metadata_dir / "data_quality_report.json"
        if report_path.exists():
            con.execute("CREATE TABLE semantic.data_quality_report AS SELECT * FROM read_json_auto(?)", [report_path.as_posix()])
            con.execute("CREATE VIEW semantic.vw_data_quality AS SELECT * FROM semantic.data_quality_report")
        else:
            con.execute("CREATE VIEW semantic.vw_data_quality AS SELECT 'missing' AS overall_status")

        views = con.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='semantic' ORDER BY table_name").fetchall()
        ready = {"asset": "semantic_ready", "duckdb_path": str(db_path), "semantic_views": [f"{s}.{t}" for s, t in views]}
        write_json(settings.metadata_dir / "semantic_ready.json", ready)
        return ready
    finally:
        con.close()


def run_full_pipeline(settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    raw = materialize_raw(settings)
    bronze = materialize_bronze(raw, settings)
    silver = materialize_silver(bronze, settings)
    gold = materialize_gold(silver, settings)
    semantic = materialize_semantic(gold, settings)
    return {"raw": raw, "bronze": bronze, "silver": silver, "gold": gold, "semantic": semantic}
