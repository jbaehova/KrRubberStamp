"""Compare complete item carts under an explicit, private purchasing policy.

This bounded contract applies synthetic purchasing terms. Its VAT-labelled
arithmetic does not decide tax filing or input-tax eligibility.
"""

from copy import deepcopy
from datetime import timedelta
from itertools import product

from rules.d_extract.engine import normalize_vendor
from rules.d_extract.procurement import _date, _integer, _split, _text

CONTRACT = "extract_cart_procurement_v1"
RULE_ID = "D.cart_procurement_comparison"

PARENT_FIELDS = {
    "source_contract",
    "processing_policy",
    "order_date",
    "latest_delivery_date",
    "items",
    "vendors",
    "offers",
}
ITEM_FIELDS = {"item_id", "name", "base_unit", "required_units"}
VENDOR_FIELDS = {
    "vendor_id",
    "name",
    "shipping_price",
    "shipping_price_includes_vat",
    "free_shipping_at",
}
OFFER_FIELDS = {
    "quote_id",
    "item_id",
    "vendor_id",
    "valid_from",
    "valid_until",
    "pack_units",
    "pack_price",
    "price_includes_vat",
    "minimum_packs",
    "stock_packs",
    "lead_days",
}


def _boolean(value, name):
    if type(value) is not bool:
        raise ValueError(f"Cart procurement {name} must be a boolean")


def _rows(value, fields, identity_field, validate):
    if not isinstance(value, list) or not value:
        raise ValueError(f"Cart procurement {identity_field} rows must be a nonempty list")
    originals, duplicates = {}, set()
    for row in value:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError(f"Cart procurement {identity_field} has unknown or missing fields")
        identity = _text(row[identity_field], identity_field)
        validate(row)
        if identity in originals:
            original = originals[identity]
            if original != row or any(type(original[k]) is not type(row[k]) for k in fields):
                raise ValueError(
                    f"Conflicting duplicate cart procurement {identity_field}: {identity}"
                )
            duplicates.add(identity)
        originals[identity] = row
    return [originals[key] for key in sorted(originals)], sorted(duplicates)


def _item(row):
    _text(row["name"], "item name")
    _text(row["base_unit"], "base_unit")
    _integer(row["required_units"], "required_units", 1)


def _vendor(row):
    name = _text(row["name"], "vendor name")
    if not normalize_vendor(name):
        raise ValueError("Cart procurement vendor normalizes to an empty identity")
    _integer(row["shipping_price"], "shipping_price")
    _boolean(row["shipping_price_includes_vat"], "shipping_price_includes_vat")
    if row["free_shipping_at"] is not None:
        _integer(row["free_shipping_at"], "free_shipping_at")


def _offer(row):
    _text(row["item_id"], "item_id")
    _text(row["vendor_id"], "vendor_id")
    if _date(row["valid_from"], "valid_from") > _date(row["valid_until"], "valid_until"):
        raise ValueError("Cart procurement validity starts after it ends")
    for field in ("pack_units", "minimum_packs"):
        _integer(row[field], field, 1)
    for field in ("pack_price", "stock_packs", "lead_days"):
        _integer(row[field], field)
    _boolean(row["price_includes_vat"], "price_includes_vat")


def _evaluate(offer, item, vendor, order_day, latest_day):
    packs = max(
        (item["required_units"] + offer["pack_units"] - 1) // offer["pack_units"],
        offer["minimum_packs"],
    )
    supply, vat = _split(packs * offer["pack_price"], offer["price_includes_vat"])
    try:
        delivery_day = order_day + timedelta(days=offer["lead_days"])
    except OverflowError as error:
        raise ValueError("Cart procurement delivery date is outside the calendar range") from error
    valid = (
        _date(offer["valid_from"], "valid_from")
        <= order_day
        <= _date(offer["valid_until"], "valid_until")
    )
    stock = offer["stock_packs"] >= packs
    timely = delivery_day <= latest_day
    return {
        "quote_id": offer["quote_id"],
        "item_id": item["item_id"],
        "vendor_id": vendor["vendor_id"],
        "vendor": normalize_vendor(vendor["name"]),
        "packs": packs,
        "obtained_units": packs * offer["pack_units"],
        "leftover_units": packs * offer["pack_units"] - item["required_units"],
        "merchandise_supply": supply,
        "merchandise_vat": vat,
        "merchandise_total": supply + vat,
        "delivery_date": delivery_day.isoformat(),
        "valid_on_order": valid,
        "stock_sufficient": stock,
        "delivered_in_time": timely,
        "eligible": valid and stock and timely,
    }


def _cart_totals(selected, vendors):
    rows = []
    for vendor_id in sorted({offer["vendor_id"] for offer in selected}):
        vendor = vendors[vendor_id]
        offers = [offer for offer in selected if offer["vendor_id"] == vendor_id]
        supply = sum(offer["merchandise_supply"] for offer in offers)
        vat = sum(offer["merchandise_vat"] for offer in offers)
        threshold = vendor["free_shipping_at"]
        free = threshold is not None and supply + vat >= threshold
        shipping_supply, shipping_vat = _split(
            0 if free else vendor["shipping_price"], vendor["shipping_price_includes_vat"]
        )
        rows.append(
            {
                "vendor_id": vendor_id,
                "vendor": normalize_vendor(vendor["name"]),
                "merchandise_supply": supply,
                "merchandise_vat": vat,
                "merchandise_total": supply + vat,
                "shipping_free": free,
                "shipping_supply": shipping_supply,
                "shipping_vat": shipping_vat,
                "shipping_total": shipping_supply + shipping_vat,
                "supply": supply + shipping_supply,
                "vat": vat + shipping_vat,
                "total": supply + vat + shipping_supply + shipping_vat,
            }
        )
    return rows


def calculate(source: dict) -> tuple[dict, list[dict]]:
    """Evaluate every eligible complete cart and return a canonical decision trace."""
    if not isinstance(source, dict) or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown cart procurement source contract")
    if set(source) != PARENT_FIELDS:
        raise ValueError("Cart procurement source has unknown or missing fields")
    _text(source["processing_policy"], "visible processing policy")
    order_day = _date(source["order_date"], "order_date")
    latest_day = _date(source["latest_delivery_date"], "latest_delivery_date")
    if latest_day < order_day:
        raise ValueError("Cart procurement latest delivery date predates its order")
    items, duplicate_items = _rows(source["items"], ITEM_FIELDS, "item_id", _item)
    vendors, duplicate_vendors = _rows(source["vendors"], VENDOR_FIELDS, "vendor_id", _vendor)
    offers, duplicate_offers = _rows(source["offers"], OFFER_FIELDS, "quote_id", _offer)
    if not 2 <= len(items) <= 4:
        raise ValueError("Cart procurement requires 2..4 unique items")
    if not 1 <= len(vendors) <= 8:
        raise ValueError("Cart procurement requires 1..8 unique vendors")
    item_map = {row["item_id"]: row for row in items}
    vendor_map = {row["vendor_id"]: row for row in vendors}
    by_item = {item_id: [] for item_id in item_map}
    comparisons = []
    for offer in offers:
        if offer["item_id"] not in item_map or offer["vendor_id"] not in vendor_map:
            raise ValueError("Cart procurement offer has a dangling item or vendor reference")
        row = _evaluate(
            offer,
            item_map[offer["item_id"]],
            vendor_map[offer["vendor_id"]],
            order_day,
            latest_day,
        )
        comparisons.append(row)
        by_item[row["item_id"]].append(row)
    if any(not 1 <= len(rows) <= 6 for rows in by_item.values()):
        raise ValueError("Cart procurement requires 1..6 unique offers per item")
    carts = []
    for selected in product(
        *([row for row in by_item[item_id] if row["eligible"]] for item_id in sorted(item_map))
    ):
        totals = _cart_totals(selected, vendor_map)
        total = sum(row["total"] for row in totals)
        tie = tuple((row["vendor"], row["vendor_id"], row["quote_id"]) for row in selected)
        carts.append((total, tie, selected, totals))
    carts.sort(key=lambda cart: (cart[0], cart[1]))
    chosen = carts[0] if carts else None
    answer = {
        "offer_comparisons": comparisons,
        "chosen_offers": deepcopy(list(chosen[2])) if chosen else [],
        "vendor_cart_totals": chosen[3] if chosen else [],
        "supply_total": sum(row["supply"] for row in chosen[3]) if chosen else None,
        "vat_total": sum(row["vat"] for row in chosen[3]) if chosen else None,
        "grand_total": chosen[0] if chosen else None,
        "feasible_cart_count": len(carts),
    }
    canonical = deepcopy(source)
    for field, identity in (("items", "item_id"), ("vendors", "vendor_id"), ("offers", "quote_id")):
        canonical[field].sort(key=lambda row: row[identity])
    trace = {
        "rule_id": RULE_ID,
        "inputs": canonical,
        "output": {
            "deduplicated_item_ids": duplicate_items,
            "deduplicated_vendor_ids": duplicate_vendors,
            "deduplicated_quote_ids": duplicate_offers,
            "selection": {
                "tie_break_fields": ["grand_total", "vendor_name_vendor_id_quote_id_per_item_id"],
                "evaluated_carts": [
                    {"grand_total": cart[0], "tie_tuple": [list(key) for key in cart[1]]}
                    for cart in carts
                ],
                "chosen_tie_tuple": [list(key) for key in chosen[1]] if chosen else None,
                "reason": "lowest_complete_total_then_per_item_vendor_and_quote"
                if chosen
                else "no_feasible_complete_cart",
            },
            "comparison": deepcopy(answer),
        },
    }
    return answer, [trace]
