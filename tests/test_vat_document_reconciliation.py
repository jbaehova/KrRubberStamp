"""Independent small-money proofs of bounded supply/payment/document joins."""

from copy import deepcopy
import hashlib
import json

import pytest

from KrRubberStamp.authoring import load_cases
from KrRubberStamp.registry import calculate as registry_calculate
from rules.c_vat.document_reconciliation import CONTRACT, derivation_trace, interpret
from rules.c_vat.engine import calculate


def sale_source():
    return {
        "source_contract": CONTRACT,
        "taxpayer_type": "general",
        "period_start": "2026-01-01",
        "period_end": "2026-06-30",
        "business_name": "가상시험점포",
        "business_type": "individual",
        "consumer_facing_business": True,
        "prior_year_site_supply_base": 10_000_000,
        "receipt_credit_previously_claimed": 0,
        "prepaid_assessed_vat": 0,
        "scope_note": "국내 과세 공급이다. 적법한 증빙을 보관하고 수령명세서를 제출한다.",
        "operations": [],
        "activities": [],
        "supplies": [
            {
                "transaction_id": "S",
                "direction": "sale",
                "date": "2026-05-20",
                "description": "당일 완료 공급",
                "amount": 110_000,
                "includes_vat": True,
                "taxable": True,
                "counterparty_consumer": True,
            }
        ],
        "payments": [
            {
                "payment_id": "P-card",
                "transaction_id": "S",
                "date": "2026-05-20",
                "amount": 55_000,
                "includes_vat": True,
                "method": "card",
            },
            {
                "payment_id": "P-cash",
                "transaction_id": "S",
                "date": "2026-05-20",
                "amount": 55_000,
                "includes_vat": True,
                "method": "cash",
            },
        ],
        "evidence_documents": [
            {
                "document_id": "D-card",
                "transaction_id": "S",
                "date": "2026-05-20",
                "document_type": "card_receipt",
                "amount": 55_000,
                "includes_vat": True,
                "vat_separately_stated": True,
                "stated_vat": 5_000,
                "payment_id": "P-card",
            }
        ],
    }


def invoice():
    return {
        "document_id": "D-invoice",
        "transaction_id": "S",
        "date": "2026-05-20",
        "document_type": "tax_invoice",
        "amount": 100_000,
        "includes_vat": False,
        "vat_separately_stated": True,
        "stated_vat": 10_000,
        "payment_id": None,
    }


def purchase_source():
    source = sale_source()
    source["supplies"][0].update(
        direction="purchase",
        counterparty_consumer=False,
        activity_id="A",
        supplier_general=True,
        vehicle_subject_excise=False,
        vehicle_direct_business=False,
    )
    source["payments"] = [source["payments"][0]]
    source["payments"][0]["amount"] = 110_000
    source["evidence_documents"][0].update(
        amount=110_000,
        vat_separately_stated=False,
        stated_vat=None,
    )
    source["evidence_documents"].append(invoice())
    source["operations"] = [
        {
            "operation_id": "O",
            "description": "과세 제품 생산",
            "output_taxable": True,
        }
    ]
    source["activities"] = [
        {
            "activity_id": "A",
            "transaction_id": "S",
            "document_ids": ["D-card", "D-invoice"],
            "date": "2026-05-20",
            "action": "delivery",
            "location": {"name": "가상생산실", "kind": "worksite"},
            "participants": [
                {
                    "name": "가상직원",
                    "role": "employee",
                    "organization": "가상시험점포",
                }
            ],
            "operation_id": "O",
            "description": "직원이 생산 자재를 실제 수령했다.",
        }
    ]
    return source


def result(source):
    normalized = interpret(source)
    answer, trace = calculate(normalized)
    return answer, [derivation_trace(source, normalized), *trace]


def test_half_card_half_unissued_cash_counts_the_whole_supply_only_once():
    source = sale_source()
    original = deepcopy(source)
    answer, trace = result(source)
    # 110000 / 11 = 10000; issued 55000 * .013 = 715; 10000 - 715 = 9285.
    assert answer == {
        "tax_base": 100_000,
        "output_vat": 10_000,
        "input_vat": 0,
        "noncreditable_vat": 0,
        "deductible_input_vat": 0,
        "receipt_credit": 715,
        "prepaid_vat": 0,
        "net_vat": 9_285,
        "payable_vat": 9_285,
        "refund_vat": 0,
        "unique_transaction_count": 1,
    }
    assert trace[0]["output"][0]["issued_receipt_gross"] == 55_000
    assert trace[0]["output"][0]["unissued_receipt_gross"] == 55_000
    assert source == original
    assert "issued_receipt_gross" not in source["supplies"][0]


def test_card_and_cash_partial_originals_sum_actual_issuance_not_whole_supply():
    source = sale_source()
    source["payments"][0]["amount"] = 33_000
    source["payments"][1]["amount"] = 44_000
    source["evidence_documents"][0].update(amount=33_000, stated_vat=3_000)
    cash = deepcopy(source["evidence_documents"][0])
    cash.update(
        document_id="D-cash",
        document_type="cash_receipt",
        amount=44_000,
        stated_vat=4_000,
        payment_id="P-cash",
    )
    source["evidence_documents"].append(cash)
    answer, trace = result(source)
    assert answer["output_vat"] == 10_000
    assert answer["receipt_credit"] == 1_001  # (33000 + 44000) * 13 / 1000
    assert answer["payable_vat"] == 8_999
    assert answer["unique_transaction_count"] == 1
    assert trace[0]["output"][0]["unpaid_gross"] == 33_000
    assert trace[0]["output"][0]["unissued_receipt_gross"] == 33_000


def test_whole_invoice_and_partial_card_do_not_create_receipt_credit():
    source = sale_source()
    source["evidence_documents"].append(invoice())
    answer, trace = result(source)
    assert answer["tax_base"] == 100_000
    assert answer["receipt_credit"] == 0
    assert answer["payable_vat"] == 10_000
    assert answer["unique_transaction_count"] == 1
    receipt = next(row for row in trace if row["rule_id"] == "VAT_RECEIPT_BASE")
    assert receipt["inputs"]["issued_receipt_gross"] == 55_000
    assert receipt["output"] == {"eligible_gross": 0}


def test_full_electronic_proof_supplements_unstated_card_without_double_input():
    source = purchase_source()
    before, trace = result(source)
    assert before["input_vat"] == before["deductible_input_vat"] == 10_000
    assert before["refund_vat"] == 10_000
    assert before["unique_transaction_count"] == 1
    assert trace[0]["output"][0]["eligible_input_document_ids"] == ["D-invoice"]
    source["evidence_documents"] = source["evidence_documents"][:1]
    source["activities"][0]["document_ids"] = ["D-card"]
    after, _ = result(source)
    assert after["input_vat"] == before["input_vat"]
    assert after["unique_transaction_count"] == before["unique_transaction_count"]
    assert after["deductible_input_vat"] == 0
    assert after["noncreditable_vat"] == 10_000
    assert after["refund_vat"] == 0


def test_full_invoice_can_cover_partial_purchase_payment_proof_but_not_partial_credit():
    source = purchase_source()
    source["payments"][0]["amount"] = 55_000
    source["evidence_documents"][0]["amount"] = 55_000
    assert result(source)[0]["deductible_input_vat"] == 10_000
    source["evidence_documents"] = source["evidence_documents"][:1]
    source["activities"][0]["document_ids"] = ["D-card"]
    with pytest.raises(ValueError, match="Partial purchase"):
        interpret(source)


def test_qualified_full_card_and_full_invoice_deduct_once():
    source = purchase_source()
    source["evidence_documents"][0].update(vat_separately_stated=True, stated_vat=10_000)
    answer, trace = result(source)
    assert answer["input_vat"] == answer["deductible_input_vat"] == 10_000
    assert trace[0]["output"][0]["eligible_input_document_ids"] == ["D-card", "D-invoice"]


def test_unpaid_completed_supply_is_not_reduced_to_collected_cash():
    source = sale_source()
    source["payments"] = []
    source["evidence_documents"] = []
    answer, trace = result(source)
    assert answer["output_vat"] == 10_000
    assert answer["receipt_credit"] == 0
    assert trace[0]["output"][0]["unpaid_gross"] == 110_000


def test_payment_only_counterfactual_preserves_tax_and_changes_unpaid_balance():
    source = sale_source()
    before, before_trace = result(source)
    source["payments"] = source["payments"][:1]
    after, after_trace = result(source)
    assert before == after
    assert before_trace[0]["output"][0]["unpaid_gross"] == 0
    assert after_trace[0]["output"][0]["unpaid_gross"] == 55_000


@pytest.mark.parametrize("factory", [sale_source, purchase_source])
def test_exact_document_and_payment_retransmissions_preserve_answer_and_entire_trace(factory):
    source = factory()
    expected = result(source)
    source["payments"].append(deepcopy(source["payments"][0]))
    source["evidence_documents"].append(deepcopy(source["evidence_documents"][0]))
    assert result(source) == expected


def test_all_record_orders_preserve_answer_and_entire_trace():
    source = purchase_source()
    extra = deepcopy(source["supplies"][0])
    extra.update(transaction_id="Q", direction="sale", description="독립 공급")
    for field in (
        "activity_id",
        "supplier_general",
        "vehicle_subject_excise",
        "vehicle_direct_business",
    ):
        extra.pop(field)
    source["supplies"].append(extra)
    source["operations"].append(
        {"operation_id": "Unused", "description": "별도 작업", "output_taxable": True}
    )
    source["activities"][0]["participants"].append(
        {
            "name": "가상다른직원",
            "role": "employee",
            "organization": "가상시험점포",
        }
    )
    expected = result(source)
    for field in ("supplies", "payments", "evidence_documents", "operations", "activities"):
        source[field].reverse()
    source["activities"][0]["participants"].reverse()
    source["activities"][0]["document_ids"].reverse()
    assert result(source) == expected


@pytest.mark.parametrize("blocked", ["private", "hospitality", "exempt", "vehicle", "supplier"])
def test_business_and_statutory_restrictions_override_full_qualified_proof(blocked):
    source = purchase_source()
    activity = source["activities"][0]
    if blocked == "private":
        activity.update(
            operation_id=None,
            location={"name": "가상가정", "kind": "home"},
            participants=[
                {"name": "가상가족", "role": "household_member", "organization": "가상가정"}
            ],
        )
    elif blocked == "hospitality":
        activity.update(action="meal", location={"name": "가상식당", "kind": "restaurant"})
        activity["participants"].append(
            {"name": "가상고객", "role": "customer", "organization": "가상외부"}
        )
    elif blocked == "exempt":
        source["operations"][0]["output_taxable"] = False
    elif blocked == "vehicle":
        activity["action"] = "vehicle_service"
        source["supplies"][0]["vehicle_subject_excise"] = True
    else:
        source["supplies"][0]["supplier_general"] = False
    answer, _ = result(source)
    assert answer["input_vat"] == 10_000
    assert answer["deductible_input_vat"] == 0
    assert answer["noncreditable_vat"] == 10_000


def test_existing_date_valid_supplier_and_vehicle_registers_are_reused():
    source = purchase_source()
    supply = source["supplies"][0]
    for field in ("supplier_general", "vehicle_subject_excise", "vehicle_direct_business"):
        supply.pop(field)
    supply.update(supplier_id="Supplier", vehicle_id="Vehicle")
    source["supplier_status_records"] = [
        {
            "supplier_id": "Supplier",
            "status": "general",
            "valid_from": "2026-01-01",
            "valid_to": "2026-06-30",
        }
    ]
    source["vehicle_registry"] = [
        {
            "vehicle_id": "Vehicle",
            "registration_class": "excise_passenger",
            "business_license": "taxi_transport",
            "permitted_operation_id": "O",
            "valid_from": "2026-01-01",
            "valid_to": "2026-06-30",
        }
    ]
    source["activities"][0].update(action="vehicle_service", vehicle_id="Vehicle")
    assert result(source)[0]["deductible_input_vat"] == 10_000
    source["vehicle_registry"][0]["permitted_operation_id"] = "Other"
    source["operations"].append(
        {"operation_id": "Other", "description": "다른 허가사업", "output_taxable": True}
    )
    assert result(source)[0]["deductible_input_vat"] == 0


@pytest.mark.parametrize(
    "restriction", ["corporation", "industry", "prior_supply", "annual", "liability"]
)
def test_existing_receipt_credit_restrictions_remain_in_force(restriction):
    source = sale_source()
    if restriction == "corporation":
        source["business_type"] = "corporation"
    elif restriction == "industry":
        source["consumer_facing_business"] = False
    elif restriction == "prior_supply":
        source["prior_year_site_supply_base"] = 1_000_000_001
    elif restriction == "annual":
        source["receipt_credit_previously_claimed"] = 9_999_900
    else:
        purchase = purchase_source()
        purchase["supplies"][0]["transaction_id"] = "Buy"
        purchase["supplies"][0]["amount"] = 106_700  # input VAT 9700: liability 300
        for payment in purchase["payments"]:
            payment.update(transaction_id="Buy", payment_id="Buy-pay", amount=106_700)
        for proof in purchase["evidence_documents"]:
            proof.update(transaction_id="Buy", document_id="Buy-" + proof["document_id"])
            proof["amount"] = 97_000 if proof["document_type"] == "tax_invoice" else 106_700
            proof["payment_id"] = None if proof["document_type"] == "tax_invoice" else "Buy-pay"
            proof["stated_vat"] = 9_700 if proof["document_type"] == "tax_invoice" else None
        purchase["activities"][0].update(
            transaction_id="Buy",
            document_ids=[p["document_id"] for p in purchase["evidence_documents"]],
        )
        for field in ("supplies", "payments", "evidence_documents", "activities", "operations"):
            source[field].extend(purchase[field])
    answer, _ = result(source)
    expected = 100 if restriction == "annual" else 300 if restriction == "liability" else 0
    assert answer["receipt_credit"] == expected


@pytest.mark.parametrize(
    "collection,field,value",
    [
        ("payments", "transaction_id", "unknown"),
        ("payments", "date", "2026-05-19"),
        ("payments", "amount", 110_000),
        ("payments", "method", "bank_transfer"),
        ("evidence_documents", "transaction_id", "unknown"),
        ("evidence_documents", "payment_id", "unknown"),
        ("evidence_documents", "date", "2026-05-21"),
        ("evidence_documents", "amount", 44_000),
        ("evidence_documents", "stated_vat", 4_000),
        ("evidence_documents", "document_type", "invoice"),
    ],
)
def test_conflicting_links_dates_amounts_and_tax_display_are_rejected(collection, field, value):
    source = sale_source()
    source[collection][0][field] = value
    with pytest.raises(ValueError):
        interpret(source)


@pytest.mark.parametrize(
    "collection,field,value",
    [
        ("supplies", "amount", True),
        ("supplies", "amount", 110_000.0),
        ("supplies", "amount", 0),
        ("supplies", "amount", 110_001),
        ("supplies", "includes_vat", 1),
        ("supplies", "taxable", 1),
        ("supplies", "counterparty_consumer", 1),
        ("supplies", "date", "20260520"),
        ("payments", "amount", True),
        ("payments", "includes_vat", 1),
        ("evidence_documents", "amount", True),
        ("evidence_documents", "includes_vat", 1),
        ("evidence_documents", "vat_separately_stated", 1),
        ("evidence_documents", "stated_vat", True),
    ],
)
def test_numeric_boolean_and_calendar_types_are_strict(collection, field, value):
    source = sale_source()
    source[collection][0][field] = value
    with pytest.raises(ValueError):
        interpret(source)


@pytest.mark.parametrize(
    "collection,field,value",
    [
        ("payments", "amount", 44_000),
        ("evidence_documents", "vat_separately_stated", False),
        ("evidence_documents", "amount", True),
    ],
)
def test_same_identity_with_conflicting_content_is_rejected(collection, field, value):
    source = sale_source()
    copy = deepcopy(source[collection][0])
    copy[field] = value
    source[collection].append(copy)
    with pytest.raises(ValueError, match="Conflicting documentary identity"):
        interpret(source)


def test_duplicate_identity_distinguishes_boolean_from_numeric_one():
    source = sale_source()
    source["payments"][0]["amount"] = True
    copy = deepcopy(source["payments"][0])
    copy["amount"] = 1
    source["payments"].append(copy)
    with pytest.raises(ValueError, match="Conflicting documentary identity"):
        interpret(source)


def test_two_distinct_issued_originals_for_one_payment_are_not_assumed_disjoint():
    source = sale_source()
    copy = deepcopy(source["evidence_documents"][0])
    copy["document_id"] = "D-other"
    source["evidence_documents"].append(copy)
    with pytest.raises(ValueError, match="Several issued originals"):
        interpret(source)


def test_partial_or_unstated_invoice_is_rejected():
    source = sale_source()
    source["evidence_documents"] = [invoice()]
    source["evidence_documents"][0].update(amount=50_000, stated_vat=5_000)
    with pytest.raises(ValueError, match="whole actual supply"):
        interpret(source)
    source["evidence_documents"] = [invoice()]
    source["evidence_documents"][0].update(vat_separately_stated=False, stated_vat=None)
    with pytest.raises(ValueError, match="whole actual supply"):
        interpret(source)


@pytest.mark.parametrize(
    "field",
    [
        "purpose",
        "business_related",
        "issued_receipt_gross",
        "documented_input_vat",
        "eligible",
        "receipt_base",
    ],
)
def test_precomputed_decisions_are_not_raw_source_fields(field):
    source = sale_source()
    source["supplies"][0][field] = 0
    with pytest.raises(ValueError, match="precomputed decision"):
        interpret(source)


def test_purchase_activity_must_name_the_actual_full_evidence_set():
    source = purchase_source()
    source["activities"][0]["document_ids"] = ["D-card"]
    with pytest.raises(ValueError, match="activity link"):
        interpret(source)


@pytest.mark.parametrize(
    "field,value",
    [
        ("issued_receipt_gross", 110_001),
        ("issued_receipt_gross", True),
        ("documented_input_vat", 5_000),
    ],
)
def test_engine_rejects_invalid_optional_normalized_amounts(field, value):
    normalized = interpret(purchase_source() if field == "documented_input_vat" else sale_source())
    for row in normalized["transactions"]:
        row[field] = value
    with pytest.raises(ValueError):
        calculate(normalized)


def test_optional_normalized_amounts_must_agree_across_internal_duplicates():
    normalized = interpret(purchase_source())
    normalized["transactions"][1]["documented_input_vat"] = 0
    with pytest.raises(ValueError, match="conflicting duplicate facts"):
        calculate(normalized)


def test_all_300_frozen_batch_one_vat_answers_and_traces_are_unchanged():
    records = {}
    for case, _ in load_cases(1, domain="C_vat"):
        answer, trace = registry_calculate("C_vat", case["facts"])
        encoded = json.dumps(
            {"answer": answer, "trace": trace},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        records[case["case_id"]] = hashlib.sha256(encoded).hexdigest()
    assert len(records) == 300
    assert hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest() == (
        "4b63a47229a4c6f28482f70ab816ef569c31f9b063aca9ec10cb6bcf28f6e9f3"
    )


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
def test_public_registry_restores_actual_nested_documents(tmp_path, fmt):
    from KrRubberStamp.registry import calculate as registered_calculate
    from render.authored import render_authored
    from render.documents import restore_scenario

    facts = sale_source()
    documents = [
        {
            "filename": "원본." + fmt,
            "format": fmt,
            "title": "원자료 연결 통합 검산",
            "note": "합성 원자료의 실제 기재를 복원하여 대조합니다.",
            "fields": list(facts),
        }
    ]
    render_authored(facts, tmp_path, "C_vat", documents)
    restored = restore_scenario(tmp_path)
    assert restored == facts
    answer, trace = registered_calculate("C_vat", restored)
    assert (
        answer["output_vat"] == 10_000
        and answer["receipt_credit"] == 715
        and answer["net_vat"] == 9_285
    )
    assert trace[0]["rule_id"] == "C_DOCUMENT_RECONCILIATION"
    if fmt == "xlsx":
        import json
        from openpyxl import load_workbook

        mapping = json.loads((tmp_path / "extraction_map.json").read_text())
        workbook = load_workbook(tmp_path / "inputs/원본.xlsx")
        for path, amount in [
            (["payments", 0, "amount"], 44000),
            (["evidence_documents", 0, "amount"], 44000),
            (["evidence_documents", 0, "stated_vat"], 4000),
        ]:
            record = next(row for row in mapping["records"] if row["path"] == path)
            selector = record["selector"]
            workbook[selector["sheet"]][selector["cell"]] = amount
        workbook.save(tmp_path / "inputs/원본.xlsx")
        workbook.close()
        after, _ = registered_calculate("C_vat", restore_scenario(tmp_path))
        assert (
            after["output_vat"] == 10_000
            and after["receipt_credit"] == 572
            and after["net_vat"] == 9_428
        )


@pytest.mark.parametrize("field", ["issued_receipt_gross", "documented_input_vat"])
def test_legacy_raw_contract_cannot_supply_new_compiler_conclusions(field):
    case = next(
        case
        for case, _ in load_cases(1, domain="C_vat")
        if case["facts"].get("source_contract") == "vat_activity_evidence_v1"
    )
    facts = deepcopy(case["facts"])
    assert facts["source_contract"] == "vat_activity_evidence_v1"
    facts["transactions"][0][field] = 1
    with pytest.raises(ValueError, match="documentary derived fields"):
        registry_calculate("C_vat", facts)
