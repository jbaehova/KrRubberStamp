"""Central documentary decisions change answers without input admission flags."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from KrRubberStamp.registry import calculate
from rules.a_yearend.evidence import interpret

ROOT = Path(__file__).resolve().parents[1]


def case(identity):
    number = int(identity[1:])
    name = "cases_004_053.json" if number <= 53 else "cases_054_103.json"
    rows = json.loads((ROOT / "authored/batch_1/A_yearend" / name).read_text())
    return deepcopy(next(row for row in rows if row["case_id"] == identity))


def answer(facts):
    return calculate("A_yearend", facts)[0]


def test_contract_address_and_registration_must_be_read_separately():
    raw = case("A019")["facts"]
    assert "address_matches" not in raw["rent"]
    assert answer(raw)["rent_credit"] == 0
    raw["rent"]["resident_registration_address"] = raw["rent"]["contract_address"]
    assert answer(raw)["rent_credit"] == 1_326_000
    raw["rent"]["resident_registration_address"] = raw["rent"]["contract_address"].replace(
        " ", "　"
    )
    assert answer(raw)["rent_credit"] == 1_326_000


def test_medical_organization_is_not_sufficient_without_treatment_purpose():
    raw = case("A075")["facts"]
    before = answer(raw)
    raw["medical"][1]["treatment_purpose"] = "therapeutic"
    after = answer(raw)
    assert after["medical_credit"] - before["medical_credit"] == 276_000
    assert before["final_national_tax"] - after["final_national_tax"] == 276_000


def test_management_fee_is_classified_from_billed_item():
    raw = case("A085")["facts"]
    before = answer(raw)["credit_card_deduction"]
    raw["cards"][2]["billed_item"] = "ordinary_goods_services"
    assert answer(raw)["credit_card_deduction"] > before


@pytest.mark.parametrize("identity,index", [("A053", 2), ("A101", 1), ("A102", 2)])
def test_attending_school_does_not_make_private_academy_fees_school_tuition(identity, index):
    raw = case(identity)["facts"]
    before = answer(raw)["education_credit"]
    raw["education"][index]["institution_type"] = "primary_secondary_school"
    assert answer(raw)["education_credit"] > before


def test_household_home_list_precedes_mortgage_interest_cap():
    raw = case("A099")["facts"]
    assert answer(raw)["housing_income_deduction"] == 0
    raw["housing_mortgage"]["household_homes_at_year_end"].pop()
    assert answer(raw)["housing_income_deduction"] == 8_600_000


def test_donation_date_joins_organization_designation_interval():
    raw = case("A031")["facts"]
    assert answer(raw)["donation_credit"] == 255_000
    raw["organization_designations"][1]["valid_to"] = "2025-12-31"
    assert answer(raw)["donation_credit"] == 600_000


@pytest.mark.parametrize(
    "identity,mutate,message",
    [
        ("A019", lambda s: s["rent"].update(address_matches=False), "compiled match"),
        ("A019", lambda s: s["rent"].pop("contract_address"), "both addresses"),
        ("A075", lambda s: s["medical"][1].update(excluded=True), "compiled exclusion"),
        ("A085", lambda s: s["cards"][2].update(billed_item="unknown"), "Unsupported raw"),
        ("A053", lambda s: s["education"][2].update(level="preschool"), "conflicting institution"),
        (
            "A099",
            lambda s: s["housing_mortgage"].update(requirements_met=False),
            "compiled mortgage",
        ),
        (
            "A099",
            lambda s: s["housing_mortgage"]["household_homes_at_year_end"].append(
                deepcopy(s["housing_mortgage"]["household_homes_at_year_end"][0])
            ),
            "Duplicate household",
        ),
        ("A031", lambda s: s["donations"][0].update(organization_id="missing"), "Unknown donation"),
        (
            "A031",
            lambda s: s["organization_designations"].append(
                deepcopy(s["organization_designations"][0])
            ),
            "Overlapping organization",
        ),
        (
            "A031",
            lambda s: s["donations"][0].update(eligible_organization=True),
            "compiled organization",
        ),
    ],
)
def test_ambiguous_or_precompiled_sources_are_rejected(identity, mutate, message):
    raw = case(identity)["facts"]
    mutate(raw)
    with pytest.raises(ValueError, match=message):
        interpret(raw)


def test_interpretation_does_not_write_admission_flags_back_into_source():
    raw = case("A099")["facts"]
    original = deepcopy(raw)
    _, trace = calculate("A_yearend", raw)
    assert raw == original
    assert trace[0]["output"] == {"housing_mortgage.requirements_met": False}


def test_raw_yearend_sources_survive_physical_document_roundtrip(tmp_path):
    from render.authored import render_authored
    from render.documents import restore_scenario

    row = case("A019")
    render_authored(row["facts"], tmp_path, row["domain"], row["documents"], seed=19)
    restored = restore_scenario(tmp_path)
    assert restored == row["facts"]
    assert answer(restored)["rent_credit"] == 0
