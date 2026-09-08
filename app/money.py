from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTS = Decimal("0.01")


def parse_money(raw):
    """Parses the monetary amount entered by the user into a Decimal,
    rounded to two decimal places (like DECIMAL(10,2) in the schema)."""
    try:
        value = Decimal(str(raw).strip())
    except InvalidOperation:
        raise ValueError(f"Invalid amount: {raw!r}")
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)
