"""Authored activity joins must determine purchase treatment from raw facts."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from render.authored import render_authored
from render.documents import restore_scenario
from rules.c_vat.engine import calculate
from rules.c_vat.evidence import CONTRACT, derivation_trace, interpret

PREVIEW = Path(__file__).resolve().parents[1] / "authored/batch_1/C_vat/preview.json"


def authored_case():
    return next(row for row in json.loads(PREVIEW.read_text()) if row["case_id"] == "C002")


def source():
    return authored_case()["facts"]


def one_purchase():
    result = source()
    result["transactions"] = [result["transactions"][2]]
    result["activities"] = [result["activities"][0]]
    return result


def contains_derived(value):
    if isinstance(value, dict):
        return bool({"purpose", "business_related"} & value.keys()) or any(
            contains_derived(child) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_derived(child) for child in value)
    return False


def test_authored_customer_meal_preserves_original_intended_gold():
    raw = source()
    original = deepcopy(raw)
    assert raw["source_contract"] == CONTRACT
    assert not contains_derived(raw)
    normalized = interpret(raw)
    assert raw == original
    assert normalized["transactions"][-1]["purpose"] == "hospitality"
    assert calculate(normalized)[0] == {
        "tax_base": 20_000_000,
        "output_vat": 2_000_000,
        "input_vat": 850_000,
        "noncreditable_vat": 60_000,
        "deductible_input_vat": 790_000,
        "receipt_credit": 171_600,
        "prepaid_vat": 0,
        "net_vat": 1_038_400,
        "payable_vat": 1_038_400,
        "refund_vat": 0,
        "unique_transaction_count": 6,
    }


def test_changing_actual_recipients_to_staff_changes_the_deduction():
    customer_source = source()
    staff_source = deepcopy(customer_source)
    activity = staff_source["activities"][-1]
    for person in activity["participants"][1:]:
        person.update(role="employee", organization=staff_source["business_name"])
    activity["description"] = "공방 직원들이 제작 업무를 마친 뒤 대표와 식사를 했다."
    customer_gold = calculate(interpret(customer_source))[0]
    staff_normalized = interpret(staff_source)
    staff_gold = calculate(staff_normalized)[0]
    assert staff_normalized["transactions"][-1]["purpose"] == "business"
    assert customer_source["transactions"] == staff_source["transactions"]
    assert staff_gold["noncreditable_vat"] == 0
    assert staff_gold["deductible_input_vat"] == customer_gold["deductible_input_vat"] + 60_000
    assert staff_gold["payable_vat"] == customer_gold["payable_vat"] - 60_000


def test_authored_source_roundtrips_real_files_without_compiled_outcomes(tmp_path):
    case = authored_case()
    inputs = render_authored(case["facts"], tmp_path, "C_vat", case["documents"])
    restored = restore_scenario(tmp_path)
    assert restored == case["facts"]
    assert not contains_derived(restored)
    assert len(inputs) == 6
    assert calculate(interpret(restored))[0] == calculate(interpret(case["facts"]))[0]
    from pymupdf import open as open_pdf

    with open_pdf(tmp_path / "inputs/06_납품처_미팅기록.pdf") as document:
        text = "".join(page.get_text() for page in document)
    assert "가상늘봄기획" in text
    assert "가상-C002-대표카드-0522" in text
    assert "hospitality" not in text
    assert "business_related" not in text


@pytest.mark.parametrize(
    "action,place,expected",
    [
        ("delivery", "worksite", "business"),
        ("service", "worksite", "business"),
        ("vehicle_delivery", "worksite", "passenger_car_purchase"),
        ("vehicle_lease", "road", "passenger_car_rental"),
        ("vehicle_service", "worksite", "passenger_car_maintenance"),
        ("ground_work", "land_parcel", "land"),
    ],
)
def test_observable_acquisition_actions_cover_supported_engine_classes(action, place, expected):
    raw = one_purchase()
    activity = raw["activities"][0]
    activity["action"] = action
    activity["location"]["kind"] = place
    if action.startswith("vehicle_"):
        raw["transactions"][0]["vehicle_subject_excise"] = True
    normalized = interpret(raw)
    assert normalized["transactions"][0]["purpose"] == expected
    gold = calculate(normalized)[0]
    assert gold["noncreditable_vat"] == (0 if expected == "business" else 600_000)


def test_exempt_activity_is_connected_to_the_supplied_output_classification():
    raw = one_purchase()
    raw["operations"][0]["output_taxable"] = False
    normalized = interpret(raw)
    assert normalized["transactions"][0]["purpose"] == "exempt_business"
    assert calculate(normalized)[0]["noncreditable_vat"] == 600_000


def test_official_direct_vehicle_use_fact_remains_separate_from_the_activity():
    raw = one_purchase()
    raw["activities"][0]["action"] = "vehicle_delivery"
    raw["transactions"][0].update(vehicle_subject_excise=True, vehicle_direct_business=True)
    normalized = interpret(raw)
    assert normalized["transactions"][0]["purpose"] == "passenger_car_purchase"
    assert calculate(normalized)[0]["deductible_input_vat"] == 600_000


def test_household_use_is_derived_from_actual_place_and_family_participants():
    raw = one_purchase()
    activity = raw["activities"][0]
    activity["location"] = {"name": "대표 가족 거주 주택", "kind": "home"}
    activity["operation_id"] = None
    activity["participants"].append(
        {"name": "가상김가족", "role": "household_member", "organization": "대표 가족"}
    )
    normalized = interpret(raw)
    assert normalized["transactions"][0]["purpose"] == "private"
    assert normalized["transactions"][0]["business_related"] is False
    assert calculate(normalized)[0]["deductible_input_vat"] == 0


def test_family_owned_separate_worksite_requires_distinct_recipient_organization():
    raw = one_purchase()
    activity = raw["activities"][0]
    activity["operation_id"] = None
    activity["location"] = {
        "name": "대표 가족의 별도 자전거점",
        "kind": "worksite",
        "organization": "가상 가족자전거점",
    }
    activity["participants"].append(
        {
            "name": "가상김가족",
            "role": "household_member",
            "organization": "가상 가족자전거점",
        }
    )
    assert interpret(raw)["transactions"][0]["business_related"] is False
    activity["location"]["organization"] = raw["business_name"]
    with pytest.raises(ValueError, match="distinct recipient organization"):
        interpret(raw)


def test_duplicate_evidence_joins_one_activity_and_is_deducted_once():
    raw = one_purchase()
    duplicate = deepcopy(raw["transactions"][0])
    duplicate["document_id"] += "-CARD"
    duplicate.update(evidence="card_receipt", invoice_issued=False)
    raw["transactions"].append(duplicate)
    raw["activities"][0]["document_ids"].append(duplicate["document_id"])
    normalized = interpret(raw)
    assert calculate(normalized)[0]["input_vat"] == 600_000
    assert calculate(normalized)[0]["unique_transaction_count"] == 1


@pytest.mark.parametrize(
    "alter",
    [
        lambda raw: raw["transactions"][0].pop("activity_id"),
        lambda raw: raw["transactions"][0].update(activity_id="missing"),
        lambda raw: raw["transactions"][0].update(transaction_id="another-transaction"),
        lambda raw: raw["transactions"][0].update(document_id="another-document"),
        lambda raw: raw["transactions"][0].update(date="2026-03-01"),
        lambda raw: raw["activities"].append(deepcopy(raw["activities"][0])),
        lambda raw: raw["activities"][0]["document_ids"].append("missing-document"),
        lambda raw: raw["activities"][0].update(operation_id="missing-operation"),
        lambda raw: raw["activities"][0].update(purpose="hospitality"),
        lambda raw: raw["transactions"][0].update(business_related=True),
        lambda raw: raw["operations"][0].update(output_taxable="true"),
        lambda raw: raw["transactions"][0].update(vehicle_subject_excise=True),
        lambda raw: raw["activities"][0].update(action="meal"),
        lambda raw: raw["activities"][0]["participants"][0].update(role="customer"),
        lambda raw: raw["activities"][0]["participants"].append(
            {"name": "가상가족", "role": "household_member", "organization": "대표 가족"}
        ),
    ],
)
def test_ambiguous_or_conflicting_activity_facts_are_rejected(alter):
    raw = one_purchase()
    alter(raw)
    with pytest.raises(ValueError):
        interpret(raw)


def test_sales_only_need_no_fabricated_purchase_activity():
    raw = source()
    raw["transactions"] = raw["transactions"][:2]
    raw["activities"] = []
    raw["operations"] = []
    assert calculate(interpret(raw))[0]["tax_base"] == 20_000_000


def test_raw_derivation_trace_records_actual_joins_and_computed_fields():
    raw = source()
    normalized = interpret(raw)
    trace = derivation_trace(raw, normalized)
    assert trace["rule_id"] == "VAT_ACTIVITY_EVIDENCE"
    assert trace["inputs"]["activities"] == raw["activities"]
    assert not contains_derived(trace["inputs"])
    assert trace["output"][-1]["purpose"] == "hospitality"
