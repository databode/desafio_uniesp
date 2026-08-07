from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_quality_report(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def checks_as_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for severity, key in [("error", "error_checks"), ("warning", "warning_checks")]:
        for name, value in report.get(key, {}).items():
            rows.append({"check_name": name, "passed": bool(value), "severity": severity})
    if rows:
        return rows
    return [{"check_name": name, "passed": bool(value), "severity": "unknown"} for name, value in report.get("checks", {}).items()]
