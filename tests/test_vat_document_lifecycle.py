"""Confirmed original selection with independently computed VAT examples."""

from copy import deepcopy

import pytest

from rules.c_vat.document_lifecycle import CONTRACT, calculate, derivation_trace, interpret, select
from test_vat_document_reconciliation import invoice, purchase_source, sale_source


def lifecycle(source):
    source = deepcopy(source)
    source.update(
        source_contract=CONTRACT,
        processing_date="2026-07-15",
        document_status_records=[
            {
                "document_id": row["document_id"],
                "state": "valid",
                "confirmed_on": row["date"],
                "replaces_document_id": None,
            }
            for row in source["evidence_documents"]
        ],
    )
    return source


def corrected_partial_sale():
    source = sale_source()
    source["supplies"][0]["amount"] = 1_100_000
    source["payments"][0]["amount"] = 440_000
    source["payments"][1].update(amount=220_000, method="bank_transfer")
    source["evidence_documents"][0].update(amount=440_000, stated_vat=40_000)
    old = deepcopy(source["evidence_documents"][0])
    old.update(document_id="D-old", amount=550_000, stated_vat=50_000)
    source["evidence_documents"].append(old)
    source = lifecycle(source)
    source["document_status_records"][0].update(
        replaces_document_id="D-old", confirmed_on="2026-06-11"
    )
    source["document_status_records"][1].update(state="revoked", confirmed_on="2026-06-10")
    return source


def corrected_purchase():
    source = purchase_source()
    source["supplies"][0]["amount"] = 550_000
    source["payments"][0]["amount"] = 550_000
    source["evidence_documents"] = source["evidence_documents"][:1]
    source["evidence_documents"][0]["amount"] = 550_000
    corrected = deepcopy(source["evidence_documents"][0])
    corrected.update(document_id="D-corrected", vat_separately_stated=True, stated_vat=50_000)
    receipt = deepcopy(source["evidence_documents"][0])
    receipt.update(document_id="D-ordinary", document_type="receipt")
    source["evidence_documents"].extend([corrected, receipt])
    source["activities"][0]["document_ids"] = ["D-card", "D-corrected", "D-ordinary"]
    source = lifecycle(source)
    source["document_status_records"][0]["state"] = "revoked"
    source["document_status_records"][1]["replaces_document_id"] = "D-card"
    return source


def test_manual_partial_sales_amount_correction_and_unpaid_supply():
    source = corrected_partial_sale()
    original = deepcopy(source)
    answer, trace = calculate(source)
    assert (answer["output_vat"], answer["receipt_credit"], answer["payable_vat"]) == (
        100_000,
        5_720,
        94_280,
    )
    assert trace[1]["output"][0]["unpaid_gross"] == 440_000
    assert trace[0]["output"]["replacement_relations"] == [
        {"revoked_document_id": "D-old", "valid_document_id": "D-card"}
    ]
    assert source == original


def test_manual_corrected_purchase_vat_display_changes_credit_not_actual_purchase():
    source = corrected_purchase()
    before, _ = calculate(source)
    assert before["input_vat"] == before["deductible_input_vat"] == 50_000
    assert before["refund_vat"] == 50_000
    source["document_status_records"][1].update(state="revoked", replaces_document_id=None)
    after, _ = calculate(source)
    assert after["input_vat"] == 50_000
    assert after["deductible_input_vat"] == 0
    assert after["noncreditable_vat"] == 50_000
    assert after["unique_transaction_count"] == before["unique_transaction_count"] == 1


def test_manual_cancelled_full_invoice_selection_and_annual_credit_remaining():
    source = corrected_partial_sale()
    source["evidence_documents"] = source["evidence_documents"][:1]
    full = invoice()
    full.update(amount=1_000_000, stated_vat=100_000)
    source["evidence_documents"].append(full)
    supply = deepcopy(source["supplies"][0])
    supply.update(transaction_id="B", amount=550_000)
    source["supplies"].append(supply)
    source["payments"].append(
        {
            "payment_id": "B-cash",
            "transaction_id": "B",
            "date": "2026-05-20",
            "amount": 110_000,
            "includes_vat": True,
            "method": "cash",
        }
    )
    source["evidence_documents"].append(
        {
            "document_id": "B-doc",
            "transaction_id": "B",
            "date": "2026-05-20",
            "document_type": "cash_receipt",
            "amount": 110_000,
            "includes_vat": True,
            "vat_separately_stated": True,
            "stated_vat": 10_000,
            "payment_id": "B-cash",
        }
    )
    source = lifecycle(source)
    source["document_status_records"][1]["state"] = "revoked"
    source["receipt_credit_previously_claimed"] = 9_994_000
    before, _ = calculate(source)
    assert before["receipt_credit"] == 6_000  # (440000 + 110000) * .013 = 7150, cap6000.
    source["document_status_records"][1]["state"] = "valid"
    after, _ = calculate(source)
    assert after["receipt_credit"] == 1_430
    assert before["output_vat"] == after["output_vat"] == 150_000


@pytest.mark.parametrize("factory", [corrected_partial_sale, corrected_purchase])
def test_exact_retransmission_and_collection_order_preserve_entire_trace(factory):
    source = factory()
    expected = calculate(source)
    for field in ("evidence_documents", "document_status_records", "payments"):
        source[field].append(deepcopy(source[field][0]))
        source[field].reverse()
    source["supplies"].reverse()
    source["activities"].reverse()
    assert calculate(source) == expected
    normalized = interpret(source)
    assert derivation_trace(source, normalized) == expected[1][0]
    selected, selection_trace = select(source)
    assert selection_trace == expected[1][0]
    assert selected["source_contract"] == "vat_document_reconciliation_v1"


def test_processing_after_july25_is_allowed_and_not_a_legal_deduction_deadline():
    source = corrected_partial_sale()
    source["processing_date"] = "2026-12-01"
    source["document_status_records"][0]["confirmed_on"] = "2026-11-30"
    assert calculate(source)[0]["receipt_credit"] == 5_720


@pytest.mark.parametrize(
    "field,value",
    [
        ("state", "pending"),
        ("state", None),
        ("confirmed_on", "2026-05-19"),
        ("confirmed_on", "2026-07-16"),
        ("confirmed_on", "20260611"),
        ("replaces_document_id", "D-card"),
        ("replaces_document_id", "missing"),
    ],
)
def test_invalid_status_dates_states_and_replacement_refs(field, value):
    source = corrected_partial_sale()
    source["document_status_records"][0][field] = value
    with pytest.raises(ValueError):
        calculate(source)


@pytest.mark.parametrize("defect", ["missing", "foreign", "conflict", "extra", "document_conflict"])
def test_status_exact_coverage_and_identity_conflicts(defect):
    source = corrected_partial_sale()
    if defect == "missing":
        source["document_status_records"].pop()
    elif defect == "foreign":
        source["document_status_records"][1]["document_id"] = "foreign"
    elif defect == "extra":
        source["document_status_records"][1]["memo"] = "extra"
    elif defect == "document_conflict":
        duplicate = deepcopy(source["evidence_documents"][1])
        duplicate["amount"] = 660_000
        source["evidence_documents"].append(duplicate)
    else:
        duplicate = deepcopy(source["document_status_records"][1])
        duplicate["confirmed_on"] = "2026-06-09"
        source["document_status_records"].append(duplicate)
    with pytest.raises(ValueError):
        calculate(source)


@pytest.mark.parametrize(
    "field,value",
    [
        ("amount", 550_001),
        ("amount", True),
        ("includes_vat", 1),
        ("stated_vat", 40_000),
        ("vat_separately_stated", 1),
        ("date", "2026-05-21"),
        ("date", "20260520"),
        ("transaction_id", "foreign"),
        ("payment_id", "foreign"),
        ("document_type", "cash_receipt"),
        ("document_type", "unsupported"),
    ],
)
def test_revoked_originals_still_require_valid_raw_shapes_dates_refs_and_self_vat(field, value):
    source = corrected_partial_sale()
    source["evidence_documents"][1][field] = value
    with pytest.raises(ValueError):
        calculate(source)


def test_valid_original_does_not_inherit_revoked_amount_mismatch_permission():
    source = corrected_partial_sale()
    source["evidence_documents"][0].update(amount=550_000, stated_vat=50_000)
    with pytest.raises(ValueError, match="amount or transaction"):
        calculate(source)


@pytest.mark.parametrize(
    "defect",
    [
        "valid_target",
        "revoked_replacer",
        "early",
        "double",
        "type",
        "payment",
        "transaction",
        "cycle",
    ],
)
def test_replacement_relationship_constraints(defect):
    source = corrected_partial_sale()
    statuses = source["document_status_records"]
    docs = source["evidence_documents"]
    if defect == "valid_target":
        statuses[1]["state"] = "valid"
    elif defect == "revoked_replacer":
        statuses[0]["state"] = "revoked"
    elif defect == "early":
        statuses[0]["confirmed_on"] = "2026-06-09"
    elif defect == "double":
        doc = deepcopy(docs[0])
        doc["document_id"] = "D-second"
        docs.append(doc)
        status = deepcopy(statuses[0])
        status["document_id"] = "D-second"
        statuses.append(status)
    elif defect == "type":
        docs[1].update(document_type="receipt", vat_separately_stated=False, stated_vat=None)
    elif defect == "payment":
        payment = deepcopy(source["payments"][0])
        payment.update(payment_id="second-card", amount=110_000)
        source["payments"].append(payment)
        docs[1]["payment_id"] = "second-card"
    elif defect == "transaction":
        supply = deepcopy(source["supplies"][0])
        supply["transaction_id"] = "other-supply"
        source["supplies"].append(supply)
        payment = deepcopy(source["payments"][0])
        payment.update(payment_id="other-card", transaction_id="other-supply")
        source["payments"].append(payment)
        docs[1].update(transaction_id="other-supply", payment_id="other-card")
    else:
        statuses[1]["replaces_document_id"] = "D-card"
    with pytest.raises(ValueError):
        calculate(source)


@pytest.mark.parametrize(
    "defect",
    [
        "missing_original",
        "foreign_doc",
        "sale_activity",
        "date",
        "foreign_transaction",
        "duplicate",
    ],
)
def test_original_activity_references_validated_before_filtering(defect):
    source = corrected_purchase()
    activity = source["activities"][0]
    if defect == "missing_original":
        activity["document_ids"].remove("D-card")
    elif defect == "foreign_doc":
        activity["document_ids"].append("foreign")
    elif defect == "sale_activity":
        source["supplies"][0] = sale_source()["supplies"][0]
    elif defect == "date":
        activity["date"] = "2026-05-19"
    elif defect == "foreign_transaction":
        activity["transaction_id"] = "other"
    else:
        source["activities"].append(deepcopy(activity))
    with pytest.raises(ValueError):
        calculate(source)


def test_all_revoked_purchase_is_rejected_instead_of_silently_deducted_or_erased():
    source = corrected_purchase()
    for status in source["document_status_records"]:
        status.update(state="revoked", replaces_document_id=None)
    with pytest.raises(ValueError):
        calculate(source)


def test_partial_purchase_still_needs_valid_full_invoice():
    source = lifecycle(purchase_source())
    source["payments"][0]["amount"] = 55_000
    source["evidence_documents"][0]["amount"] = 55_000
    assert calculate(source)[0]["deductible_input_vat"] == 10_000
    source["document_status_records"][1]["state"] = "revoked"
    with pytest.raises(ValueError, match="Partial purchase"):
        calculate(source)


def test_revoked_full_invoice_can_have_old_wrong_amount_but_not_wrong_self_vat():
    source = lifecycle(sale_source())
    old = invoice()
    old.update(amount=200_000, stated_vat=20_000)
    source["evidence_documents"].append(old)
    source["document_status_records"].append(
        {
            "document_id": "D-invoice",
            "state": "revoked",
            "confirmed_on": "2026-06-01",
            "replaces_document_id": None,
        }
    )
    assert calculate(source)[0]["receipt_credit"] == 715
    source["evidence_documents"][1]["stated_vat"] = 10_000
    with pytest.raises(ValueError, match="Separately stated"):
        calculate(source)


@pytest.mark.parametrize(
    "field",
    [
        "purpose",
        "receipt_credit",
        "issued_receipt_gross",
        "documented_input_vat",
        "selected_document_ids",
    ],
)
def test_recursive_precomputed_decisions_are_rejected(field):
    source = corrected_partial_sale()
    source["evidence_documents"][1][field] = 0
    with pytest.raises(ValueError, match="precomputed"):
        calculate(source)


def test_all_revoked_sales_keep_actual_supply_and_remove_only_issuance_credit():
    source = corrected_partial_sale()
    source["document_status_records"][0].update(state="revoked", replaces_document_id=None)
    answer, trace = calculate(source)
    assert answer["output_vat"] == 100_000
    assert answer["receipt_credit"] == 0
    assert answer["unique_transaction_count"] == 1
    assert trace[0]["output"]["selected_document_ids"] == []
    assert trace[1]["output"][0]["document_ids"] == []


def test_two_valid_receipts_for_one_payment_are_still_ambiguous_without_replacement():
    source = corrected_partial_sale()
    source["evidence_documents"][1].update(amount=440_000, stated_vat=40_000)
    for status in source["document_status_records"]:
        status.update(state="valid", replaces_document_id=None)
    with pytest.raises(ValueError, match="Several issued originals"):
        calculate(source)


def test_revocation_does_not_hide_invalid_actual_payment_total():
    source = corrected_partial_sale()
    source["payments"][1]["amount"] = 880_000
    with pytest.raises(ValueError, match="Payment total exceeds"):
        calculate(source)


def test_revoked_original_cannot_reference_another_supplies_payment():
    source = corrected_partial_sale()
    supply = deepcopy(source["supplies"][0])
    supply["transaction_id"] = "other-supply"
    source["supplies"].append(supply)
    payment = deepcopy(source["payments"][0])
    payment.update(payment_id="other-card", transaction_id="other-supply")
    source["payments"].append(payment)
    source["evidence_documents"][1]["payment_id"] = "other-card"
    with pytest.raises(ValueError, match="transaction conflicts"):
        calculate(source)
