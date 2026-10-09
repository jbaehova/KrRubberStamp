"""Join completed supplies, same-day payments and individually issued proofs.

This factual contract supports partial sales receipts and full-input proof
supplementation. It does not classify supply time or allocate partial input VAT.
"""

from copy import deepcopy
from datetime import date
import json

from . import engine, evidence

CONTRACT = "vat_document_reconciliation_v1"
RULE_ID = "C_DOCUMENT_RECONCILIATION"
RECEIPTS = {"card_receipt", "cash_receipt"}
DERIVED = {
    "purpose",
    "business_related",
    "issued_receipt_gross",
    "documented_input_vat",
    "receipt_base",
    "eligible",
    "deductible",
    "included",
    "tax_base",
    "output_vat",
    "input_vat",
    "noncreditable_vat",
    "deductible_input_vat",
    "receipt_credit",
    "prepaid_vat",
    "net_vat",
    "payable_vat",
    "refund_vat",
    "unique_transaction_count",
}
SUPPLY_FIELDS = {
    "transaction_id",
    "direction",
    "date",
    "description",
    "amount",
    "includes_vat",
    "taxable",
    "counterparty_consumer",
}
PURCHASE_FIELDS = {
    "activity_id",
    "supplier_id",
    "supplier_general",
    "vehicle_id",
    "vehicle_subject_excise",
    "vehicle_direct_business",
}
PAYMENT_FIELDS = {
    "payment_id",
    "transaction_id",
    "date",
    "amount",
    "includes_vat",
    "method",
}
DOCUMENT_FIELDS = {
    "document_id",
    "transaction_id",
    "date",
    "document_type",
    "amount",
    "includes_vat",
    "vat_separately_stated",
    "stated_vat",
    "payment_id",
}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"VAT documentary contract requires nonempty {field}")
    return value


def _date(value):
    _text(value, "date")
    if date.fromisoformat(value).isoformat() != value:
        raise ValueError("VAT documentary contract requires ISO calendar dates")
    return value


def _boolean(value, field):
    if type(value) is not bool:
        raise ValueError(f"VAT documentary contract requires boolean {field}")
    return value


def _split(row):
    if type(row.get("amount")) is not int or row["amount"] <= 0:
        raise ValueError("VAT documentary amount must be a positive integer")
    _boolean(row.get("includes_vat"), "includes_vat")
    return engine._split({**row, "taxable": True})


def _canonical(value):
    """These factual record collections are sets, not ordered decision steps."""
    if isinstance(value, dict):
        return {key: _canonical(child) for key, child in sorted(value.items())}
    if isinstance(value, list):
        children = [_canonical(child) for child in value]
        return sorted(children, key=lambda child: json.dumps(child, sort_keys=True))
    return value


def _no_outcomes(value):
    if isinstance(value, dict):
        if DERIVED & value.keys():
            raise ValueError("VAT documentary source exposes a precomputed decision")
        for child in value.values():
            _no_outcomes(child)
    elif isinstance(value, list):
        for child in value:
            _no_outcomes(child)


def _unique_records(source, field, identity, required):
    rows = source.get(field)
    if not isinstance(rows, list):
        raise ValueError(f"VAT documentary {field} must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != required:
            raise ValueError(f"VAT documentary {field} has unknown or missing fields")
        key = _text(row[identity], identity)
        if key in result and json.dumps(row, sort_keys=True) != json.dumps(
            result[key], sort_keys=True
        ):
            raise ValueError(f"Conflicting documentary identity: {key}")
        result[key] = row
    return result


def _supplies(source):
    rows = source.get("supplies")
    if not isinstance(rows, list) or not rows:
        raise ValueError("VAT documentary supplies must be a nonempty list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not SUPPLY_FIELDS <= row.keys():
            raise ValueError("VAT supply has missing factual fields")
        direction = _text(row["direction"], "direction")
        if direction not in {"sale", "purchase"}:
            raise ValueError("VAT supply direction must be sale or purchase")
        allowed = SUPPLY_FIELDS | (PURCHASE_FIELDS if direction == "purchase" else set())
        if set(row) - allowed:
            raise ValueError("VAT supply has unknown factual fields")
        identity = _text(row["transaction_id"], "transaction_id")
        if identity in result:
            raise ValueError("Duplicate supply transaction identity")
        _text(row["description"], "supply description")
        _date(row["date"])
        if _boolean(row["taxable"], "taxable") is not True:
            raise ValueError("Only domestic 10% taxable supplies are supported")
        _boolean(row["counterparty_consumer"], "counterparty_consumer")
        _split(row)
        if direction == "purchase":
            _text(row.get("activity_id"), "activity_id")
            if "supplier_status_records" in source:
                _text(row.get("supplier_id"), "supplier_id")
                if "supplier_general" in row:
                    raise ValueError("Registered supplier exposes preselected status")
            else:
                if "supplier_id" in row:
                    raise ValueError("Supplier identity requires supplier records")
                _boolean(row.get("supplier_general"), "supplier_general")
            if "vehicle_id" in row:
                _text(row["vehicle_id"], "vehicle_id")
                if (
                    "vehicle_registry" not in source
                    or {"vehicle_subject_excise", "vehicle_direct_business"} & row.keys()
                ):
                    raise ValueError("Registered vehicle requires raw classification records")
            else:
                for field in ("vehicle_subject_excise", "vehicle_direct_business"):
                    _boolean(row.get(field), field)
        result[identity] = row
    return result


def _join(source):
    if not isinstance(source, dict) or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown VAT documentary reconciliation contract")
    if "transactions" in source:
        raise ValueError("Raw documentary source must separate supplies from proofs")
    _no_outcomes(source)
    _text(source.get("scope_note"), "scope_note")
    if source.get("taxpayer_type") != "general":
        raise ValueError("Only general VAT taxpayers are supported")
    if (source.get("period_start"), source.get("period_end")) != ("2026-01-01", "2026-06-30"):
        raise ValueError("Only 2026 first-half is supported")
    _boolean(source.get("consumer_facing_business"), "consumer_facing_business")
    supplies = _supplies(source)
    payments = _unique_records(source, "payments", "payment_id", PAYMENT_FIELDS)
    documents = _unique_records(source, "evidence_documents", "document_id", DOCUMENT_FIELDS)
    paid = {identity: 0 for identity in supplies}
    proofs = {identity: [] for identity in supplies}
    for payment in payments.values():
        identity = payment["transaction_id"]
        _text(identity, "payment transaction_id")
        if identity not in supplies:
            raise ValueError("Payment refers to unknown supply")
        if _date(payment["date"]) != supplies[identity]["date"]:
            raise ValueError("Only payments on the actual supply date are supported")
        if _text(payment["method"], "payment method") not in {"card", "cash", "bank_transfer"}:
            raise ValueError("Unsupported payment method")
        paid[identity] += _split(payment)[2]
    for identity, amount in paid.items():
        if amount > _split(supplies[identity])[2]:
            raise ValueError("Payment total exceeds the actual supply gross")
    receipted_payments = set()
    for document in documents.values():
        identity = document["transaction_id"]
        _text(identity, "document transaction_id")
        if identity not in supplies:
            raise ValueError("Document refers to unknown supply")
        supply = supplies[identity]
        if _date(document["date"]) != supply["date"]:
            raise ValueError("Only issuance on the actual supply date is supported")
        kind = _text(document["document_type"], "document_type")
        if kind not in engine.EVIDENCE:
            raise ValueError("Unsupported document_type")
        split = _split(document)
        separately = _boolean(document["vat_separately_stated"], "vat_separately_stated")
        if separately:
            if type(document["stated_vat"]) is not int or document["stated_vat"] != split[1]:
                raise ValueError("Separately stated VAT conflicts with the proof amount")
        elif document["stated_vat"] is not None:
            raise ValueError("An unstated VAT amount must be null")
        payment_id = document["payment_id"]
        if kind == "tax_invoice":
            if payment_id is not None or not separately or split != _split(supply):
                raise ValueError("Tax invoice must state VAT for the whole actual supply")
        else:
            _text(payment_id, "document payment_id")
            if payment_id not in payments:
                raise ValueError("Document refers to unknown payment")
            payment = payments[payment_id]
            if payment["transaction_id"] != identity or split != _split(payment):
                raise ValueError("Document amount or transaction conflicts with its payment")
            if kind in RECEIPTS:
                expected_method = "card" if kind == "card_receipt" else "cash"
                if payment["method"] != expected_method:
                    raise ValueError("Receipt kind conflicts with the actual payment method")
                if payment_id in receipted_payments:
                    raise ValueError("Several issued originals refer to one payment")
                receipted_payments.add(payment_id)
            elif separately:
                raise ValueError("Ordinary receipts and ledgers cannot state eligible VAT")
        proofs[identity].append(document)
    joins = {}
    for identity, supply in sorted(supplies.items()):
        proof = sorted(proofs[identity], key=lambda row: row["document_id"])
        base, vat, gross = _split(supply)
        invoice = any(row["document_type"] == "tax_invoice" for row in proof)
        issued = sum(_split(row)[2] for row in proof if row["document_type"] in RECEIPTS)
        if issued > gross:
            raise ValueError("Receipt issuance exceeds the actual supply gross")
        eligible = [
            row["document_id"]
            for row in proof
            if supply["direction"] == "purchase"
            and row["document_type"] in RECEIPTS | {"tax_invoice"}
            and row["vat_separately_stated"]
            and _split(row)[2] == gross
        ]
        if supply["direction"] == "purchase":
            if not proof:
                raise ValueError("Purchase needs its actual documentary proof")
            if any(_split(row)[2] < gross for row in proof) and not invoice:
                raise ValueError("Partial purchase evidence requires a full tax invoice")
        joins[identity] = {
            "proof": proof,
            "supply_base": base,
            "vat": vat,
            "gross": gross,
            "paid_gross": paid[identity],
            "unpaid_gross": gross - paid[identity],
            "issued_receipt_gross": issued,
            "unissued_receipt_gross": gross - issued,
            "invoice_issued": invoice,
            "eligible_input_document_ids": eligible,
            "documented_input_vat": vat if eligible else 0,
        }
    return supplies, payments, documents, joins


def interpret(source):
    """Normalize proof-specific amounts and VAT display before activity joins.

    Purchase purpose, supplier validity and vehicle treatment come from the
    existing factual activity contract. No supplied deduction outcome is read.
    """
    supplies, _, _, joins = _join(source)
    intermediate = _canonical(deepcopy(source))
    for field in ("supplies", "payments", "evidence_documents"):
        intermediate.pop(field)
    intermediate["source_contract"] = evidence.CONTRACT
    rows = []
    for identity, supply in sorted(supplies.items()):
        join = joins[identity]
        proof = join["proof"] or [{"document_id": identity, "document_type": "receipt"}]
        for document in proof:
            row = deepcopy(supply)
            row.update(
                document_id=document["document_id"],
                evidence=document["document_type"],
                invoice_issued=join["invoice_issued"],
                vat_separately_stated=bool(join["eligible_input_document_ids"]),
            )
            if supply["direction"] == "sale":
                row.update(
                    supplier_general=True,
                    vehicle_subject_excise=False,
                    vehicle_direct_business=False,
                    issued_receipt_gross=join["issued_receipt_gross"],
                )
            rows.append(row)
    intermediate["transactions"] = rows
    normalized = evidence.interpret(intermediate)
    for row in normalized["transactions"]:
        if row["direction"] == "purchase":
            row["documented_input_vat"] = joins[row["transaction_id"]]["documented_input_vat"]
    return normalized


def derivation_trace(source, normalized):
    """Deterministic raw joins and factual derivation, distinct from VAT law."""
    supplies, payments, documents, joins = _join(source)
    derived_rows = {row["transaction_id"]: row for row in normalized["transactions"]}
    inputs = {
        "source_contract": CONTRACT,
        "supplies": [supplies[key] for key in sorted(supplies)],
        "payments": [payments[key] for key in sorted(payments)],
        "evidence_documents": [documents[key] for key in sorted(documents)],
    }
    for field in (
        "business_name",
        "operations",
        "activities",
        "vehicle_registry",
        "supplier_status_records",
        "site_year_records",
        "filing_site_id",
    ):
        if field in source:
            inputs[field] = _canonical(source[field])
    outputs = []
    for identity, join in sorted(joins.items()):
        output = {
            "transaction_id": identity,
            "document_ids": [row["document_id"] for row in join["proof"]],
            **{key: value for key, value in join.items() if key != "proof"},
        }
        if supplies[identity]["direction"] == "purchase":
            row = derived_rows[identity]
            output["purchase_activity_facts"] = {
                key: row[key]
                for key in (
                    "purpose",
                    "business_related",
                    "supplier_general",
                    "vehicle_subject_excise",
                    "vehicle_direct_business",
                )
            }
        outputs.append(output)
    result = {"rule_id": RULE_ID, "inputs": inputs, "output": outputs}
    if "site_year_records" in source:
        result["prior_year_site_supply_base"] = normalized["prior_year_site_supply_base"]
    return result
