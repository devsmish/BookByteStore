from decimal import Decimal

import pytest

from app.money import parse_money


@pytest.mark.parametrize("raw,expected", [
    ("10", Decimal("10.00")),
    ("19.9", Decimal("19.90")),
    ("19.999", Decimal("20.00")),  # ROUND_HALF_UP
    (" 5 ", Decimal("5.00")),
    ("0", Decimal("0.00")),
])
def test_parse_money_valid(raw, expected):
    assert parse_money(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "", "   ", "1,2", "1.2.3"])
def test_parse_money_invalid(raw):
    with pytest.raises(ValueError):
        parse_money(raw)
