from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.limits import MAX_MONEY

CENTS = Decimal("0.01")


def parse_money(raw):
    """Parse a user-entered amount into a Decimal rounded to 2 places (like DECIMAL(10,2)).

    Rejects NaN/Infinity and anything that does not fit DECIMAL(10,2). Sign checks
    (negative amounts) are the caller's business rule and live in services/.
    """
    try:
        value = Decimal(str(raw).strip())
        if not value.is_finite():
            raise InvalidOperation
        result = value.quantize(CENTS, rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError(f"Invalid amount: {raw!r}")
    if abs(result) > MAX_MONEY:
        raise ValueError(f"Amount is too large (maximum {MAX_MONEY}): {raw!r}")
    return result
