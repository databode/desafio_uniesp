from decimal import Decimal

from uniesp_data_platform.utils.parsing import parse_ano_mes, parse_cargo, parse_date_ddmmyyyy, parse_valor_vantagem


def test_parse_ptbr_decimal_value():
    value, category = parse_valor_vantagem("3.490,31")
    assert value == Decimal("3490.31")
    assert category == "ptbr_decimal_comma"


def test_parse_dot_thousand_integer_value():
    value, category = parse_valor_vantagem("1.700")
    assert value == Decimal("1700")
    assert category == "dot_thousand_integer"


def test_parse_date_ddmmyyyy():
    assert parse_date_ddmmyyyy("02/01/2025").isoformat() == "2025-01-02"


def test_parse_ano_mes():
    ano_mes, competencia = parse_ano_mes("202601")
    assert ano_mes == "202601"
    assert competencia.isoformat() == "2026-01-01"


def test_leading_zero_identifier_stays_string():
    matricula = "000000000000028"
    assert str(matricula) == "000000000000028"


def test_parse_cargo_code_and_description():
    code, description, valid = parse_cargo("00000023 - DIGITADORA")
    assert code == "00000023"
    assert description == "DIGITADORA"
    assert valid is True


def test_parse_cargo_without_pattern():
    code, description, valid = parse_cargo("SEM CODIGO")
    assert code is None
    assert description == "SEM CODIGO"
    assert valid is False
