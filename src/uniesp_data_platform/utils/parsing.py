from __future__ import annotations

import hashlib
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping

CARGO_RE = re.compile(r"^(?P<code>\d+)\s+-\s+(?P<description>.+)$")
ANO_MES_RE = re.compile(r"^\d{6}$")


def clean_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def parse_valor_vantagem(value: object) -> tuple[Decimal | None, str]:
    """Parse pt-BR monetary-like values without using float.

    Rules:
    - `3.490,31` -> Decimal('3490.31')
    - `1.700` -> Decimal('1700') because dot with exactly 3 trailing digits is thousands.
    - `1234` -> Decimal('1234')
    - `1234,56` -> Decimal('1234.56')
    """
    text = clean_string(value)
    if text is None:
        return None, "empty"
    normalized = text
    category = "unknown"
    if "," in text:
        normalized = text.replace(".", "").replace(",", ".")
        category = "ptbr_decimal_comma"
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", text):
        normalized = text.replace(".", "")
        category = "dot_thousand_integer"
    elif re.fullmatch(r"-?\d+", text):
        category = "integer"
    elif re.fullmatch(r"-?\d+\.\d{1,2}", text):
        # Compatibility for synthetic fixtures or future sources; not the observed dominant source format.
        category = "decimal_dot"
    else:
        return None, "invalid"

    try:
        return Decimal(normalized), category
    except InvalidOperation:
        return None, "invalid"


def decimal_to_cents(value: Decimal | None) -> int | None:
    if value is None:
        return None
    return int((value * Decimal("100")).quantize(Decimal("1")))


def parse_date_ddmmyyyy(value: object) -> date | None:
    text = clean_string(value)
    if text is None:
        return None
    try:
        return datetime.strptime(text, "%d/%m/%Y").date()
    except ValueError:
        return None


def parse_ano_mes(value: object) -> tuple[str | None, date | None]:
    text = clean_string(value)
    if text is None or not ANO_MES_RE.fullmatch(text):
        return None, None
    month = int(text[4:6])
    if month < 1 or month > 12:
        return text, None
    return text, date(int(text[:4]), month, 1)


def parse_cargo(value: object) -> tuple[str | None, str | None, bool]:
    text = clean_string(value)
    if text is None:
        return None, None, False
    match = CARGO_RE.match(text)
    if not match:
        return None, text, False
    return match.group("code"), clean_string(match.group("description")), True


def row_hash(row: Mapping[str, object], columns: Iterable[str]) -> str:
    payload = "|".join("" if row.get(col) is None else str(row.get(col)) for col in columns)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
