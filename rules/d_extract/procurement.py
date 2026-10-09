"""Compare exact costs under an explicitly stated synthetic purchasing policy.

VAT-labelled components implement the private arithmetic convention in this
contract. They do not decide legal tax filing or input-tax eligibility.
"""

from copy import deepcopy
from datetime import date, timedelta
import re
import unicodedata

from rules.d_extract.engine import normalize_vendor, split_vat

CONTRACT = "extract_procurement_v1"
RULE_ID = "D.procurement_comparison"

QUOTE_FIELDS = {
    "quote_id",
    "vendor",
    "valid_from",
    "valid_until",
    "pack_units",
    "pack_price",
    "price_includes_vat",
    "minimum_packs",
    "shipping_price",
    "shipping_price_includes_vat",
    "free_shipping_at",
    "stock_packs",
    "lead_days",
}


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Procurement evidence requires nonempty {name}")
    return value


def _date(value, name):
    value = _text(value, name)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Procurement {name} must use YYYY-MM-DD") from error
    if parsed.isoformat() != value:
        raise ValueError(f"Procurement {name} must use YYYY-MM-DD")
    return parsed


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"Procurement {name} must be an integer at least {minimum}")
    return value


def _split(amount, includes_vat):
    return split_vat(amount) if includes_vat else (amount, amount // 10)


def _quotes(value):
    if not isinstance(value, list) or not value:
        raise ValueError("Procurement quotes must be a nonempty list")
    originals = {}
    duplicates = set()
    for row in value:
        if not isinstance(row, dict) or set(row) != QUOTE_FIELDS:
            raise ValueError("Procurement quote has unknown or missing fields")
        identity = _text(row["quote_id"], "quote_id")
        vendor = _text(row["vendor"], "vendor")
        if not normalize_vendor(vendor):
            raise ValueError("Procurement vendor normalizes to an empty identity")
        start = _date(row["valid_from"], "valid_from")
        end = _date(row["valid_until"], "valid_until")
        if start > end:
            raise ValueError("Procurement validity starts after it ends")
        for field in ("pack_units", "minimum_packs"):
            _integer(row[field], field, 1)
        for field in ("pack_price", "shipping_price", "stock_packs", "lead_days"):
            _integer(row[field], field)
        if row["free_shipping_at"] is not None:
            _integer(row["free_shipping_at"], "free_shipping_at")
        for field in ("price_includes_vat", "shipping_price_includes_vat"):
            if type(row[field]) is not bool:
                raise ValueError(f"Procurement {field} must be a boolean")
        if identity in originals:
            original = originals[identity]
            if original != row or any(
                type(original[field]) is not type(row[field]) for field in QUOTE_FIELDS
            ):
                raise ValueError(f"Conflicting duplicate procurement quote_id: {identity}")
            duplicates.add(identity)
        originals[identity] = row
    return [originals[key] for key in sorted(originals)], sorted(duplicates)


def calculate(source: dict) -> tuple[dict, list[dict]]:
    """Return quote comparisons and one canonical, source-grounded trace row."""
    if not isinstance(source, dict) or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown procurement source contract")
    _text(source.get("processing_policy"), "visible processing policy")
    item = _text(source.get("item"), "item")
    normalized_item = re.sub(r"\s+", "", unicodedata.normalize("NFKC", item)).casefold()
    if not normalized_item:
        raise ValueError("Procurement item normalizes to an empty identity")
    base_unit = _text(source.get("base_unit"), "base_unit")
    required = _integer(source.get("required_units"), "required_units", 1)
    order_day = _date(source.get("order_date"), "order_date")
    latest_day = _date(source.get("latest_delivery_date"), "latest_delivery_date")
    if latest_day < order_day:
        raise ValueError("Procurement latest delivery date predates its order")
    quotes, duplicates = _quotes(source.get("quotes"))
    comparisons = []
    arithmetic = []
    for quote in quotes:
        required_packs = (required + quote["pack_units"] - 1) // quote["pack_units"]
        packs = max(quote["minimum_packs"], required_packs)
        obtained = packs * quote["pack_units"]
        merchandise_amount = packs * quote["pack_price"]
        merchandise_supply, merchandise_vat = _split(
            merchandise_amount, quote["price_includes_vat"]
        )
        merchandise_total = merchandise_supply + merchandise_vat
        threshold = quote["free_shipping_at"]
        shipping_free = threshold is not None and merchandise_total >= threshold
        shipping_amount = 0 if shipping_free else quote["shipping_price"]
        shipping_supply, shipping_vat = _split(
            shipping_amount, quote["shipping_price_includes_vat"]
        )
        shipping_total = shipping_supply + shipping_vat
        try:
            delivery_day = order_day + timedelta(days=quote["lead_days"])
        except OverflowError as error:
            raise ValueError("Procurement delivery date is outside the calendar range") from error
        valid = (
            _date(quote["valid_from"], "valid_from")
            <= order_day
            <= _date(quote["valid_until"], "valid_until")
        )
        stock = quote["stock_packs"] >= packs
        timely = delivery_day <= latest_day
        supply = merchandise_supply + shipping_supply
        vat = merchandise_vat + shipping_vat
        total = supply + vat
        comparisons.append(
            {
                "quote_id": quote["quote_id"],
                "vendor": normalize_vendor(quote["vendor"]),
                "packs": packs,
                "obtained_units": obtained,
                "leftover_units": obtained - required,
                "merchandise_supply": merchandise_supply,
                "merchandise_vat": merchandise_vat,
                "merchandise_total": merchandise_total,
                "shipping_supply": shipping_supply,
                "shipping_vat": shipping_vat,
                "shipping_total": shipping_total,
                "supply": supply,
                "vat": vat,
                "total": total,
                "delivery_date": delivery_day.isoformat(),
                "valid_on_order": valid,
                "stock_sufficient": stock,
                "delivered_in_time": timely,
                "eligible": valid and stock and timely,
            }
        )
        arithmetic.append(
            {
                "quote_id": quote["quote_id"],
                "required_packs_before_minimum": required_packs,
                "minimum_packs": quote["minimum_packs"],
                "packs_after_minimum": packs,
                "pack_units": quote["pack_units"],
                "merchandise_amount_before_vat_split": merchandise_amount,
                "price_includes_vat": quote["price_includes_vat"],
                "free_shipping_at": threshold,
                "shipping_threshold_basis": merchandise_total,
                "shipping_free": shipping_free,
                "shipping_amount_before_vat_split": shipping_amount,
                "shipping_price_includes_vat": quote["shipping_price_includes_vat"],
                "lead_calendar_days": quote["lead_days"],
            }
        )
    eligible = sorted(
        (row for row in comparisons if row["eligible"]),
        key=lambda row: (row["total"], row["vendor"], row["quote_id"]),
    )
    chosen = eligible[0] if eligible else None
    answer = {
        "quote_comparisons": comparisons,
        "chosen_quote_id": chosen["quote_id"] if chosen else None,
        "chosen_vendor": chosen["vendor"] if chosen else None,
        "chosen_total": chosen["total"] if chosen else None,
        "chosen_leftover_units": chosen["leftover_units"] if chosen else None,
        "eligible_quote_count": len(eligible),
    }
    canonical_inputs = deepcopy(source)
    canonical_inputs["quotes"].sort(key=lambda row: row["quote_id"])
    trace = {
        "rule_id": RULE_ID,
        "inputs": canonical_inputs,
        "output": {
            "normalized_item": normalized_item,
            "base_unit": base_unit,
            "deduplicated_quote_ids": duplicates,
            "comparison_arithmetic": arithmetic,
            "selection": {
                "tie_break_fields": ["total", "vendor", "quote_id"],
                "eligible_tie_break_tuples": [
                    [row["total"], row["vendor"], row["quote_id"]] for row in eligible
                ],
                "chosen_tie_break_tuple": (
                    [chosen["total"], chosen["vendor"], chosen["quote_id"]] if chosen else None
                ),
                "reason": "lowest_total_then_vendor_then_quote_id"
                if chosen
                else "no_eligible_quote",
            },
            "comparison": deepcopy(answer),
        },
    }
    return answer, [trace]
