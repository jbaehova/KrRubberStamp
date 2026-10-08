"""Registered identities and effective dates must drive requested VAT answers."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from KrRubberStamp.registry import calculate
from render.authored import render_authored
from render.documents import restore_scenario
from rules.c_vat.evidence import interpret

ROOT = Path(__file__).resolve().parents[1]


def case(identity):
    name = "cases_004_053.json" if int(identity[1:]) <= 53 else "cases_054_103.json"
    return deepcopy(
        next(
            c
            for c in json.loads((ROOT / "authored/batch_1/C_vat" / name).read_text())
            if c["case_id"] == identity
        )
    )


def answer(raw):
    return calculate("C_vat", raw)[0]


def test_same_invoice_vehicle_lines_join_different_registration_ids():
    raw = case("C027")["facts"]
    assert answer(raw)["deductible_input_vat"] == 200_000
    raw["vehicle_registry"][1]["registration_class"] = "excise_passenger"
    assert answer(raw)["deductible_input_vat"] == 0


def test_same_repair_card_and_invoice_count_once_despite_different_display_amounts():
    raw = case("C028")["facts"]
    gold = answer(raw)
    assert gold["unique_transaction_count"] == 2
    assert gold["input_vat"] == 75_000
    raw["transactions"] = raw["transactions"][:2]
    raw["activities"][0]["document_ids"] = [raw["transactions"][1]["document_id"]]
    assert answer(raw) == gold


def test_site_code_selects_amount_and_exact_billion_boundary():
    raw = case("C050")["facts"]
    assert answer(raw)["receipt_credit"] == 257_400
    raw["site_year_records"][1]["supply_base"] += 1
    gold = answer(raw)
    assert gold["receipt_credit"] == 0
    assert gold["refund_vat"] == 100_000


def test_license_links_actual_operation_and_vehicle():
    raw = case("C075")["facts"]
    assert answer(raw)["payable_vat"] == 607_300
    raw["vehicle_registry"][0].update(business_license="none", permitted_operation_id=None)
    assert answer(raw)["payable_vat"] == 771_300


@pytest.mark.parametrize("identity,delta", [("C083", 50_000), ("C096", 100_000)])
def test_supplier_effective_period_changes_card_input_credit(identity, delta):
    raw = case(identity)["facts"]
    before = answer(raw)["deductible_input_vat"]
    raw["supplier_status_records"][0]["status"] = "general"
    assert answer(raw)["deductible_input_vat"] - before == delta


def test_vehicle_transition_is_not_applied_retroactively():
    raw = case("C099")["facts"]
    normalized = interpret(raw)
    assert normalized["transactions"][1]["vehicle_direct_business"] is False
    assert normalized["transactions"][2]["vehicle_direct_business"] is True
    assert answer(raw)["payable_vat"] == 278_400
    raw["vehicle_registry"][1].update(business_license="none", permitted_operation_id=None)
    assert answer(raw)["payable_vat"] == 328_400


@pytest.mark.parametrize(
    "identity,mutate,message",
    [
        ("C027", lambda s: s["transactions"][1].update(vehicle_subject_excise=True), "preselected"),
        ("C027", lambda s: s["activities"][0].update(vehicle_id="missing"), "conflicting vehicle"),
        (
            "C027",
            lambda s: s["vehicle_registry"].append(deepcopy(s["vehicle_registry"][0])),
            "Overlapping vehicle",
        ),
        (
            "C075",
            lambda s: s["vehicle_registry"][0].update(permitted_operation_id="missing"),
            "unknown permitted",
        ),
        (
            "C099",
            lambda s: s["vehicle_registry"][0].update(valid_to="2026-05-01"),
            "Overlapping vehicle",
        ),
        (
            "C099",
            lambda s: s["vehicle_registry"][1].update(valid_from="2026-05-20"),
            "cover purchase date",
        ),
        ("C099", lambda s: s["vehicle_registry"][0].pop("valid_from"), "both validity"),
        (
            "C083",
            lambda s: s["transactions"][0].update(supplier_general=False),
            "preselected status",
        ),
        ("C083", lambda s: s["transactions"][0].update(supplier_id="missing"), "Unknown supplier"),
        (
            "C083",
            lambda s: s["supplier_status_records"][0].update(valid_to="2026-05-01"),
            "Overlapping supplier",
        ),
        (
            "C096",
            lambda s: s["supplier_status_records"][1].update(valid_from="2026-04-18"),
            "cover purchase date",
        ),
        ("C050", lambda s: s.update(prior_year_site_supply_base=1), "preselected prior"),
        ("C050", lambda s: s.update(filing_site_id="missing"), "conflicting filing"),
        (
            "C050",
            lambda s: s["site_year_records"].append(deepcopy(s["site_year_records"][0])),
            "Duplicate site",
        ),
    ],
)
def test_ambiguous_links_and_preselected_facts_are_rejected(identity, mutate, message):
    raw = case(identity)["facts"]
    mutate(raw)
    with pytest.raises(ValueError, match=message):
        interpret(raw)


def test_raw_vehicle_history_survives_physical_documents_without_source_mutation(tmp_path):
    c = case("C099")
    original = deepcopy(c["facts"])
    render_authored(c["facts"], tmp_path, "C_vat", c["documents"], seed=99)
    restored = restore_scenario(tmp_path)
    assert restored == original
    assert answer(restored) == answer(original)
    assert c["facts"] == original
    _, trace = calculate("C_vat", original)
    assert trace[0]["inputs"]["vehicle_registry"] == original["vehicle_registry"]


@pytest.mark.parametrize("amount", [600, 499_000, 500_001])
def test_invalid_assessment_minimum_or_rounding_is_rejected(amount):
    raw = case("C050")["facts"]
    raw["prepaid_assessed_vat"] = amount
    with pytest.raises(ValueError, match="at least 500000"):
        answer(raw)


def test_prior_return_payment_is_not_deducted_from_additional_transactions_again():
    raw = case("C086")["facts"]
    assert raw["prepaid_assessed_vat"] == 0
    assert raw["prior_declared_vat_paid"] == 600
    assert answer(raw)["net_vat"] == 500
    raw["prior_declared_vat_paid"] = 1_500_000
    assert answer(raw)["net_vat"] == 500


def test_prior_return_and_still_valid_notice_cannot_be_claimed_together():
    raw = case("C086")["facts"]
    raw["prepaid_assessed_vat"] = 500_000
    with pytest.raises(ValueError, match="cannot both"):
        answer(raw)
