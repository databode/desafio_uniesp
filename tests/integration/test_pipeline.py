from pathlib import Path

import duckdb

from uniesp_data_platform.config import Settings
from uniesp_data_platform.pipeline import run_full_pipeline


def test_fixture_full_pipeline(tmp_path: Path):
    source = Path(__file__).parents[1] / "fixtures" / "servidores_fixture.csv"
    settings = Settings(source_file_path=source, data_root=tmp_path / "data")

    result = run_full_pipeline(settings)

    assert Path(result["raw"]["path"]).exists()
    assert Path(result["bronze"]["path"]).exists()
    assert Path(result["silver"]["path"]).exists()
    assert Path(result["semantic"]["duckdb_path"]).exists()

    with duckdb.connect(result["semantic"]["duckdb_path"], read_only=True) as con:
        overview = con.execute("SELECT quantidade_registros, valor_vantagem_total, matriculas_distintas FROM semantic.vw_overview").fetchone()
        assert overview[0] == 3
        assert str(overview[1]) == "7690.31"
        assert overview[2] == 3
        assert con.execute("SELECT COUNT(*) FROM gold.dim_matricula").fetchone()[0] == 3
        views = {row[0] for row in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='semantic'").fetchall()}
        assert "vw_municipios" in views
        assert "vw_data_quality" in views
