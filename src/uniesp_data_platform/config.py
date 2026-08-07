from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


@dataclass(frozen=True)
class Settings:
    source_file_path: Path
    data_root: Path

    @property
    def raw_dir(self) -> Path:
        return self.data_root / "raw"

    @property
    def bronze_dir(self) -> Path:
        return self.data_root / "bronze"

    @property
    def silver_dir(self) -> Path:
        return self.data_root / "silver"

    @property
    def gold_dir(self) -> Path:
        return self.data_root / "gold"

    @property
    def semantic_dir(self) -> Path:
        return self.data_root / "semantic"

    @property
    def metadata_dir(self) -> Path:
        return self.data_root / "metadata"

    @property
    def duckdb_path(self) -> Path:
        return self.semantic_dir / "uniesp.duckdb"


def get_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv()

    source = os.getenv("SOURCE_FILE_PATH")
    if not source:
        raise ValueError("SOURCE_FILE_PATH must point to servidores-2026.csv or a compatible fixture CSV.")

    data_root = Path(os.getenv("DATA_ROOT", "./data"))
    return Settings(source_file_path=Path(source).expanduser(), data_root=data_root.expanduser())


def ensure_data_dirs(settings: Settings) -> None:
    for path in [
        settings.raw_dir,
        settings.bronze_dir,
        settings.silver_dir,
        settings.gold_dir,
        settings.semantic_dir,
        settings.metadata_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)
