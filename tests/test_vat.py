"""Official numeric regressions are separated from formula-derived properties."""

from copy import deepcopy
import json
from pathlib import Path

from hypothesis import given, settings, strategies as st
import pytest

from rules.c_vat.engine import calculate
from scenarios.c_vat import generate

FIXTURE = json.loads((Path(__file__).parent / "fixtures/vat/official_examples.json").read_text())


def empty_scenario():
    scenario = generate(10, "easy")
    scenario["transactions"] = []
    return scenario


def row(base, direction="sale", evidence="tax_invoice", identifier="T1", includes_vat=False):
    item = deepcopy(generate(10, "easy")["transactions"][0])
    item.update(
        transaction_id=identifier,
        document_id=identifier + "-DOC",
        direction=direction,
        date="2026-03-01",
        amount=base * 11 // 10 if includes_vat else base,
        includes_vat=includes_vat,
        evidence=evidence,
        invoice_issued=evidence == "tax_invoice",
        counterparty_consumer=direction == "sale" and evidence != "tax_invoice",
    )
    return item


@pytest.mark.parametrize("entry", FIXTURE["table_entries"], ids=lambda item: item["id"])
def test_official_published_table_entries(entry):
    """17 genuine published supply/tax entries, not 17 invented worked cases."""
    scenario = empty_scenario()
    scenario["transactions"] = [row(entry["supply_base"], entry["direction"], entry["evidence"])]
    gold, _ = calculate(scenario)
    key = "output_vat" if entry["direction"] == "sale" else "deductible_input_vat"
    assert gold[key] == entry["vat"]


def test_official_retail_complete_worked_return():
    scenario = empty_scenario()
    # Original 70m invoice group contains 10m settled by card. Represent that
    # disclosed overlap as a separate shared transaction; no new monetary fact.
    rows = [
        row(60_000_000, identifier="I1"),
        row(10_000_000, identifier="OVERLAP"),
        row(20_000_000, identifier="I2"),
        row(10_000_000, evidence="card_receipt", identifier="CARD"),
        row(4_000_000, evidence="cash_receipt", identifier="CASHREC"),
        row(1_000_000, evidence="cash_ledger", identifier="CASH"),
    ]
    overlap = deepcopy(rows[1])
    overlap.update(evidence="card_receipt", document_id="OVERLAP-CARD")
    rows.append(overlap)
    rows.extend(
        row(base, "purchase", evidence, f"P{i}")
        for i, (base, evidence) in enumerate(
            [
                (50_000_000, "tax_invoice"),
                (10_000_000, "tax_invoice"),
                (15_000_000, "tax_invoice"),
                (1_000_000, "card_receipt"),
                (1_000_000, "card_receipt"),
            ]
        )
    )
    scenario.update(transactions=rows, prepaid_assessed_vat=1_500_000)
    gold, _ = calculate(scenario)
    expected = FIXTURE["worked_returns"][0]
    assert {key: gold[key] for key in expected if key in gold} == {
        key: value for key, value in expected.items() if key in gold
    }


def test_official_freight_complete_worked_return():
    scenario = empty_scenario()
    entries = [r for r in FIXTURE["table_entries"] if r["document"] == "freight"]
    scenario.update(
        transactions=[
            row(r["supply_base"], r["direction"], r["evidence"], r["id"]) for r in entries
        ],
        consumer_facing_business=False,
        prepaid_assessed_vat=1_200_000,
    )
    gold, _ = calculate(scenario)
    expected = FIXTURE["worked_returns"][1]
    assert {key: gold[key] for key in expected if key in gold} == {
        key: value for key, value in expected.items() if key in gold
    }


@pytest.mark.parametrize(
    "kind",
    [
        "hospitality",
        "private",
        "passenger_car_purchase",
        "passenger_car_rental",
        "passenger_car_maintenance",
    ],
)
def test_formula_derived_noncreditable_categories(kind):
    scenario = empty_scenario()
    purchase = row(2_000_000, "purchase", "card_receipt")
    purchase.update(
        purpose=kind,
        vehicle_subject_excise=kind.startswith("passenger_car"),
        business_related=kind != "private",
    )
    scenario["transactions"] = [purchase]
    gold, _ = calculate(scenario)
    assert gold["input_vat"] == gold["noncreditable_vat"] == 200_000
    assert gold["deductible_input_vat"] == 0


@pytest.mark.parametrize(
    "business_type,prior,consumer,expected",
    [
        ("individual", 1_000_000_000, True, 14_300),
        ("individual", 1_000_000_001, True, 0),
        ("corporation", 1, True, 0),
        ("individual", 1, False, 0),
    ],
)
def test_formula_derived_credit_eligibility_boundaries(business_type, prior, consumer, expected):
    scenario = empty_scenario()
    scenario.update(
        business_type=business_type,
        prior_year_site_supply_base=prior,
        consumer_facing_business=consumer,
        transactions=[row(1_000_000, evidence="card_receipt")],
    )
    assert calculate(scenario)[0]["receipt_credit"] == expected


def test_formula_derived_credit_annual_limit_and_nonrefundable_credit():
    scenario = empty_scenario()
    scenario["transactions"] = [row(800_000_000, evidence="cash_receipt")]
    assert calculate(scenario)[0]["receipt_credit"] == 10_000_000
    scenario["receipt_credit_previously_claimed"] = 9_000_000
    assert calculate(scenario)[0]["receipt_credit"] == 1_000_000
    scenario["transactions"] = [
        row(1_000_000, evidence="card_receipt"),
        row(2_000_000, "purchase", identifier="P1"),
    ]
    gold, _ = calculate(scenario)
    assert gold["receipt_credit"] == 0
    assert gold["refund_vat"] == 100_000


def test_formula_derived_period_filtering_and_duplicate_conflict():
    scenario = empty_scenario()
    scenario["transactions"] = [row(1_000_000)]
    scenario["transactions"][0]["date"] = "2025-12-31"
    assert calculate(scenario)[0]["tax_base"] == 0
    duplicate = deepcopy(scenario["transactions"][0])
    duplicate["amount"] += 10
    scenario["transactions"].append(duplicate)
    with pytest.raises(ValueError, match="conflicting duplicate"):
        calculate(scenario)


@settings(max_examples=70)
@given(
    seed=st.integers(min_value=0, max_value=2**31),
    difficulty=st.sampled_from(["easy", "medium", "hard"]),
)
def test_generation_reproducibility_and_exception_counts(seed, difficulty):
    first = generate(seed, difficulty)
    assert first == generate(seed, difficulty)
    count = len(first["exceptions"])
    assert (
        count == 0 if difficulty == "easy" else count == 1 if difficulty == "medium" else count >= 2
    )
    gold, trace = calculate(first)
    assert all(set(entry) == {"rule_id", "inputs", "output"} for entry in trace)
    assert (
        gold["output_vat"]
        - gold["deductible_input_vat"]
        - gold["receipt_credit"]
        - gold["prepaid_vat"]
        == gold["net_vat"]
    )


@settings(max_examples=70)
@given(
    seed=st.integers(min_value=0, max_value=100000), index=st.integers(min_value=0, max_value=14)
)
def test_duplicate_invariance(seed, index):
    scenario = generate(seed, "hard")
    gold, _ = calculate(scenario)
    duplicate = deepcopy(scenario["transactions"][index])
    duplicate["document_id"] += "-EXTRA-COPY"
    scenario["transactions"].append(duplicate)
    assert calculate(scenario)[0] == gold


@given(
    base=st.integers(min_value=1, max_value=100000).map(lambda n: n * 100_000),
    increment=st.integers(min_value=1, max_value=1000).map(lambda n: n * 100_000),
)
def test_sales_liability_monotonicity(base, increment):
    scenario = empty_scenario()
    scenario["transactions"] = [row(base, evidence="card_receipt")]
    before = calculate(scenario)[0]["net_vat"]
    scenario["transactions"][0]["amount"] += increment
    assert calculate(scenario)[0]["net_vat"] >= before


@given(base=st.integers(min_value=1, max_value=10000).map(lambda n: n * 100_000))
def test_reclassification_as_noncreditable_cannot_reduce_liability(base):
    scenario = empty_scenario()
    scenario["transactions"] = [row(1_000_000_000), row(base, "purchase", "card_receipt", "P1")]
    before = calculate(scenario)[0]["net_vat"]
    scenario["transactions"][1]["purpose"] = "hospitality"
    assert calculate(scenario)[0]["net_vat"] == before + base // 10
