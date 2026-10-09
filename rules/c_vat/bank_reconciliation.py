"""Match independent VAT returns to a bounded private cash ledger.

The existing VAT contracts own all tax arithmetic. A signed balance here is
only an unmatched private-ledger amount, never an offset or a new tax right.
"""

from collections import defaultdict
from copy import deepcopy
from datetime import date

from . import document_lifecycle, document_reconciliation, engine, evidence, itemized_activity

CONTRACT = "vat_bank_reconciliation_v1"
RULE_ID = "C_VAT_BANK_RECONCILIATION"
MAX_FILINGS = 3
MAX_UNIQUE_TRANSFERS = 100
MAX_TRANSFER_ROWS = 200
SOURCE_FIELDS = {"source_contract", "processing_policy", "as_of_date", "filings", "transfers"}
FILING_FIELDS = {"filing_id", "taxpayer_id", "registration_id", "business_name", "facts"}
TRANSFER_FIELDS = {
    "transfer_id",
    "filing_id",
    "registration_id",
    "date",
    "status",
    "kind",
    "amount",
}
CHILD_CONTRACTS = {
    evidence.CONTRACT,
    document_reconciliation.CONTRACT,
    document_lifecycle.CONTRACT,
    itemized_activity.CONTRACT,
}
CHILD_REQUIRED = {
    "source_contract",
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
}
CHILD_OPTIONAL = {
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
DERIVED_FIELDS = document_reconciliation.DERIVED | {
    "tax_due",
    "paid",
    "received",
    "net_outflow",
    "balance",
    "tax_due_total",
    "paid_total",
    "received_total",
    "balance_total",
    "filing_calculations",
    "registration_settlements",
    "accepted_transfer_ids",
    "excluded_transfer_ids",
    "deduplicated_transfer_ids",
    "selected_document_ids",
    "excluded_document_ids",
    "revoked_document_ids",
    "replacement_relations",
}


def _text(value, field):
    if type(value) is not str or not value.strip():
        raise ValueError(f"VAT bank reconciliation requires nonempty {field}")
    return value


def _date(value):
    _text(value, "ISO date")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("VAT bank reconciliation dates must use YYYY-MM-DD")
    return parsed


def _money(value, field):
    if type(value) is not int or value < 0:
        raise ValueError(f"VAT bank reconciliation requires nonnegative integer {field}")
    return value


def _rows(value, fields, field):
    if type(value) is not list:
        raise ValueError(f"VAT bank reconciliation {field} must be a list")
    for row in value:
        if type(row) is not dict or set(row) != fields:
            raise ValueError(f"VAT bank reconciliation {field} has unknown or missing fields")
    return value


def _no_outcomes(value):
    if isinstance(value, dict):
        if DERIVED_FIELDS & value.keys():
            raise ValueError("VAT bank source exposes a precomputed decision")
        for child in value.values():
            _no_outcomes(child)
    elif isinstance(value, list):
        for child in value:
            _no_outcomes(child)


def _activity_rows(rows):
    """Keep the bounded child's literal ledger free of unvalidated extra fields."""
    required = {
        "transaction_id",
        "document_id",
        "direction",
        "date",
        "description",
        "amount",
        "includes_vat",
        "taxable",
        "evidence",
        "invoice_issued",
        "vat_separately_stated",
        "counterparty_consumer",
    }
    optional = {
        "activity_id",
        "supplier_id",
        "supplier_general",
        "vehicle_id",
        "vehicle_subject_excise",
        "vehicle_direct_business",
    }
    if type(rows) is not list:
        raise ValueError("VAT child transactions must be a list")
    for row in rows:
        if type(row) is not dict or not required <= row.keys() or set(row) - required - optional:
            raise ValueError("VAT child transaction has unknown or missing fields")
        for field in ("transaction_id", "document_id", "description"):
            _text(row[field], field)
        for field in ("activity_id", "supplier_id", "vehicle_id"):
            if field in row:
                _text(row[field], field)
        _date(row["date"])
        _money(row["amount"], "child amount")
        if _text(row["direction"], "child direction") not in {"sale", "purchase"}:
            raise ValueError("Unsupported child transaction direction")
        if _text(row["evidence"], "child evidence") not in engine.EVIDENCE:
            raise ValueError("Unsupported child evidence")
        for field in (
            "includes_vat",
            "taxable",
            "invoice_issued",
            "vat_separately_stated",
            "counterparty_consumer",
            "supplier_general",
            "vehicle_subject_excise",
            "vehicle_direct_business",
        ):
            if field in row and type(row[field]) is not bool:
                raise ValueError(f"Child {field} must be a strict boolean")


def _no_nested_contract(value):
    if isinstance(value, dict):
        if "source_contract" in value:
            raise ValueError("Nested source contracts are outside the VAT bank child scope")
        for child in value.values():
            _no_nested_contract(child)
    elif isinstance(value, list):
        for child in value:
            _no_nested_contract(child)


def _child(facts, business, cutoff):
    if type(facts) is not dict:
        raise ValueError("VAT filing facts must be a literal object")
    contract = _text(facts.get("source_contract"), "child source_contract")
    if contract not in CHILD_CONTRACTS:
        raise ValueError("Unsupported or nested VAT child source contract")
    if contract in {evidence.CONTRACT, itemized_activity.CONTRACT}:
        specific = {"transactions"}
    else:
        specific = {"supplies", "payments", "evidence_documents", "scope_note"}
    if contract == document_lifecycle.CONTRACT:
        specific |= {"processing_date", "document_status_records"}
    if contract == itemized_activity.CONTRACT:
        specific |= {"billing_policy"}
    required = CHILD_REQUIRED | specific
    if not required <= facts.keys() or set(facts) - required - CHILD_OPTIONAL:
        raise ValueError("VAT child source has unknown or missing fields")
    for value in facts.values():
        _no_nested_contract(value)
    if facts["taxpayer_type"] != "general" or type(facts["taxpayer_type"]) is not str:
        raise ValueError("VAT bank source supports explicit general taxpayers only")
    if (_date(facts["period_start"]), _date(facts["period_end"])) != (
        date(2026, 1, 1),
        date(2026, 6, 30),
    ):
        raise ValueError("VAT bank source supports 2026-H1 only")
    if _text(facts["business_name"], "child business_name") != business:
        raise ValueError("VAT filing business_name conflicts with its child")
    if _text(facts["business_type"], "child business_type") not in {"individual", "corporation"}:
        raise ValueError("Unsupported child business_type")
    if type(facts["consumer_facing_business"]) is not bool:
        raise ValueError("Child consumer_facing_business must be a strict boolean")
    for field in ("scope_note", "domain", "synthetic_id", "reference_period", "filing_site_id"):
        if field in facts:
            _text(facts[field], field)
    if "domain" in facts and facts["domain"] != "C_vat":
        raise ValueError("Child domain conflicts with the VAT filing")
    if "reference_period" in facts and facts["reference_period"] != "2026-H1":
        raise ValueError("Child reference_period conflicts with 2026-H1")
    for field in (
        "prior_year_site_supply_base",
        "receipt_credit_previously_claimed",
        "prepaid_assessed_vat",
        "prior_declared_vat_paid",
    ):
        if field in facts:
            _money(facts[field], field)
    if "prior_year_site_supply_base" not in facts and "site_year_records" not in facts:
        raise ValueError("VAT child requires its prior-year amount or site register")
    if contract == document_lifecycle.CONTRACT and _date(facts["processing_date"]) > cutoff:
        raise ValueError("Lifecycle processing_date is after the bank cutoff")
    if contract == evidence.CONTRACT:
        _activity_rows(facts["transactions"])
    if contract == itemized_activity.CONTRACT:
        # The strict itemized validator owns the complete raw child, including
        # invoice prices. No derived engine ledger is accepted as parent input.
        return itemized_activity.calculate(deepcopy(facts))
    # Import only after the allowlist check. Registry can route this optional
    # parent without permitting a child to recurse into another bank contract.
    from KrRubberStamp.registry import calculate as calculate_child

    try:
        return calculate_child("C_vat", deepcopy(facts))
    except (KeyError, TypeError) as error:
        raise ValueError("Invalid raw VAT child fields") from error


def calculate(source: dict) -> tuple[dict, list[dict]]:
    """Return separate registration balances without offsetting their positions."""
    if type(source) is not dict or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown VAT bank reconciliation source contract")
    if set(source) != SOURCE_FIELDS:
        raise ValueError("VAT bank source has unknown or missing fields")
    _no_outcomes(source)
    policy = _text(source["processing_policy"], "visible processing_policy")
    cutoff = _date(source["as_of_date"])
    filings = _rows(source["filings"], FILING_FIELDS, "filings")
    if not 1 <= len(filings) <= MAX_FILINGS:
        raise ValueError("VAT bank source requires one to three independent filings")
    by_id, taxpayers, registrations = {}, set(), set()
    calculations, derivations = [], []
    for filing in sorted(filings, key=lambda row: _text(row["filing_id"], "filing_id")):
        identifiers = {
            field: _text(filing[field], field)
            for field in ("filing_id", "taxpayer_id", "registration_id", "business_name")
        }
        identity = identifiers["filing_id"]
        if identity in by_id:
            raise ValueError("Duplicate filing_id")
        if (
            identifiers["taxpayer_id"] in taxpayers
            or identifiers["registration_id"] in registrations
        ):
            raise ValueError("VAT bank filings must have independent taxpayers and registrations")
        taxpayers.add(identifiers["taxpayer_id"])
        registrations.add(identifiers["registration_id"])
        calculation, child_trace = _child(filing["facts"], identifiers["business_name"], cutoff)
        by_id[identity] = {**identifiers, "calculation": calculation}
        calculations.append({**identifiers, "calculation": calculation})
        derivations.append({"filing_id": identity, "trace": child_trace})

    transfers = _rows(source["transfers"], TRANSFER_FIELDS, "transfers")
    if len(transfers) > MAX_TRANSFER_ROWS:
        raise ValueError("VAT bank source supports at most 200 raw transfer rows")
    unique, duplicates = {}, set()
    for transfer in transfers:
        identity = _text(transfer["transfer_id"], "transfer_id")
        filing_id = _text(transfer["filing_id"], "transfer filing_id")
        registration = _text(transfer["registration_id"], "transfer registration_id")
        if filing_id not in by_id or registration != by_id[filing_id]["registration_id"]:
            raise ValueError("Transfer filing and registration references must match")
        _date(transfer["date"])
        _money(transfer["amount"], "transfer amount")
        if _text(transfer["status"], "transfer status") not in {"executed", "planned"}:
            raise ValueError("Unsupported transfer status")
        if _text(transfer["kind"], "transfer kind") not in {
            "settlement_payment",
            "settlement_refund",
            "assessed_prepayment",
        }:
            raise ValueError("Unsupported transfer kind")
        if identity in unique:
            prior = unique[identity]
            if prior != transfer or any(
                type(prior[field]) is not type(value) for field, value in transfer.items()
            ):
                raise ValueError("Conflicting duplicate transfer_id")
            duplicates.add(identity)
        unique[identity] = deepcopy(transfer)
    if len(unique) > MAX_UNIQUE_TRANSFERS:
        raise ValueError("VAT bank source supports at most 100 unique transfers")

    paid, received = defaultdict(int), defaultdict(int)
    accepted, excluded = [], []
    for identity, transfer in sorted(unique.items()):
        reasons = []
        if transfer["status"] != "executed":
            reasons.append("planned")
        if _date(transfer["date"]) > cutoff:
            reasons.append("after_cutoff")
        if transfer["kind"] == "assessed_prepayment":
            reasons.append("already_in_child_assessment")
        if reasons:
            excluded.append({"transfer_id": identity, "reasons": reasons})
        else:
            accepted.append(identity)
            totals = paid if transfer["kind"] == "settlement_payment" else received
            totals[transfer["filing_id"]] += transfer["amount"]

    settlements = []
    for identity, filing in sorted(by_id.items(), key=lambda item: item[1]["registration_id"]):
        child = filing["calculation"]
        tax_due = child["payable_vat"] - child["refund_vat"]
        net_outflow = paid[identity] - received[identity]
        settlements.append(
            {
                key: filing[key]
                for key in ("filing_id", "taxpayer_id", "registration_id", "business_name")
            }
            | {
                "tax_due": tax_due,
                "payable_vat": child["payable_vat"],
                "refund_vat": child["refund_vat"],
                "paid": paid[identity],
                "received": received[identity],
                "net_outflow": net_outflow,
                "balance": tax_due - net_outflow,
            }
        )
    answer = {
        "filing_calculations": calculations,
        "registration_settlements": settlements,
        "tax_due_total": sum(row["tax_due"] for row in settlements),
        "paid_total": sum(row["paid"] for row in settlements),
        "received_total": sum(row["received"] for row in settlements),
        "balance_total": sum(row["balance"] for row in settlements),
    }
    canonical_source = deepcopy(source)
    canonical_source["processing_policy"] = policy
    canonical_source["filings"].sort(key=lambda row: row["filing_id"])
    canonical_source["transfers"] = [unique[key] for key in sorted(unique)]
    trace = {
        "rule_id": RULE_ID,
        "inputs": canonical_source,
        "output": {
            "filing_derivations": derivations,
            "accepted_transfer_ids": accepted,
            "excluded_transfer_ids": [row["transfer_id"] for row in excluded],
            "excluded_transfers": excluded,
            "deduplicated_transfer_ids": sorted(duplicates),
            "cash_by_registration": [
                {
                    key: row[key]
                    for key in (
                        "filing_id",
                        "registration_id",
                        "tax_due",
                        "paid",
                        "received",
                        "net_outflow",
                        "balance",
                    )
                }
                for row in settlements
            ],
            "settlement": deepcopy(answer),
        },
    }
    return deepcopy(answer), deepcopy([trace])
