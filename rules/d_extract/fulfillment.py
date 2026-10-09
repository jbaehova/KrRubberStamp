"""Reconcile synthetic order, receiving, return and payment agreements exactly.

This optional contract describes a stated settlement convention. Its VAT-labelled
amounts are contract arithmetic, not a tax filing or refund eligibility decision.
"""

from collections import defaultdict
from copy import deepcopy
from datetime import date
import re
import unicodedata

from rules.d_extract.engine import normalize_vendor, split_vat

CONTRACT = "extract_fulfillment_v1"
RULE_ID = "D.fulfillment_reconciliation"


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Fulfillment evidence requires {name}")
    return value


def _date(value):
    _text(value, "ISO calendar date")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Fulfillment date must use YYYY-MM-DD")
    return parsed


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"Fulfillment {name} must be an integer at least {minimum}")
    return value


def _rows(value, fields, name):
    if not isinstance(value, list):
        raise ValueError(f"Fulfillment {name} must be a list")
    for row in value:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError(f"Fulfillment {name} has unknown or missing fields")
    return value


def _deduplicate(rows, identity):
    originals = {}
    duplicates = set()
    for row in rows:
        key = _text(row[identity], identity)
        if key in originals:
            if originals[key] != row or any(
                type(originals[key][field]) is not type(value) for field, value in row.items()
            ):
                raise ValueError(f"Conflicting duplicate fulfillment {identity}: {key}")
            duplicates.add(key)
        originals[key] = row
    return [originals[key] for key in sorted(originals)], sorted(duplicates)


def _item(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).casefold()


def calculate(source: dict) -> tuple[dict, list[dict]]:
    """Return stable exact settlements and a source-grounded derivation trace."""
    if not isinstance(source, dict) or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown fulfillment source contract")
    policy = _text(source.get("processing_policy"), "visible processing policy")
    cutoff = _date(source.get("cutoff_date"))
    orders = _rows(source.get("orders"), {"order_id", "vendor", "date", "kind", "lines"}, "orders")
    by_order = {}
    by_line = {}
    for order in orders:
        identity = _text(order["order_id"], "order_id")
        if identity in by_order:
            raise ValueError(f"Duplicate fulfillment order_id: {identity}")
        _text(order["vendor"], "vendor")
        if not normalize_vendor(order["vendor"]):
            raise ValueError("Fulfillment vendor normalizes to an empty identity")
        _date(order["date"])
        if not isinstance(order["kind"], str) or order["kind"] not in {"order", "quote"}:
            raise ValueError("Unsupported fulfillment order kind")
        lines = _rows(
            order["lines"],
            {
                "line_id",
                "item",
                "base_unit",
                "ordered_packages",
                "units_per_package",
                "package_price",
                "price_includes_vat",
            },
            "order lines",
        )
        if not lines:
            raise ValueError("Fulfillment order requires at least one line")
        by_order[identity] = order
        for line in lines:
            line_id = _text(line["line_id"], "line_id")
            key = (identity, line_id)
            if key in by_line:
                raise ValueError(f"Duplicate fulfillment order line: {key}")
            _text(line["item"], "item")
            _text(line["base_unit"], "base_unit")
            _integer(line["ordered_packages"], "ordered_packages", 1)
            _integer(line["units_per_package"], "units_per_package", 1)
            _integer(line["package_price"], "package_price")
            if type(line["price_includes_vat"]) is not bool:
                raise ValueError("Fulfillment VAT inclusion must be a boolean")
            by_line[key] = line

    event_rows = _rows(
        source.get("events"),
        {"event_id", "order_id", "line_id", "kind", "date", "units"},
        "events",
    )
    events, duplicate_events = _deduplicate(event_rows, "event_id")
    accepted_events = []
    excluded_events = []
    for event in events:
        key = (
            _text(event["order_id"], "event order_id"),
            _text(event["line_id"], "event line_id"),
        )
        if key not in by_line:
            raise ValueError(f"Unknown fulfillment event order line: {key}")
        if not isinstance(event["kind"], str) or event["kind"] not in {"received", "returned"}:
            raise ValueError("Unsupported fulfillment event kind")
        day = _date(event["date"])
        _integer(event["units"], "event units", 1)
        order = by_order[key[0]]
        if order["kind"] == "quote":
            raise ValueError("Quote cannot have an actual fulfillment event")
        if day < _date(order["date"]):
            raise ValueError("Fulfillment event predates its order")
        (accepted_events if day <= cutoff else excluded_events).append(event)

    payment_rows = _rows(
        source.get("payments"),
        {"payment_id", "order_id", "date", "status", "amount"},
        "payments",
    )
    payments, duplicate_payments = _deduplicate(payment_rows, "payment_id")
    accepted_payments = []
    excluded_payments = []
    for payment in payments:
        identity = _text(payment["order_id"], "payment order_id")
        if identity not in by_order:
            raise ValueError(f"Unknown fulfillment payment order: {identity}")
        if not isinstance(payment["status"], str) or payment["status"] not in {
            "executed",
            "planned",
        }:
            raise ValueError("Unsupported fulfillment payment status")
        day = _date(payment["date"])
        _integer(payment["amount"], "payment amount")
        order = by_order[identity]
        if payment["status"] == "executed":
            if order["kind"] == "quote":
                raise ValueError("Quote cannot have an executed payment")
            if day < _date(order["date"]):
                raise ValueError("Executed fulfillment payment predates its order")
        included = payment["status"] == "executed" and day <= cutoff
        (accepted_payments if included else excluded_payments).append(payment)

    quantities = defaultdict(lambda: {"received": 0, "returned": 0})
    event_timeline = []
    for event in sorted(
        accepted_events,
        key=lambda row: (row["date"], row["kind"] == "returned", row["event_id"]),
    ):
        key = (event["order_id"], event["line_id"])
        state = quantities[key]
        state[event["kind"]] += event["units"]
        net = state["received"] - state["returned"]
        if net < 0:
            raise ValueError(f"Return exceeds previously received fulfillment units: {key}")
        event_timeline.append({"event_id": event["event_id"], "net_units_after_event": net})

    vendor_amounts = defaultdict(lambda: {"supply": 0, "vat": 0, "total": 0, "paid": 0})
    item_amounts = defaultdict(int)
    settlements = []
    line_arithmetic = []
    for (order_id, line_id), line in sorted(by_line.items()):
        order = by_order[order_id]
        if order["kind"] == "quote":
            continue
        quantity = quantities[(order_id, line_id)]
        net = quantity["received"] - quantity["returned"]
        numerator = line["package_price"] * net
        amount = numerator // line["units_per_package"]
        if line["price_includes_vat"]:
            supply, vat = split_vat(amount)
        else:
            supply, vat = amount, amount // 10
        total = supply + vat
        item = _item(line["item"])
        base_unit = line["base_unit"]
        ordered = line["ordered_packages"] * line["units_per_package"]
        settlements.append(
            {
                "order_id": order_id,
                "line_id": line_id,
                "item": item,
                "base_unit": base_unit,
                "ordered_units": ordered,
                "received_units": quantity["received"],
                "returned_units": quantity["returned"],
                "net_units": net,
                "outstanding_units": ordered - net,
                "supply": supply,
                "vat": vat,
                "total": total,
            }
        )
        item_amounts[(item, base_unit)] += net
        vendor = normalize_vendor(order["vendor"])
        for name, value in (("supply", supply), ("vat", vat), ("total", total)):
            vendor_amounts[vendor][name] += value
        line_arithmetic.append(
            {
                "order_id": order_id,
                "line_id": line_id,
                "package_price_times_net_units": numerator,
                "units_per_package": line["units_per_package"],
                "amount_after_floor": amount,
                "price_includes_vat": line["price_includes_vat"],
                "supply": supply,
                "vat": vat,
                "total": total,
            }
        )
    for payment in accepted_payments:
        vendor = normalize_vendor(by_order[payment["order_id"]]["vendor"])
        vendor_amounts[vendor]["paid"] += payment["amount"]
    vendors = [
        {"vendor": vendor, **amounts, "balance": amounts["total"] - amounts["paid"]}
        for vendor, amounts in sorted(vendor_amounts.items())
    ]
    answer = {
        "line_settlements": settlements,
        "item_quantities": [
            {"item": item, "base_unit": unit, "net_units": net}
            for (item, unit), net in sorted(item_amounts.items())
        ],
        "vendor_balances": vendors,
        "grand_total": sum(row["total"] for row in vendors),
        "payment_total": sum(row["paid"] for row in vendors),
        "balance_total": sum(row["balance"] for row in vendors),
    }
    canonical_orders = []
    for order in sorted(orders, key=lambda row: row["order_id"]):
        copied = deepcopy(order)
        copied["lines"].sort(key=lambda row: row["line_id"])
        canonical_orders.append(copied)
    trace = {
        "rule_id": RULE_ID,
        "inputs": {
            "source_contract": CONTRACT,
            "processing_policy": policy,
            "cutoff_date": source["cutoff_date"],
            "orders": canonical_orders,
            "events": deepcopy(sorted(event_rows, key=lambda row: row["event_id"])),
            "payments": deepcopy(sorted(payment_rows, key=lambda row: row["payment_id"])),
        },
        "output": {
            "accepted_event_ids": sorted(row["event_id"] for row in accepted_events),
            "excluded_after_cutoff_event_ids": sorted(row["event_id"] for row in excluded_events),
            "accepted_payment_ids": sorted(row["payment_id"] for row in accepted_payments),
            "excluded_payment_ids": sorted(row["payment_id"] for row in excluded_payments),
            "deduplicated_event_ids": duplicate_events,
            "deduplicated_payment_ids": duplicate_payments,
            "excluded_quote_order_ids": sorted(
                row["order_id"] for row in orders if row["kind"] == "quote"
            ),
            "event_timeline": event_timeline,
            "line_arithmetic": line_arithmetic,
            "settlement": deepcopy(answer),
        },
    }
    return answer, [trace]
