"""Select already confirmed documentary status before unchanged VAT joins.

This is a synthetic handover policy, not an issuance deadline or a legal
determination of revocation. Actual supplies and executed payments never change.
"""

from copy import deepcopy

from . import document_reconciliation as documentary
from . import engine, evidence

CONTRACT = "vat_document_lifecycle_v1"
RULE_ID = "C_DOCUMENT_LIFECYCLE_SELECTION"
STATUS_FIELDS = {"document_id", "state", "confirmed_on", "replaces_document_id"}
SELECTION_OUTCOMES = {
    "selected_document_ids",
    "excluded_document_ids",
    "revoked_document_ids",
    "replacement_relations",
}


def _no_selection_outcomes(value):
    if isinstance(value, dict):
        if SELECTION_OUTCOMES & value.keys():
            raise ValueError("Document lifecycle source exposes a precomputed selection")
        for child in value.values():
            _no_selection_outcomes(child)
    elif isinstance(value, list):
        for child in value:
            _no_selection_outcomes(child)


def _original_documents(source, supplies, payments):
    documents = documentary._unique_records(
        source, "evidence_documents", "document_id", documentary.DOCUMENT_FIELDS
    )
    for payment in payments.values():
        identity = documentary._text(payment["transaction_id"], "payment transaction_id")
        if identity not in supplies:
            raise ValueError("Payment refers to unknown supply")
        if documentary._date(payment["date"]) != supplies[identity]["date"]:
            raise ValueError("Only payments on the actual supply date are supported")
        if documentary._text(payment["method"], "payment method") not in {
            "card",
            "cash",
            "bank_transfer",
        }:
            raise ValueError("Unsupported payment method")
        documentary._split(payment)
    for document in documents.values():
        identity = documentary._text(document["transaction_id"], "document transaction_id")
        if identity not in supplies:
            raise ValueError("Document refers to unknown supply")
        if documentary._date(document["date"]) != supplies[identity]["date"]:
            raise ValueError("Only issuance on the actual supply date is supported")
        kind = documentary._text(document["document_type"], "document_type")
        if kind not in engine.EVIDENCE:
            raise ValueError("Unsupported document_type")
        split = documentary._split(document)
        separately = documentary._boolean(
            document["vat_separately_stated"], "vat_separately_stated"
        )
        if separately:
            if type(document["stated_vat"]) is not int or document["stated_vat"] != split[1]:
                raise ValueError("Separately stated VAT conflicts with the proof amount")
        elif document["stated_vat"] is not None:
            raise ValueError("An unstated VAT amount must be null")
        payment_id = document["payment_id"]
        if kind == "tax_invoice":
            if payment_id is not None or not separately:
                raise ValueError("Tax invoice must state VAT and have no payment reference")
        else:
            documentary._text(payment_id, "document payment_id")
            if payment_id not in payments:
                raise ValueError("Document refers to unknown payment")
            payment = payments[payment_id]
            if payment["transaction_id"] != identity:
                raise ValueError("Document transaction conflicts with its payment")
            if kind in documentary.RECEIPTS:
                expected = "card" if kind == "card_receipt" else "cash"
                if payment["method"] != expected:
                    raise ValueError("Receipt kind conflicts with the actual payment method")
            elif separately:
                raise ValueError("Ordinary receipts and ledgers cannot state eligible VAT")
    return documents


def _validate_original_activities(source, supplies, documents):
    """Check full original reference sets without treating revoked amounts as supply."""
    intermediate = deepcopy(source)
    for field in (
        "supplies",
        "payments",
        "evidence_documents",
        "processing_date",
        "document_status_records",
    ):
        intermediate.pop(field)
    intermediate["source_contract"] = evidence.CONTRACT
    rows = []
    for identity, supply in sorted(supplies.items()):
        proof = [row for row in documents.values() if row["transaction_id"] == identity]
        if not proof and supply["direction"] == "sale":
            proof = [{"document_id": identity, "document_type": "receipt"}]
        for document in sorted(proof, key=lambda row: row["document_id"]):
            row = deepcopy(supply)
            row.update(
                document_id=document["document_id"],
                evidence=document["document_type"],
                invoice_issued=False,
                vat_separately_stated=False,
            )
            if supply["direction"] == "sale":
                row.update(
                    supplier_general=True,
                    vehicle_subject_excise=False,
                    vehicle_direct_business=False,
                )
            rows.append(row)
    intermediate["transactions"] = rows
    evidence.interpret(documentary._canonical(intermediate))


def _selection(source):
    if not isinstance(source, dict) or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown VAT document lifecycle contract")
    if "transactions" in source:
        raise ValueError("Raw documentary source must separate supplies from proofs")
    documentary._no_outcomes(source)
    _no_selection_outcomes(source)
    processing_date = documentary._date(source.get("processing_date"))
    supplies = documentary._supplies(source)
    payments = documentary._unique_records(
        source, "payments", "payment_id", documentary.PAYMENT_FIELDS
    )
    documents = _original_documents(source, supplies, payments)
    statuses = documentary._unique_records(
        source, "document_status_records", "document_id", STATUS_FIELDS
    )
    if set(statuses) != set(documents):
        raise ValueError("Status records must cover exactly all original documents")
    replacements = {}
    for identity, status in sorted(statuses.items()):
        if documentary._text(status["state"], "document state") not in {"valid", "revoked"}:
            raise ValueError("Document state must be valid or revoked")
        confirmed = documentary._date(status["confirmed_on"])
        if not documents[identity]["date"] <= confirmed <= processing_date:
            raise ValueError("Document status confirmation is before issuance or after processing")
        target = status["replaces_document_id"]
        if target is None:
            continue
        documentary._text(target, "replaces_document_id")
        if status["state"] != "valid" or target == identity or target not in statuses:
            raise ValueError("Replacement must be valid and refer to another original")
        if statuses[target]["state"] != "revoked":
            raise ValueError("Replacement target must be revoked")
        if confirmed < documentary._date(statuses[target]["confirmed_on"]):
            raise ValueError("Replacement confirmation precedes revocation confirmation")
        if target in replacements:
            raise ValueError("Several valid replacements refer to one revoked original")
        if any(
            documents[identity][field] != documents[target][field]
            for field in ("transaction_id", "document_type", "payment_id")
        ):
            raise ValueError("Replacement transaction, type or payment reference conflicts")
        replacements[target] = identity
    _validate_original_activities(source, supplies, documents)
    selected_ids = sorted(key for key, row in statuses.items() if row["state"] == "valid")
    selected = documentary._canonical(deepcopy(source))
    selected.pop("processing_date")
    selected.pop("document_status_records")
    selected["source_contract"] = documentary.CONTRACT
    selected["evidence_documents"] = [deepcopy(documents[key]) for key in selected_ids]
    for activity in selected["activities"]:
        activity["document_ids"] = sorted(set(activity["document_ids"]) & set(selected_ids))
    trace = {
        "rule_id": RULE_ID,
        "inputs": {
            "source_contract": CONTRACT,
            "processing_date": processing_date,
            "evidence_documents": [documents[key] for key in sorted(documents)],
            "document_status_records": [statuses[key] for key in sorted(statuses)],
            "activities": documentary._canonical(source["activities"]),
        },
        "output": {
            "selected_document_ids": selected_ids,
            "excluded_document_ids": sorted(set(documents) - set(selected_ids)),
            "replacement_relations": [
                {"revoked_document_id": key, "valid_document_id": replacements[key]}
                for key in sorted(replacements)
            ],
        },
    }
    return selected, deepcopy(trace)


def select(source):
    """Return validated documentary input and the status selection trace."""
    selected, trace = _selection(source)
    documentary.interpret(selected)
    return selected, trace


def interpret(source):
    """Return the existing VAT engine input after confirmed status selection."""
    selected, _ = _selection(source)
    return documentary.interpret(selected)


def derivation_trace(source, normalized=None):
    """Return only the selection trace, validating the selected old contract."""
    selected, trace = _selection(source)
    documentary.interpret(selected)
    return trace


def calculate(source):
    """Keep the old VAT answer and prepend deterministic factual selection trace."""
    selected, selection_trace = _selection(source)
    normalized = documentary.interpret(selected)
    answer, trace = engine.calculate(normalized)
    return answer, [selection_trace, documentary.derivation_trace(selected, normalized), *trace]
