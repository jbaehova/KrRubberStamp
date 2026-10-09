"""Private final billing terms feed the existing VAT arithmetic unchanged."""

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from rules.c_vat import bank_reconciliation, batch_allocation
from rules.c_vat.itemized_activity import (
    CONTRACT,
    RULE_ID,
    SOURCE_OPTIONAL,
    SOURCE_REQUIRED,
    TRANSACTION_OPTIONAL,
    TRANSACTION_REQUIRED,
    calculate,
)

FIXTURE = Path(__file__).parent / "fixtures/vat_itemized_activity.yaml"


def source(index=0):
    return yaml.safe_load(FIXTURE.read_text())[index]["facts"]


EXPECTED = [
    {
        "tax_base": 350_000,
        "output_vat": 35_000,
        "input_vat": 0,
        "noncreditable_vat": 0,
        "deductible_input_vat": 0,
        "receipt_credit": 5005,
        "prepaid_vat": 0,
        "net_vat": 29_995,
        "payable_vat": 29_995,
        "refund_vat": 0,
        "unique_transaction_count": 1,
    },
    {
        "tax_base": 300_000,
        "output_vat": 30_000,
        "input_vat": 11_500,
        "noncreditable_vat": 0,
        "deductible_input_vat": 11_500,
        "receipt_credit": 4290,
        "prepaid_vat": 0,
        "net_vat": 14_210,
        "payable_vat": 14_210,
        "refund_vat": 0,
        "unique_transaction_count": 2,
    },
]


@pytest.mark.parametrize("index", [0, 1])
def test_two_individually_authored_examples_all_eleven_fields_and_manual_lines(index):
    raw = source(index)
    before = deepcopy(raw)
    answer, trace = calculate(raw)
    assert answer == EXPECTED[index]
    assert raw == before
    assert trace[0]["rule_id"] == RULE_ID
    manual = yaml.safe_load(FIXTURE.read_text())[index]["manual_lines"]
    derived = {row["transaction_id"]: row for row in trace[0]["output"]["invoice_amounts"]}
    for expected in manual:
        row = derived[expected["transaction_id"]]
        assert sorted(line["line_supply"] for line in row["lines"]) == sorted(
            expected["line_supplies"]
        )
        for field in (
            "merchandise_supply",
            "document_discount",
            "freight_supply",
            "final_supply",
            "final_vat",
            "final_gross",
        ):
            assert row[field] == expected[field]


@pytest.mark.parametrize(
    "level,field,value,base,credit,net",
    [
        ("line", "quantity", 4, 440_000, 6292, 37_708),
        ("line", "unit_discount", 20_000, 320_000, 4576, 27_424),
        ("line", "line_discount", 30_000, 340_000, 4862, 29_138),
        ("document", "document_discount", 30_000, 340_000, 4862, 29_138),
        ("document", "freight_supply", 30_000, 360_000, 5148, 30_852),
    ],
)
def test_each_actual_price_term_changes_the_full_answer(level, field, value, base, credit, net):
    raw = source()
    row = raw["transactions"][0]
    (row["invoice_lines"][0] if level == "line" else row)[field] = value
    answer, _ = calculate(raw)
    assert answer == {
        **EXPECTED[0],
        "tax_base": base,
        "output_vat": base // 10,
        "receipt_credit": credit,
        "net_vat": net,
        "payable_vat": net,
    }


def test_actual_next_period_delivery_is_independent_of_price_and_payment():
    raw = source(1)
    assert calculate(raw)[0] == EXPECTED[1]
    raw["transactions"][2]["date"] = "2026-06-30"
    raw["activities"][1]["date"] = "2026-06-30"
    assert calculate(raw)[0] == {
        **EXPECTED[1],
        "input_vat": 31_500,
        "deductible_input_vat": 31_500,
        "receipt_credit": 0,
        "net_vat": -1500,
        "payable_vat": 0,
        "refund_vat": 1500,
        "unique_transaction_count": 3,
    }


def test_invoice_issuance_dominates_card_credit_without_price_change():
    raw = source()
    second = deepcopy(raw["transactions"][0])
    second.update(document_id="별도전자", evidence="tax_invoice", invoice_issued=True)
    raw["transactions"].append(second)
    assert calculate(raw)[0] == {
        **EXPECTED[0],
        "receipt_credit": 0,
        "net_vat": 35_000,
        "payable_vat": 35_000,
    }


def test_same_actual_different_document_line_presentation_is_counted_once():
    raw = source()
    second = deepcopy(raw["transactions"][0])
    second["document_id"] = "같은인도다른카드"
    second["invoice_lines"] = [
        {
            "line_id": "확정묶음",
            "description": "동일 상품을 묶은 확정 공급가",
            "quantity": 1,
            "unit_supply_price": 350_000,
            "unit_discount": 0,
            "line_discount": 0,
        }
    ]
    second.update(document_discount=0, freight_supply=0)
    raw["transactions"].append(second)
    answer, trace = calculate(raw)
    assert answer == EXPECTED[0]
    assert len(trace[0]["output"]["invoice_amounts"]) == 2
    assert next(row for row in trace if row["rule_id"] == "VAT_DEDUP")["output"] == {
        "occurrences": 2,
        "invoice_issued": False,
        "counted_once": True,
    }


def test_distinct_actual_transactions_with_equal_prices_are_not_merged():
    raw = source()
    second = deepcopy(raw["transactions"][0])
    second.update(transaction_id="별도인도", document_id="별도카드")
    raw["transactions"].append(second)
    assert calculate(raw)[0] == {
        **EXPECTED[0],
        "tax_base": 700_000,
        "output_vat": 70_000,
        "receipt_credit": 10_010,
        "net_vat": 59_990,
        "payable_vat": 59_990,
        "unique_transaction_count": 2,
    }


def test_exact_document_copies_deduplicate_without_changing_law_trace():
    raw = source(1)
    expected_answer, expected_trace = calculate(raw)
    raw["transactions"] += deepcopy(raw["transactions"])
    answer, trace = calculate(raw)
    assert answer == expected_answer
    assert trace[1:] == expected_trace[1:]
    assert trace[0]["inputs"] == expected_trace[0]["inputs"]
    assert trace[0]["output"]["deduplicated_document_ids"] == sorted(
        row["document_id"] for row in source(1)["transactions"]
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("transaction_id", "foreign"),
        ("description", "같은 번호의 다른 원본"),
        ("freight_supply", 30_000),
        ("invoice_issued", True),
        ("date", "2026-06-17"),
    ],
)
def test_conflicting_same_document_id_rejected_even_outside_period(field, value):
    raw = source()
    raw["transactions"][0]["date"] = "2026-07-01"
    second = deepcopy(raw["transactions"][0])
    second[field] = value
    raw["transactions"].append(second)
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("freight_supply", 30_000),
        ("date", "2026-06-17"),
        ("direction", "purchase"),
        ("counterparty_consumer", False),
        ("supplier_general", False),
        ("vehicle_subject_excise", True),
        ("vat_separately_stated", True),
    ],
)
def test_same_actual_conflicts_are_rejected_after_line_reconstruction(field, value):
    raw = source()
    second = deepcopy(raw["transactions"][0])
    second["document_id"] = "다른문서"
    second[field] = value
    raw["transactions"].append(second)
    with pytest.raises(ValueError):
        calculate(raw)


def test_complete_trace_is_stable_under_all_source_collection_permutations():
    raw = source(1)
    raw["transactions"][0]["invoice_lines"] += [
        {
            "line_id": "무료부속",
            "description": "무료 부속",
            "quantity": 1,
            "unit_supply_price": 0,
            "unit_discount": 0,
            "line_discount": 0,
        }
    ]
    raw["activities"][0]["participants"].append(
        {"name": "가상소영", "role": "employee", "organization": raw["business_name"]}
    )
    expected = calculate(raw)
    raw["transactions"].reverse()
    raw["activities"].reverse()
    raw["operations"].reverse()
    for row in raw["transactions"]:
        row["invoice_lines"].reverse()
    for activity in raw["activities"]:
        activity["document_ids"].reverse()
        activity["participants"].reverse()
    assert calculate(raw) == expected


def test_no_mutable_aliases_between_source_answer_or_each_trace_branch():
    raw = source(1)
    before = deepcopy(raw)
    expected = calculate(raw)
    answer, trace = calculate(raw)
    answer["net_vat"] = 1
    assert trace == expected[1]
    trace[0]["inputs"]["transactions"][0]["invoice_lines"][0]["quantity"] = 999
    trace[0]["output"]["invoice_amounts"][0]["lines"][0]["quantity"] = 888
    trace[1]["inputs"]["activities"][0]["description"] = "변경"
    assert raw == before
    assert calculate(raw) == expected
    trace[-1]["output"]["net_vat"] = 2
    assert answer["net_vat"] == 1


@pytest.mark.parametrize("field", sorted(SOURCE_REQUIRED))
def test_every_required_top_field_is_required(field):
    raw = source()
    raw.pop(field)
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("field", sorted(TRANSACTION_REQUIRED))
def test_every_required_transaction_field_is_required(field):
    raw = source()
    raw["transactions"][0].pop(field)
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field",
    ["line_id", "description", "quantity", "unit_supply_price", "unit_discount", "line_discount"],
)
def test_every_required_line_field_is_required(field):
    raw = source()
    raw["transactions"][0]["invoice_lines"][0].pop(field)
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("scope", ["source", "transaction", "line", "operation", "activity"])
@pytest.mark.parametrize("field", ["unknown", "purpose", "invoice_total", "amount", "includes_vat"])
def test_unknown_nested_and_derived_fields_are_rejected(scope, field):
    raw = source(1)
    row = {
        "source": raw,
        "transaction": raw["transactions"][0],
        "line": raw["transactions"][0]["invoice_lines"][0],
        "operation": raw["operations"][0],
        "activity": raw["activities"][0],
    }[scope]
    row[field] = 0
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("scope", ["source", "transaction", "line", "activity"])
def test_nested_source_contracts_rejected(scope):
    raw = source(1)
    if scope == "source":
        raw["scope_note"] = {"source_contract": bank_reconciliation.CONTRACT}
    else:
        row = {
            "transaction": raw["transactions"][0],
            "line": raw["transactions"][0]["invoice_lines"][0],
            "activity": raw["activities"][0],
        }[scope]
        row["source_contract"] = bank_reconciliation.CONTRACT
    with pytest.raises(ValueError, match="Nested"):
        calculate(raw)


@pytest.mark.parametrize(
    "field", ["quantity", "unit_supply_price", "unit_discount", "line_discount"]
)
@pytest.mark.parametrize("value", [True, False, 1.0, "1", -1])
def test_line_integers_are_strict(field, value):
    raw = source()
    raw["transactions"][0]["invoice_lines"][0][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("field", ["document_discount", "freight_supply"])
@pytest.mark.parametrize("value", [True, False, 1.0, "1", -1])
def test_document_integers_are_strict(field, value):
    raw = source()
    raw["transactions"][0][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_contract", "vat_activity_evidence_v1"),
        ("billing_policy", ""),
        ("billing_policy", False),
        ("taxpayer_type", "simplified"),
        ("business_type", "other"),
        ("business_name", " "),
        ("consumer_facing_business", 1),
        ("period_start", "20260101"),
        ("period_start", "2025-01-01"),
        ("period_end", "2026-12-31"),
        ("period_end", "2026-02-30"),
        ("receipt_credit_previously_claimed", True),
        ("prepaid_assessed_vat", -1),
        ("prior_year_site_supply_base", 1.0),
        ("scope_note", None),
        ("domain", "B_payroll"),
        ("reference_period", "2025"),
        ("operations", {}),
        ("activities", {}),
        ("transactions", []),
        ("transactions", {}),
    ],
)
def test_top_scope_types_and_bounds(field, value):
    raw = source()
    raw[field] = value
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("field", ["scope_note", "synthetic_id", "filing_site_id"])
def test_optional_text_fields_are_strict(field):
    raw = source()
    raw[field] = True
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize("field", sorted(TRANSACTION_OPTIONAL | {"invoice_issued", "taxable"}))
def test_optional_transaction_ids_and_boolean_facts_are_strict(field):
    raw = source()
    raw["transactions"][0][field] = 1
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("direction", "refund"),
        ("evidence", "quotation"),
        ("date", "20260616"),
        ("date", True),
        ("description", ""),
        ("transaction_id", " "),
        ("document_id", 1),
        ("taxable", False),
        ("vat_separately_stated", 1),
        ("counterparty_consumer", 1),
        ("invoice_lines", []),
        ("invoice_lines", {}),
        ("freight_supply", 1_000_000_001),
        ("document_discount", 350_001),
    ],
)
def test_transaction_scope_and_limits_even_when_excluded(field, value):
    raw = source()
    raw["transactions"][0]["date"] = "2026-07-01"
    raw["transactions"][0][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("quantity", 0),
        ("quantity", 10_001),
        ("quantity", 10_000),  # Current 100000-unit price exceeds the line-principal bound.
        ("unit_supply_price", 1_000_000_001),
        ("unit_discount", 100_001),
        ("line_discount", 270_001),
        ("line_id", ""),
        ("description", False),
    ],
)
def test_line_bounds(field, value):
    raw = source()
    if field == "quantity" and value == 10_000:
        raw["transactions"][0]["invoice_lines"][0]["unit_supply_price"] = 100_010
    raw["transactions"][0]["invoice_lines"][0][field] = value
    with pytest.raises(ValueError):
        calculate(raw)


def test_free_accessory_line_is_allowed_but_zero_whole_supply_is_rejected():
    raw = source()
    row = raw["transactions"][0]
    free = deepcopy(row["invoice_lines"][0])
    free.update(line_id="무료", unit_supply_price=0, unit_discount=0, line_discount=0)
    row["invoice_lines"].append(free)
    assert calculate(raw)[0] == EXPECTED[0]
    row["invoice_lines"] = [free]
    row.update(document_discount=0, freight_supply=0)
    with pytest.raises(ValueError):
        calculate(raw)
    row["freight_supply"] = 10
    assert calculate(raw)[0]["output_vat"] == 1


def test_discount_boundaries_and_final_only_exact_vat_requirement():
    raw = source()
    row = raw["transactions"][0]
    row["document_discount"] = 350_000
    assert calculate(raw)[0]["tax_base"] == 20_000  # Freight is not discounted.
    row["freight_supply"] = 0
    with pytest.raises(ValueError):
        calculate(raw)
    raw = source()
    row = raw["transactions"][0]
    row["invoice_lines"][0]["unit_discount"] = 100_000
    row["invoice_lines"][0]["line_discount"] = 0
    row["document_discount"] = 0
    assert calculate(raw)[0]["tax_base"] == 120_000
    row["invoice_lines"][1]["line_discount"] = 100_000
    assert calculate(raw)[0]["tax_base"] == 20_000
    row["invoice_lines"][0].update(quantity=1, unit_supply_price=3, unit_discount=0)
    row["invoice_lines"][1].update(quantity=1, unit_supply_price=7, line_discount=0)
    row.update(document_discount=0, freight_supply=0)
    assert calculate(raw)[0]["output_vat"] == 1
    row["invoice_lines"][0]["unit_supply_price"] = 4
    with pytest.raises(ValueError, match="exact 10%"):
        calculate(raw)


def test_price_principal_quantity_and_six_line_inclusive_bounds():
    raw = source()
    row = raw["transactions"][0]
    prototype = deepcopy(row["invoice_lines"][0])
    prototype.update(quantity=1, unit_supply_price=1_000_000_000, unit_discount=0, line_discount=0)
    row["invoice_lines"] = [{**prototype, "line_id": f"L{i}"} for i in range(6)]
    row.update(document_discount=0, freight_supply=1_000_000_000)
    assert calculate(raw)[0]["tax_base"] == 7_000_000_000
    row["invoice_lines"].append({**prototype, "line_id": "L6"})
    with pytest.raises(ValueError, match="six"):
        calculate(raw)
    row["invoice_lines"] = [prototype]
    prototype.update(quantity=10_000, unit_supply_price=100_000)
    assert calculate(raw)[0]["tax_base"] == 2_000_000_000
    row["invoice_lines"].append(deepcopy(prototype))
    with pytest.raises(ValueError, match="line_id"):
        calculate(raw)


def test_sixteen_actuals_32_documents_and_strict_maximum_boundaries():
    raw = source()
    row = raw["transactions"][0]
    raw["transactions"] = [
        {**deepcopy(row), "transaction_id": f"T{i}", "document_id": f"D{i}"} for i in range(16)
    ]
    assert calculate(raw)[0]["unique_transaction_count"] == 16
    raw["transactions"] += deepcopy(raw["transactions"])
    assert calculate(raw)[0]["unique_transaction_count"] == 16
    raw["transactions"].append(deepcopy(row))
    with pytest.raises(ValueError, match="32"):
        calculate(raw)
    raw["transactions"] = raw["transactions"][:16] + [deepcopy(row)]
    with pytest.raises(ValueError, match="16 actual"):
        calculate(raw)


@pytest.mark.parametrize(
    "alter",
    [
        lambda raw: raw["transactions"][1].pop("activity_id"),
        lambda raw: raw["transactions"][1].update(activity_id="unknown"),
        lambda raw: raw["transactions"][1].update(date="2026-06-11"),
        lambda raw: raw["transactions"][1].update(document_id="unknown"),
        lambda raw: raw["transactions"][1].pop("supplier_general"),
        lambda raw: raw["transactions"][1].pop("vehicle_direct_business"),
        lambda raw: raw["activities"][0].update(operation_id="unknown"),
        lambda raw: raw["activities"].append(deepcopy(raw["activities"][0])),
        lambda raw: raw["activities"][0]["document_ids"].append("unknown"),
        lambda raw: raw["activities"][0]["participants"][0].update(organization="foreign"),
        lambda raw: raw["transactions"][0].update(activity_id="현재수령"),
    ],
)
def test_existing_activity_and_evidence_constraints_remain_strict(alter):
    raw = source(1)
    alter(raw)
    with pytest.raises(ValueError):
        calculate(raw)


def registered_source():
    raw = source(1)
    for row in raw["transactions"][1:]:
        row.pop("supplier_general")
        row["supplier_id"] = "공급자"
    raw["supplier_status_records"] = [
        {
            "supplier_id": "공급자",
            "status": "general",
            "valid_from": "2026-01-01",
            "valid_to": "2026-06-30",
        },
        {
            "supplier_id": "공급자",
            "status": "simplified_no_invoice_duty",
            "valid_from": "2026-07-01",
            "valid_to": "2026-12-31",
        },
    ]
    raw.pop("prior_year_site_supply_base")
    raw["filing_site_id"] = "사업장"
    raw["site_year_records"] = [
        {
            "site_id": "사업장",
            "site_name": raw["business_name"],
            "year": 2025,
            "supply_base": 90_000_000,
        },
        {
            "site_id": "사업장",
            "site_name": raw["business_name"],
            "year": 2024,
            "supply_base": 10_000_000,
        },
    ]
    return raw


def test_existing_supplier_and_site_registers_select_by_actual_date_and_year():
    raw = registered_source()
    expected = calculate(raw)
    assert expected[0] == EXPECTED[1]
    raw["supplier_status_records"].reverse()
    raw["site_year_records"].reverse()
    assert calculate(raw) == expected
    raw["supplier_status_records"][1]["status"] = "simplified_no_invoice_duty"
    changed = calculate(raw)[0]
    assert changed == {
        **EXPECTED[1],
        "noncreditable_vat": 11_500,
        "deductible_input_vat": 0,
        "net_vat": 25_710,
        "payable_vat": 25_710,
    }


@pytest.mark.parametrize(
    "alter",
    [
        lambda raw: raw["transactions"][1].update(supplier_general=True),
        lambda raw: raw["transactions"][1].update(supplier_id="unknown"),
        lambda raw: raw["supplier_status_records"][0].update(valid_to="2026-06-01"),
        lambda raw: raw["supplier_status_records"][1].update(valid_from="2026-06-01"),
        lambda raw: raw["supplier_status_records"][0].update(derived_status=True),
        lambda raw: raw.update(prior_year_site_supply_base=90_000_000),
        lambda raw: raw["site_year_records"][0].update(site_name="foreign"),
        lambda raw: raw["site_year_records"][0].update(year=True),
        lambda raw: raw["site_year_records"].append(deepcopy(raw["site_year_records"][0])),
    ],
)
def test_existing_register_conflicts_and_preselected_status_are_rejected(alter):
    raw = registered_source()
    alter(raw)
    with pytest.raises(ValueError):
        calculate(raw)


def test_registered_vehicle_classification_still_comes_from_raw_vehicle_record():
    raw = source(1)
    raw["transactions"] = raw["transactions"][1:2]
    raw["activities"] = raw["activities"][:1]
    purchase, activity = raw["transactions"][0], raw["activities"][0]
    purchase.pop("vehicle_subject_excise")
    purchase.pop("vehicle_direct_business")
    purchase["vehicle_id"] = "차량"
    activity.update(action="vehicle_delivery", vehicle_id="차량")
    raw["vehicle_registry"] = [
        {
            "vehicle_id": "차량",
            "registration_class": "excise_passenger",
            "business_license": "none",
            "permitted_operation_id": None,
        }
    ]
    answer, _ = calculate(raw)
    assert (answer["input_vat"], answer["noncreditable_vat"], answer["refund_vat"]) == (
        11_500,
        11_500,
        0,
    )
    raw["vehicle_registry"][0].update(
        business_license="vehicle_sales", permitted_operation_id="매장판매"
    )
    assert calculate(raw)[0]["refund_vat"] == 11_500
    purchase["vehicle_subject_excise"] = True
    with pytest.raises(ValueError, match="preselected"):
        calculate(raw)


def bank_source(index=0):
    facts = source(index)
    return {
        "source_contract": bank_reconciliation.CONTRACT,
        "processing_policy": "사적 확정 신고와 실행 이체만 대조한다.",
        "as_of_date": "2026-08-31",
        "filings": [
            {
                "filing_id": "F",
                "taxpayer_id": "T",
                "registration_id": "R",
                "business_name": facts["business_name"],
                "facts": facts,
            }
        ],
        "transfers": [
            {
                "transfer_id": "이체",
                "filing_id": "F",
                "registration_id": "R",
                "date": "2026-07-27",
                "status": "executed",
                "kind": "settlement_payment",
                "amount": 10_000,
            }
        ],
    }


@pytest.mark.parametrize("index", [0, 1])
def test_bank_parent_explicitly_accepts_only_full_new_raw_child_and_preserves_trace(index):
    raw = bank_source(index)
    expected_child, expected_trace = calculate(raw["filings"][0]["facts"])
    answer, trace = bank_reconciliation.calculate(raw)
    assert answer["filing_calculations"][0]["calculation"] == EXPECTED[index] == expected_child
    assert trace[0]["output"]["filing_derivations"][0]["trace"] == expected_trace
    assert answer["balance_total"] == EXPECTED[index]["net_vat"] - 10_000
    raw["filings"][0]["facts"]["transactions"][0]["invoice_lines"][0]["quantity"] += 1
    assert bank_reconciliation.calculate(raw)[0]["balance_total"] != answer["balance_total"]


def test_batch_parent_accepts_new_raw_child_and_keeps_explicit_bank_fee_separate():
    raw = bank_source()
    batch = {
        "source_contract": batch_allocation.CONTRACT,
        "processing_policy": "확정 구성지시의 원금과 은행 수수료를 구분한다.",
        "as_of_date": raw["as_of_date"],
        "filings": raw["filings"],
        "bank_executions": [
            {
                "execution_id": "E",
                "date": "2026-07-27",
                "status": "executed",
                "direction": "debit",
                "amount": 10_100,
                "bank_fee": 100,
            }
        ],
        "allocation_instructions": [
            {
                "instruction_id": "I",
                "execution_id": "E",
                "filing_id": "F",
                "registration_id": "R",
                "kind": "settlement_payment",
                "amount": 10_000,
            }
        ],
    }
    answer, _ = batch_allocation.calculate(batch)
    assert answer["filing_calculations"][0]["calculation"] == EXPECTED[0]
    assert (answer["paid_total"], answer["balance_total"]) == (10_000, 19_995)
    assert answer["bank_cash_totals"] == {
        "debit_total": 10_100,
        "credit_total": 0,
        "fee_total": 100,
        "assessed_debit_total": 0,
        "settlement_net_outflow": 10_000,
    }


@pytest.mark.parametrize(
    "alter",
    [
        lambda raw: raw["filings"][0]["facts"].pop("billing_policy"),
        lambda raw: raw["filings"][0]["facts"].update(billing_policy={"source_contract": CONTRACT}),
        lambda raw: raw["filings"][0]["facts"].update(facts=source()),
        lambda raw: raw["filings"][0]["facts"].update(source_contract=bank_reconciliation.CONTRACT),
        lambda raw: raw["filings"][0]["facts"]["transactions"][0].update(amount=350_000),
        lambda raw: raw["filings"][0]["facts"]["transactions"][0]["invoice_lines"][0].update(
            quantity=True
        ),
        lambda raw: raw["filings"][0]["facts"]["transactions"][0]["invoice_lines"][0].update(
            final_supply=350_000
        ),
        lambda raw: raw["filings"][0]["facts"]["transactions"][0].update(invoice_total=385_000),
    ],
)
def test_parent_new_child_allowlist_cannot_bypass_itemized_validation(alter):
    raw = bank_source()
    alter(raw)
    with pytest.raises(ValueError):
        bank_reconciliation.calculate(raw)


def test_documented_schema_sets_have_no_legacy_scalar_amount_fields():
    assert SOURCE_REQUIRED & SOURCE_OPTIONAL == set()
    assert TRANSACTION_REQUIRED & TRANSACTION_OPTIONAL == set()
    assert {"amount", "includes_vat", "purpose", "business_related"}.isdisjoint(
        TRANSACTION_REQUIRED | TRANSACTION_OPTIONAL
    )
