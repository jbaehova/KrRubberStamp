"""Independent cash arithmetic around unchanged raw VAT child calculations."""

from copy import deepcopy

import pytest

from KrRubberStamp.registry import calculate as calculate_child
from rules.c_vat.bank_reconciliation import CONTRACT, RULE_ID, calculate
from test_vat_document_reconciliation import purchase_source, sale_source
from test_vat_document_lifecycle import corrected_partial_sale


def activity_sale():
    return {
        "source_contract": "vat_activity_evidence_v1",
        "taxpayer_type": "general",
        "period_start": "2026-01-01",
        "period_end": "2026-06-30",
        "business_name": "가상시험점포",
        "business_type": "individual",
        "consumer_facing_business": True,
        "prior_year_site_supply_base": 10_000_000,
        "receipt_credit_previously_claimed": 0,
        "prepaid_assessed_vat": 0,
        "operations": [],
        "activities": [],
        "transactions": [
            {
                "transaction_id": "S",
                "document_id": "INV",
                "direction": "sale",
                "date": "2026-05-20",
                "description": "완료된 국내 과세 공급",
                "amount": 100_000,
                "includes_vat": False,
                "taxable": True,
                "evidence": "tax_invoice",
                "invoice_issued": True,
                "supplier_general": True,
                "vat_separately_stated": True,
                "vehicle_subject_excise": False,
                "vehicle_direct_business": False,
                "counterparty_consumer": False,
            }
        ],
    }


def filing(facts=None, *, identity="F-A", taxpayer="T-A", registration="R-A"):
    facts = activity_sale() if facts is None else facts
    return {
        "filing_id": identity,
        "taxpayer_id": taxpayer,
        "registration_id": registration,
        "business_name": facts["business_name"],
        "facts": facts,
    }


def transfer(identity="PAY-1", *, amount=8_000, **updates):
    return {
        "transfer_id": identity,
        "filing_id": "F-A",
        "registration_id": "R-A",
        "date": "2026-07-27",
        "status": "executed",
        "kind": "settlement_payment",
        "amount": amount,
        **updates,
    }


def source():
    return {
        "source_contract": CONTRACT,
        "processing_policy": "가상 사내 정산 대조: 실행 완료된 이체를 등록번호별로 대조한다.",
        "as_of_date": "2026-08-31",
        "filings": [filing()],
        "transfers": [transfer()],
    }


def test_manual_whole_single_filing_answer_and_unchanged_child_trace():
    raw = source()
    original = deepcopy(raw)
    answer, trace = calculate(raw)
    expected_child = {
        "tax_base": 100_000,
        "output_vat": 10_000,
        "input_vat": 0,
        "noncreditable_vat": 0,
        "deductible_input_vat": 0,
        "receipt_credit": 0,
        "prepaid_vat": 0,
        "net_vat": 10_000,
        "payable_vat": 10_000,
        "refund_vat": 0,
        "unique_transaction_count": 1,
    }
    identifiers = {
        "filing_id": "F-A",
        "taxpayer_id": "T-A",
        "registration_id": "R-A",
        "business_name": "가상시험점포",
    }
    assert answer == {
        "filing_calculations": [{**identifiers, "calculation": expected_child}],
        "registration_settlements": [
            {
                **identifiers,
                "tax_due": 10_000,
                "payable_vat": 10_000,
                "refund_vat": 0,
                "paid": 8_000,
                "received": 0,
                "net_outflow": 8_000,
                "balance": 2_000,
            }
        ],
        "tax_due_total": 10_000,
        "paid_total": 8_000,
        "received_total": 0,
        "balance_total": 2_000,
    }
    assert raw == original
    assert len(trace) == 1 and trace[0]["rule_id"] == RULE_ID
    assert trace[0]["output"]["filing_derivations"] == [
        {
            "filing_id": "F-A",
            "trace": calculate_child("C_vat", raw["filings"][0]["facts"])[1],
        }
    ]
    assert trace[0]["output"]["settlement"] == answer


def test_two_taxpayers_equal_net_totals_preserve_nonzero_separate_balances():
    raw = source()
    raw["filings"].append(
        filing(purchase_source(), identity="F-B", taxpayer="T-B", registration="R-B")
    )
    raw["transfers"].append(
        transfer(
            "REF-B", amount=8_000, filing_id="F-B", registration_id="R-B", kind="settlement_refund"
        )
    )
    answer, _ = calculate(raw)
    assert answer["tax_due_total"] == answer["balance_total"] == 0
    assert answer["paid_total"] == answer["received_total"] == 8_000
    assert [
        (r["registration_id"], r["tax_due"], r["balance"])
        for r in answer["registration_settlements"]
    ] == [("R-A", 10_000, 2_000), ("R-B", -10_000, -2_000)]
    # Receiving all B's refund changes B's own discrepancy, without erasing A's.
    raw["transfers"][1]["amount"] = 10_000
    changed, _ = calculate(raw)
    assert [r["balance"] for r in changed["registration_settlements"]] == [2_000, 0]


def test_distinct_equal_split_payments_count_but_exact_copies_deduplicate():
    raw = source()
    raw["transfers"] = [transfer("P1", amount=4_000), transfer("P2", amount=4_000)]
    expected, _ = calculate(raw)
    raw["transfers"].extend(deepcopy(raw["transfers"]))
    answer, trace = calculate(raw)
    assert answer == expected
    assert (answer["paid_total"], answer["balance_total"]) == (8_000, 2_000)
    assert trace[0]["output"]["accepted_transfer_ids"] == ["P1", "P2"]
    assert trace[0]["output"]["deduplicated_transfer_ids"] == ["P1", "P2"]
    assert len(trace[0]["inputs"]["transfers"]) == 2


def test_planned_future_and_assessed_prepayment_are_all_excluded():
    raw = source()
    raw["transfers"] += [
        transfer("PLAN", amount=2_000, status="planned"),
        transfer("FUTURE", amount=2_000, date="2026-09-01"),
        transfer("NOTICE", amount=500_000, kind="assessed_prepayment", date="2026-04-25"),
        transfer(
            "ALL", amount=500_000, kind="assessed_prepayment", status="planned", date="2026-09-01"
        ),
    ]
    answer, trace = calculate(raw)
    assert (answer["paid_total"], answer["balance_total"]) == (8_000, 2_000)
    assert trace[0]["output"]["excluded_transfers"] == [
        {
            "transfer_id": "ALL",
            "reasons": ["planned", "after_cutoff", "already_in_child_assessment"],
        },
        {"transfer_id": "FUTURE", "reasons": ["after_cutoff"]},
        {"transfer_id": "NOTICE", "reasons": ["already_in_child_assessment"]},
        {"transfer_id": "PLAN", "reasons": ["planned"]},
    ]


def test_assessed_notice_in_child_is_not_subtracted_again_from_bank_rows():
    raw = source()
    raw["filings"][0]["facts"]["transactions"][0]["amount"] = 10_000_000
    raw["filings"][0]["facts"]["prepaid_assessed_vat"] = 500_000
    raw["transfers"] = [
        transfer("SETTLE", amount=500_000),
        transfer("ADVANCE", amount=500_000, kind="assessed_prepayment", date="2026-04-25"),
    ]
    answer, _ = calculate(raw)
    child = answer["filing_calculations"][0]["calculation"]
    assert (child["output_vat"], child["prepaid_vat"], child["payable_vat"]) == (
        1_000_000,
        500_000,
        500_000,
    )
    assert (answer["tax_due_total"], answer["paid_total"], answer["balance_total"]) == (
        500_000,
        500_000,
        0,
    )
    raw["transfers"][1]["amount"] = 999_999  # Ledger amount never supplies child assessment.
    assert calculate(raw)[0] == answer


def test_overpayment_and_partial_received_refund_remain_signed_ledger_positions():
    raw = source()
    raw["transfers"][0]["amount"] = 12_000
    assert calculate(raw)[0]["registration_settlements"][0]["balance"] == -2_000
    raw["filings"] = [filing(purchase_source())]
    raw["transfers"] = [transfer("REFUND", amount=3_000, kind="settlement_refund")]
    row = calculate(raw)[0]["registration_settlements"][0]
    assert (row["tax_due"], row["received"], row["net_outflow"], row["balance"]) == (
        -10_000,
        3_000,
        -3_000,
        -7_000,
    )


@pytest.mark.parametrize("factory", [activity_sale, sale_source, corrected_partial_sale])
def test_all_three_raw_children_preserve_entire_original_answer_and_trace(factory):
    facts = factory()
    child_answer, child_trace = calculate_child("C_vat", deepcopy(facts))
    raw = source()
    raw["filings"] = [filing(facts)]
    answer, trace = calculate(raw)
    assert answer["filing_calculations"][0]["calculation"] == child_answer
    assert trace[0]["output"]["filing_derivations"][0]["trace"] == child_trace


def test_parent_row_permutations_are_fully_deterministic():
    raw = source()
    raw["filings"] += [
        filing(purchase_source(), identity="F-B", taxpayer="T-B", registration="R-B")
    ]
    raw["transfers"] += [
        transfer("P2", amount=1_000),
        transfer("PLAN", amount=1_000, status="planned"),
        transfer(
            "REF-B", amount=5_000, kind="settlement_refund", filing_id="F-B", registration_id="R-B"
        ),
    ]
    raw["transfers"].append(deepcopy(raw["transfers"][0]))
    expected = calculate(raw)
    raw["filings"].reverse()
    raw["transfers"].reverse()
    assert calculate(raw) == expected


def test_returned_answer_trace_and_caller_have_no_shared_mutable_containers():
    raw = source()
    expected = calculate(deepcopy(raw))
    answer, trace = calculate(raw)
    answer["filing_calculations"][0]["calculation"]["payable_vat"] = 123
    answer["registration_settlements"][0]["paid"] = 456
    assert trace == expected[1]
    trace[0]["inputs"]["filings"][0]["facts"]["transactions"][0]["amount"] = 789
    trace[0]["output"]["filing_derivations"][0]["trace"][0]["inputs"]["operations"].append({})
    trace[0]["output"]["settlement"]["registration_settlements"][0]["paid"] = 111
    assert calculate(raw) == expected
    assert answer["registration_settlements"][0]["paid"] == 456


@pytest.mark.parametrize("field", ["filing_id", "taxpayer_id", "registration_id"])
def test_duplicate_filing_or_taxpayer_or_registration_is_rejected(field):
    raw = source()
    second = filing(identity="F-B", taxpayer="T-B", registration="R-B")
    second[field] = raw["filings"][0][field]
    raw["filings"].append(second)
    with pytest.raises(ValueError, match="Duplicate|independent"):
        calculate(raw)


@pytest.mark.parametrize("scope", ["source", "filing", "transfer", "child"])
@pytest.mark.parametrize("defect", ["extra", "missing"])
def test_unknown_and_missing_fields_are_rejected(scope, defect):
    raw = source()
    row, missing = {
        "source": (raw, "processing_policy"),
        "filing": (raw["filings"][0], "taxpayer_id"),
        "transfer": (raw["transfers"][0], "kind"),
        "child": (raw["filings"][0]["facts"], "taxpayer_type"),
    }[scope]
    if defect == "extra":
        row["unknown_field"] = "value"
    else:
        row.pop(missing)
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("transfer_id", ""),
        ("transfer_id", 1),
        ("filing_id", "unknown"),
        ("registration_id", "foreign"),
        ("date", "20260727"),
        ("date", "2026-02-30"),
        ("date", 20260727),
        ("status", "cancelled"),
        ("status", True),
        ("kind", "tax_credit"),
        ("kind", 1),
        ("amount", True),
        ("amount", 8000.0),
        ("amount", "8000"),
        ("amount", -1),
    ],
)
def test_invalid_transfer_fields_even_on_excluded_rows(field, value):
    raw = source()
    raw["transfers"][0]["status"] = "planned"
    raw["transfers"][0][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("field", ["filing_id", "taxpayer_id", "registration_id", "business_name"])
@pytest.mark.parametrize("value", ["", "  ", True])
def test_filing_text_identifiers_and_business_are_strict(field, value):
    raw = source()
    raw["filings"][0][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_contract", CONTRACT),
        ("source_contract", "unknown"),
        ("source_contract", None),
        ("business_name", "가상다른점포"),
        ("taxpayer_type", "simplified"),
        ("period_start", "2025-01-01"),
        ("period_end", "2026-12-31"),
        ("period_start", "20260101"),
        ("consumer_facing_business", 1),
        ("prepaid_assessed_vat", True),
    ],
)
def test_child_contract_subject_period_and_types_are_explicit(field, value):
    raw = source()
    raw["filings"][0]["facts"][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


def test_bare_engine_child_and_missing_prior_year_source_are_rejected():
    raw = source()
    raw["filings"][0]["facts"].pop("source_contract")
    with pytest.raises(ValueError):
        calculate(raw)
    raw = source()
    raw["filings"][0]["facts"].pop("prior_year_site_supply_base")
    with pytest.raises(ValueError, match="prior-year"):
        calculate(raw)


def test_nested_contract_inside_an_otherwise_optional_child_field_is_rejected():
    raw = source()
    raw["filings"][0]["facts"]["scope_note"] = {"source_contract": CONTRACT}
    with pytest.raises(ValueError, match="Nested"):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("domain", "A_yearend"),
        ("reference_period", "2025"),
        ("scope_note", None),
    ],
)
def test_optional_child_labels_cannot_conflict_with_subject_scope(field, value):
    raw = source()
    raw["filings"][0]["facts"][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field",
    [
        "taxable",
        "includes_vat",
        "invoice_issued",
        "vat_separately_stated",
        "counterparty_consumer",
        "supplier_general",
        "vehicle_subject_excise",
        "vehicle_direct_business",
    ],
)
def test_raw_activity_child_booleans_do_not_accept_integer_aliases(field):
    raw = source()
    raw["filings"][0]["facts"]["transactions"][0][field] = 1
    with pytest.raises(ValueError, match="strict boolean"):
        calculate(raw)


@pytest.mark.parametrize("defect", ["extra", "missing", "wrong_date"])
def test_activity_transaction_exact_fields_and_iso_date(defect):
    raw = source()
    row = raw["filings"][0]["facts"]["transactions"][0]
    if defect == "extra":
        row["nested_contract"] = {"source_contract": CONTRACT}
    elif defect == "missing":
        row.pop("invoice_issued")
    else:
        row["date"] = "20260520"
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("field", ["amount", "status", "kind", "date", "registration_id"])
def test_conflicting_same_id_rejected_even_when_both_rows_excluded(field):
    raw = source()
    raw["transfers"][0]["status"] = "planned"
    other = deepcopy(raw["transfers"][0])
    other[field] = {
        "amount": 8_001,
        "status": "executed",
        "kind": "assessed_prepayment",
        "date": "2026-07-28",
        "registration_id": "foreign",
    }[field]
    raw["transfers"].append(other)
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("field", ["tax_due", "receipt_credit", "balance", "selected_document_ids"])
def test_recursive_precomputed_fields_cannot_be_smuggled_into_raw_child(field):
    raw = source()
    raw["filings"][0]["facts"]["transactions"][0][field] = 0
    with pytest.raises(ValueError, match="precomputed"):
        calculate(raw)


def test_lifecycle_cannot_use_confirmation_after_parent_cutoff():
    raw = source()
    raw["filings"] = [filing(corrected_partial_sale())]
    raw["as_of_date"] = "2026-07-14"
    with pytest.raises(ValueError, match="processing_date"):
        calculate(raw)
    raw["as_of_date"] = "2026-07-15"
    assert calculate(raw)[0]["tax_due_total"] == 94_280
    raw["filings"][0]["facts"]["document_status_records"][0]["confirmed_on"] = "2026-07-16"
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("processing_policy", ""),
        ("processing_policy", False),
        ("as_of_date", "20260831"),
        ("as_of_date", None),
        ("filings", []),
        ("filings", {}),
        ("transfers", {}),
    ],
)
def test_invalid_parent_values(field, value):
    raw = source()
    raw[field] = value
    with pytest.raises(ValueError):
        calculate(raw)


def test_bounded_filings_and_transfer_collections():
    raw = source()
    raw["filings"] += [
        filing(identity="F-B", taxpayer="T-B", registration="R-B"),
        filing(identity="F-C", taxpayer="T-C", registration="R-C"),
    ]
    assert len(calculate(raw)[0]["filing_calculations"]) == 3
    raw["filings"].append(filing(identity="F-D", taxpayer="T-D", registration="R-D"))
    with pytest.raises(ValueError, match="one to three"):
        calculate(raw)
    raw = source()
    raw["transfers"] = [transfer(f"P-{index:03}", amount=0) for index in range(100)]
    assert calculate(raw)[0]["paid_total"] == 0
    raw["transfers"] += deepcopy(raw["transfers"])
    assert len(calculate(raw)[1][0]["output"]["deduplicated_transfer_ids"]) == 100
    raw["transfers"].append(deepcopy(raw["transfers"][0]))
    with pytest.raises(ValueError, match="200"):
        calculate(raw)
    raw["transfers"] = [transfer(f"P-{index:03}", amount=0) for index in range(101)]
    with pytest.raises(ValueError, match="100 unique"):
        calculate(raw)


def test_no_arbitrary_tax_deadline_or_transfer_same_day_requirement():
    raw = source()
    raw["as_of_date"] = "2027-01-31"
    raw["transfers"][0]["date"] = "2027-01-20"
    assert calculate(raw)[0]["balance_total"] == 2_000
    raw["transfers"][0]["date"] = "2026-01-01"
    assert calculate(raw)[0]["balance_total"] == 2_000
    raw["transfers"] = []
    assert calculate(raw)[0]["balance_total"] == 10_000
