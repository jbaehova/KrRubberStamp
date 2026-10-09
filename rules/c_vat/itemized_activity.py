"""Restore bounded, final domestic supply prices from literal invoice lines.

These are explicit private billing terms. Activity joins and all VAT law and
rounding remain the existing evidence interpreter and exact VAT engine's work.
"""

from copy import deepcopy
from datetime import date

from . import document_reconciliation, engine, evidence

CONTRACT = "vat_itemized_activity_evidence_v1"
RULE_ID = "C_VAT_ITEMIZED_ACTIVITY"
MAX_PRICE = 1_000_000_000
MAX_TRANSACTION_SUPPLY = 10_000_000_000
SOURCE_REQUIRED = {
    "source_contract",
    "billing_policy",
    "taxpayer_type",
    "period_start",
    "period_end",
    "business_name",
    "business_type",
    "consumer_facing_business",
    "receipt_credit_previously_claimed",
    "prepaid_assessed_vat",
    "operations",
    "activities",
    "transactions",
}
SOURCE_OPTIONAL = {
    "scope_note",
    "domain",
    "synthetic_id",
    "reference_period",
    "prior_year_site_supply_base",
    "prior_declared_vat_paid",
    "vehicle_registry",
    "supplier_status_records",
    "site_year_records",
    "filing_site_id",
}
TRANSACTION_REQUIRED = {
    "transaction_id",
    "document_id",
    "direction",
    "date",
    "description",
    "taxable",
    "evidence",
    "invoice_issued",
    "vat_separately_stated",
    "counterparty_consumer",
    "invoice_lines",
    "document_discount",
    "freight_supply",
}
TRANSACTION_OPTIONAL = {
    "activity_id",
    "supplier_id",
    "supplier_general",
    "vehicle_id",
    "vehicle_subject_excise",
    "vehicle_direct_business",
}
LINE_FIELDS = {
    "line_id",
    "description",
    "quantity",
    "unit_supply_price",
    "unit_discount",
    "line_discount",
}
DERIVED = document_reconciliation.DERIVED | {
    "amount",
    "includes_vat",
    "invoice_total",
    "line_supply",
    "merchandise_supply",
    "final_supply",
    "final_vat",
    "final_gross",
}


def _text(value, field):
    if type(value) is not str or not value.strip():
        raise ValueError(f"Itemized VAT requires nonempty {field}")
    return value


def _date(value, field):
    _text(value, field)
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Itemized VAT dates must use YYYY-MM-DD")
    return parsed


def _integer(value, field, minimum=0, maximum=None):
    if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"Itemized VAT {field} exceeds its strict integer bounds")
    return value


def _raw_only(value):
    if type(value) is dict:
        if DERIVED & value.keys():
            raise ValueError("Itemized VAT source exposes a derived amount or decision")
        if "source_contract" in value:
            raise ValueError("Nested source contracts are outside itemized VAT scope")
        for child in value.values():
            _raw_only(child)
    elif type(value) is list:
        for child in value:
            _raw_only(child)


def _invoice(row):
    lines = row["invoice_lines"]
    if type(lines) is not list or not 1 <= len(lines) <= 6:
        raise ValueError("Itemized VAT invoice needs one to six literal lines")
    identities, calculations = set(), []
    for line in lines:
        if type(line) is not dict or set(line) != LINE_FIELDS:
            raise ValueError("Itemized VAT line has unknown or missing fields")
        identity = _text(line["line_id"], "line_id")
        _text(line["description"], "line description")
        if identity in identities:
            raise ValueError("Duplicate invoice line_id")
        identities.add(identity)
        quantity = _integer(line["quantity"], "quantity", 1, 10_000)
        price = _integer(line["unit_supply_price"], "unit_supply_price", maximum=MAX_PRICE)
        discount = _integer(line["unit_discount"], "unit_discount", maximum=price)
        principal = _integer(quantity * price, "line principal", maximum=MAX_PRICE)
        after_unit = quantity * (price - discount)
        line_discount = _integer(line["line_discount"], "line_discount", maximum=after_unit)
        calculations.append(
            {
                "line_id": identity,
                "quantity": quantity,
                "unit_supply_price": price,
                "unit_discount": discount,
                "line_principal": principal,
                "after_unit_discount": after_unit,
                "line_discount": line_discount,
                "line_supply": after_unit - line_discount,
            }
        )
    merchandise = sum(line["line_supply"] for line in calculations)
    discount = _integer(row["document_discount"], "document_discount", maximum=merchandise)
    freight = _integer(row["freight_supply"], "freight_supply", maximum=MAX_PRICE)
    supply = _integer(
        merchandise - discount + freight, "transaction supply", 1, MAX_TRANSACTION_SUPPLY
    )
    if supply % 10:
        raise ValueError("Itemized final supply must admit an exact 10% integer-won VAT split")
    return {
        "transaction_id": row["transaction_id"],
        "document_id": row["document_id"],
        "lines": sorted(calculations, key=lambda line: line["line_id"]),
        "merchandise_supply": merchandise,
        "document_discount": discount,
        "freight_supply": freight,
        "final_supply": supply,
        "final_vat": supply // 10,
        "final_gross": supply * 11 // 10,
    }


def _canonical(source):
    result = deepcopy(source)
    result["transactions"].sort(key=lambda row: (row["transaction_id"], row["document_id"]))
    for row in result["transactions"]:
        row["invoice_lines"].sort(key=lambda line: line["line_id"])
    result["operations"].sort(key=lambda row: row["operation_id"])
    result["activities"].sort(key=lambda row: row["activity_id"])
    for activity in result["activities"]:
        activity["document_ids"].sort()
        activity["participants"].sort(key=lambda row: (row["name"], row["organization"]))
    for field, keys in (
        ("vehicle_registry", ("vehicle_id", "valid_from", "valid_to")),
        ("supplier_status_records", ("supplier_id", "valid_from", "valid_to")),
        ("site_year_records", ("site_id", "year")),
    ):
        if field in result:
            result[field].sort(key=lambda row: tuple(row.get(key, "") for key in keys))
    return result


def _prepare(source):
    if type(source) is not dict or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown itemized VAT activity contract")
    if not SOURCE_REQUIRED <= source.keys() or set(source) - SOURCE_REQUIRED - SOURCE_OPTIONAL:
        raise ValueError("Itemized VAT source has unknown or missing fields")
    for value in source.values():
        _raw_only(value)
    for field in ("billing_policy", "business_name", "business_type", "taxpayer_type"):
        _text(source[field], field)
    if source["taxpayer_type"] != "general" or source["business_type"] not in {
        "individual",
        "corporation",
    }:
        raise ValueError("Itemized VAT supports general individual or corporation taxpayers")
    if (
        _date(source["period_start"], "period_start"),
        _date(source["period_end"], "period_end"),
    ) != (
        date(2026, 1, 1),
        date(2026, 6, 30),
    ):
        raise ValueError("Itemized VAT supports 2026-H1 only")
    if type(source["consumer_facing_business"]) is not bool:
        raise ValueError("Itemized consumer_facing_business must be a strict boolean")
    for field in ("scope_note", "domain", "synthetic_id", "reference_period", "filing_site_id"):
        if field in source:
            _text(source[field], field)
    if "domain" in source and source["domain"] != "C_vat":
        raise ValueError("Itemized domain conflicts with C_vat")
    if "reference_period" in source and source["reference_period"] != "2026-H1":
        raise ValueError("Itemized reference_period conflicts with 2026-H1")
    for field in (
        "receipt_credit_previously_claimed",
        "prepaid_assessed_vat",
        "prior_year_site_supply_base",
        "prior_declared_vat_paid",
    ):
        if field in source:
            _integer(source[field], field)
    if "prior_year_site_supply_base" not in source and "site_year_records" not in source:
        raise ValueError("Itemized VAT requires prior-year amount or site register")
    rows = source["transactions"]
    if type(rows) is not list or not 1 <= len(rows) <= 32:
        raise ValueError("Itemized VAT needs one to 32 document rows")
    by_document, amounts, duplicate_ids = {}, {}, set()
    for row in rows:
        if (
            type(row) is not dict
            or not TRANSACTION_REQUIRED <= row.keys()
            or set(row) - TRANSACTION_REQUIRED - TRANSACTION_OPTIONAL
        ):
            raise ValueError("Itemized VAT transaction has unknown or missing fields")
        for field in ("transaction_id", "document_id", "description"):
            _text(row[field], field)
        for field in ("activity_id", "supplier_id", "vehicle_id"):
            if field in row:
                _text(row[field], field)
        _date(row["date"], "transaction date")
        if _text(row["direction"], "direction") not in {"sale", "purchase"}:
            raise ValueError("Unsupported itemized direction")
        if _text(row["evidence"], "evidence") not in engine.EVIDENCE:
            raise ValueError("Unsupported itemized evidence")
        for field in (
            "taxable",
            "invoice_issued",
            "vat_separately_stated",
            "counterparty_consumer",
            "supplier_general",
            "vehicle_subject_excise",
            "vehicle_direct_business",
        ):
            if field in row and type(row[field]) is not bool:
                raise ValueError(f"Itemized {field} must be a strict boolean")
        if row["taxable"] is not True:
            raise ValueError("Itemized VAT supports taxable domestic supplies only")
        calculation = _invoice(row)
        identity = row["document_id"]
        if identity in by_document:
            if by_document[identity] != row:
                raise ValueError("Conflicting duplicate itemized document_id")
            duplicate_ids.add(identity)
        else:
            by_document[identity] = deepcopy(row)
            amounts[identity] = calculation
    if len({row["transaction_id"] for row in by_document.values()}) > 16:
        raise ValueError("Itemized VAT supports at most 16 actual transactions")
    deduplicated = deepcopy(source)
    deduplicated["transactions"] = list(by_document.values())
    # Validate activities and registers before sorting their literal containers.
    provisional = deepcopy(deduplicated)
    provisional["source_contract"] = evidence.CONTRACT
    for row in provisional["transactions"]:
        calculation = amounts[row["document_id"]]
        for field in ("invoice_lines", "document_discount", "freight_supply"):
            row.pop(field)
        row.update(amount=calculation["final_supply"], includes_vat=False)
        if row["direction"] == "sale":
            row.setdefault("supplier_general", True)
            row.setdefault("vehicle_subject_excise", False)
            row.setdefault("vehicle_direct_business", False)
    normalized = evidence.interpret(provisional)
    # Same actual identity may have different invoice presentation, never
    # different actual activity, supplier/vehicle identity or final supply.
    actuals = {}
    for row in normalized["transactions"]:
        keys = {
            "direction",
            "date",
            "amount",
            "taxable",
            "counterparty_consumer",
            "activity_id",
            "supplier_id",
            "vehicle_id",
        }
        actual = {key: row.get(key) for key in keys}
        identity = row["transaction_id"]
        if identity in actuals and actuals[identity] != actual:
            raise ValueError("Conflicting duplicate itemized actual transaction")
        actuals[identity] = actual
    canonical = _canonical(deduplicated)
    # Normalize again in canonical order for deterministic complete traces.
    provisional = deepcopy(canonical)
    provisional["source_contract"] = evidence.CONTRACT
    for row in provisional["transactions"]:
        calculation = amounts[row["document_id"]]
        for field in ("invoice_lines", "document_discount", "freight_supply"):
            row.pop(field)
        row.update(amount=calculation["final_supply"], includes_vat=False)
        if row["direction"] == "sale":
            row.setdefault("supplier_general", True)
            row.setdefault("vehicle_subject_excise", False)
            row.setdefault("vehicle_direct_business", False)
    normalized = evidence.interpret(provisional)
    return canonical, provisional, normalized, amounts, duplicate_ids


def calculate(source):
    """Return the unchanged eleven VAT answer fields and factual derivation."""
    try:
        canonical, provisional, normalized, amounts, duplicate_ids = _prepare(source)
        answer, tax_trace = engine.calculate(normalized)
        trace = [
            {
                "rule_id": RULE_ID,
                "inputs": canonical,
                "output": {
                    "invoice_amounts": [amounts[key] for key in sorted(amounts)],
                    "deduplicated_document_ids": sorted(duplicate_ids),
                },
            },
            evidence.derivation_trace(provisional, normalized),
            *tax_trace,
        ]
        return deepcopy(answer), deepcopy(trace)
    except (KeyError, TypeError) as error:
        raise ValueError("Malformed itemized VAT raw source") from error
