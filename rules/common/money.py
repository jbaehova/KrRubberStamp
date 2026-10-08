"""Exact money helpers. Engines select rounding separately for each legal rule."""

from decimal import Decimal, ROUND_FLOOR, ROUND_DOWN
import re
import unicodedata


def floor_won(value):
    return int(Decimal(str(value)).to_integral_value(rounding=ROUND_FLOOR))


def truncate_ten(value):
    return int((Decimal(str(value)) / 10).to_integral_value(rounding=ROUND_DOWN)) * 10


def mul_floor(amount, rate):
    return floor_won(Decimal(str(amount)) * Decimal(str(rate)))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).casefold()
