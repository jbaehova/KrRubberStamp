"""Official worked/table examples are separate from independently derived tests."""

from copy import deepcopy
import json
from pathlib import Path

from hypothesis import given, settings, strategies as st
import pytest
import yaml

from rules.a_yearend import engine
from scenarios.a_yearend import generate

FIXTURES = json.loads(
    (Path(__file__).parent / "fixtures/yearend/official_numeric_examples.json").read_text()
)


@pytest.mark.parametrize("case", FIXTURES, ids=[case["id"] for case in FIXTURES])
def test_official_numeric_examples(case):
    assert getattr(engine, case["function"])(*case["args"]) == case["expected"]


def test_official_2025_comprehensive_receipt():
    fixture = json.loads(
        (Path(__file__).parent / "fixtures/yearend/official_comprehensive_2025.json").read_text()
    )
    gold, _ = engine.calculate(fixture["scenario"])
    for field, expected in fixture["expected_published_fields"].items():
        assert gold[field] == expected, field
    assert gold["donation_credit"] + gold["political_credit"] + gold["hometown_credit"] == 271_818
    assert gold["settlement_national_tax"] == -759_768


def test_official_disabled_23_year_old_personal_example():
    # 2025 NTS book p99 explicitly gives 1.5m basic plus 2m disability for the child.
    s = minimal()
    s["marital_status"] = "married"
    s["dependents"] = [family(age=23, disabled=True)]
    gold, _ = engine.calculate(s)
    assert gold["basic_deduction"] - 1_500_000 == 1_500_000
    assert gold["additional_deduction"] == 2_000_000
    # p164 requires basic-eligible children age8+, without an additional20-year ceiling.
    assert gold["child_credit"] == 250_000


def test_housing_mortgage_caps_and_aggregate_deduction_limit():
    s = minimal()
    s["housing_mortgage"] = {
        "borrowed_date": "2015-03-01",
        "term_years": 20,
        "fixed_rate": True,
        "non_deferred": True,
        "requirements_met": True,
        "interest_paid": 30_000_000,
    }
    assert engine.calculate(s)[0]["housing_income_deduction"] == 20_000_000
    s["housing_mortgage"]["non_deferred"] = False
    assert engine.calculate(s)[0]["housing_income_deduction"] == 18_000_000


def minimal():
    s = generate(1, "easy")
    s.update(
        {
            "annual_gross": 60_000_000,
            "non_taxable": 0,
            "employee_age": 40,
            "employee_sex": "male",
            "marital_status": "single",
            "dependents": [],
            "public_pension_paid": 0,
            "social_insurance": {},
            "pension_accounts": {},
            "cards": [],
            "insurance": [],
            "medical": [],
            "education": [],
            "donations": [],
            "rent": {},
            "paid_national_tax": 0,
            "paid_local_tax": 0,
        }
    )
    return s


def family(person_id="F1", relation="child", age=12, **kwargs):
    return {
        "person_id": person_id,
        "relation": relation,
        "age": age,
        "income_amount": 0,
        "earned_income_only": False,
        "gross_salary": 0,
        "supported": True,
        "assigned_claimant": "self",
        "disabled": False,
        **kwargs,
    }


def expense(amount, **kwargs):
    return {
        "amount": amount,
        "date": "2025-11-01",
        "person_id": "self",
        "paid_by_self": True,
        **kwargs,
    }


@pytest.mark.parametrize("difficulty,n", [("easy", 0), ("medium", 1), ("hard", 2)])
def test_generator_deterministic_and_trace_sources(difficulty, n):
    source_path = Path(__file__).parent.parent / "rules/a_yearend/sources.yaml"
    source_ids = {row["rule_id"] for row in yaml.safe_load(source_path.read_text())}
    for seed in range(100):
        s = generate(seed, difficulty)
        assert s == generate(seed, difficulty)
        assert len(s["exceptions"]) == n
        assert "gold" not in s and "trace" not in s
        gold, trace = engine.calculate(s)
        assert all(type(value) is int for value in gold.values())
        assert all(row["rule_id"] in source_ids for row in trace)
        assert all("inputs" in row and "output" in row for row in trace)
        assert engine.calculate(json.loads(json.dumps(s, ensure_ascii=False)))[0] == gold


@pytest.mark.parametrize(
    "age,relation,eligible",
    [
        (20, "child", True),
        (21, "child", False),
        (59, "parent", False),
        (60, "parent", True),
        (59, "spouse", True),
    ],
)
def test_basic_age_boundaries(age, relation, eligible):
    assert engine.basic_eligible(family(relation=relation, age=age)) is eligible


def test_income_boundary_and_disabled_age_exception():
    assert engine.basic_eligible(family(income_amount=1_000_000))
    assert not engine.basic_eligible(family(income_amount=1_000_001))
    assert engine.basic_eligible(family(age=30, disabled=True))
    assert engine.basic_eligible(
        family(income_amount=1_500_000, earned_income_only=True, gross_salary=5_000_000)
    )
    assert not engine.basic_eligible(
        family(income_amount=1_500_000, earned_income_only=True, gross_salary=5_000_001)
    )


def test_duplicate_spouse_claim_rejects_child_and_related_expenses():
    s = minimal()
    s["dependents"] = [family(assigned_claimant="spouse")]
    s["medical"] = [expense(5_000_000, person_id="F1", kind="ordinary")]
    s["education"] = [expense(3_000_000, person_id="F1", level="school")]
    s["cards"] = [expense(30_000_000, person_id="F1", category="debit", payment_method="debit")]
    gold, _ = engine.calculate(s)
    assert gold["eligible_dependents"] == 0
    assert gold["child_credit"] == gold["medical_credit"] == gold["education_credit"] == 0
    assert gold["credit_card_deduction"] == 0


def test_medical_ignores_income_and_age_tests_but_insurance_does_not():
    s = minimal()
    s["dependents"] = [family(age=25, income_amount=2_000_000)]
    s["medical"] = [expense(3_000_000, person_id="F1", kind="ordinary")]
    s["insurance"] = [expense(1_000_000, person_id="F1", kind="general")]
    gold, _ = engine.calculate(s)
    assert gold["basic_deduction"] == 1_500_000
    assert gold["medical_credit"] == 180_000
    assert gold["insurance_credit"] == 0


@given(
    st.integers(min_value=20_000_000, max_value=180_000_000),
    st.integers(min_value=0, max_value=20_000_000),
    st.integers(min_value=0, max_value=5_000_000),
)
@settings(max_examples=100)
def test_medical_spending_never_increases_final_tax(salary, amount, extra):
    s = minimal()
    s["annual_gross"] = salary
    s["medical"] = [expense(amount, kind="ordinary")]
    before = engine.calculate(s)[0]
    s["medical"][0]["amount"] += extra
    after = engine.calculate(s)[0]
    assert after["medical_credit"] >= before["medical_credit"]
    assert after["final_national_tax"] <= before["final_national_tax"]


@given(
    st.integers(min_value=0, max_value=250_000_000), st.integers(min_value=0, max_value=1_000_000)
)
def test_salary_income_monotonic(salary, extra):
    assert salary - engine.salary_deduction(salary) <= salary + extra - engine.salary_deduction(
        salary + extra
    )


def test_medical_ordinary_cap_and_reimbursement():
    s = minimal()
    s["dependents"] = [family()]
    s["medical"] = [expense(20_000_000, person_id="F1", kind="ordinary", reimbursed=0)]
    assert engine.calculate(s)[0]["medical_credit"] == 1_050_000
    s["medical"][0]["reimbursed"] = 19_000_000
    assert engine.calculate(s)[0]["medical_credit"] == 0


def test_medical_special_rates_after_threshold():
    s = minimal()
    s["medical"] = [
        expense(1_800_000, kind="ordinary"),
        expense(2_000_000, kind="premature"),
        expense(1_000_000, kind="infertility"),
    ]
    assert engine.calculate(s)[0]["medical_credit"] == 700_000


def test_pension_caps_and_salary_rate_boundary():
    s = minimal()
    s["annual_gross"] = 55_000_000
    s["pension_accounts"] = {"pension_savings": 8_000_000, "irp": 4_000_000}
    assert engine.calculate(s)[0]["pension_account_credit"] == 1_350_000
    s["annual_gross"] += 1
    assert engine.calculate(s)[0]["pension_account_credit"] == 1_080_000


def test_card_threshold_order_and_caps():
    assert engine.credit_card_deduction(40_000_000, {"credit": 10_000_000}) == 0
    assert (
        engine.credit_card_deduction(40_000_000, {"credit": 10_000_000, "debit": 1_000_000})
        == 300_000
    )
    assert (
        engine.credit_card_deduction(40_000_000, {"credit": 5_000_000, "debit": 6_000_000})
        == 300_000
    )
    assert engine.credit_card_deduction(40_000_000, {"credit": 100_000_000}) == 3_000_000
    assert (
        engine.credit_card_deduction(40_000_000, {"credit": 100_000_000, "market": 10_000_000})
        == 6_000_000
    )
    assert (
        engine.credit_card_deduction(80_000_000, {"credit": 100_000_000, "market": 10_000_000})
        == 4_500_000
    )


def test_culture_above_salary_limit_uses_original_payment_method():
    s = minimal()
    s["annual_gross"] = 80_000_000
    s["cards"] = [expense(25_000_000, category="culture", payment_method="credit")]
    assert engine.calculate(s)[0]["credit_card_deduction"] == 750_000


def test_school_cap_is_per_person_and_scholarship_is_removed():
    s = minimal()
    s["dependents"] = [family("C1"), family("C2")]
    s["education"] = [
        expense(5_000_000, person_id="C1", level="school", scholarship=500_000),
        expense(2_000_000, person_id="C2", level="school", scholarship=500_000),
    ]
    assert engine.calculate(s)[0]["education_credit"] == 675_000


def test_rent_salary_boundary_housing_and_cap():
    s = minimal()
    s["annual_gross"] = 55_000_000
    s["rent"] = {
        "homeless_household": True,
        "household_head": True,
        "address_matches": True,
        "eligible_contract_holder": True,
        "area_sqm": 85,
        "standard_value": 500_000_000,
        "payments": [expense(12_000_000)],
    }
    assert engine.calculate(s)[0]["rent_credit"] == 1_700_000
    s["annual_gross"] = 80_000_000
    assert engine.calculate(s)[0]["rent_credit"] == 1_500_000
    s["annual_gross"] += 1
    assert engine.calculate(s)[0]["rent_credit"] == 0


def test_donation_bracket_and_public_income_cap():
    s = minimal()
    s["donations"] = [expense(12_000_000, kind="statutory", eligible_organization=True)]
    assert engine.calculate(s)[0]["donation_credit"] == 2_100_000
    s["donations"][0].update(kind="public", amount=50_000_000)
    # Earned income 47.25 million, public-donation limit 30% = 14.175 million.
    assert engine.calculate(s)[0]["donation_credit"] == 2_752_500


def test_pre_employment_special_costs_excluded_donation_retained():
    s = minimal()
    s["employment_start"] = "2025-07-01"
    s["medical"] = [expense(5_000_000, kind="ordinary", date="2025-01-01")]
    s["donations"] = [expense(1_000_000, kind="public", date="2025-01-01")]
    gold, _ = engine.calculate(s)
    assert gold["medical_credit"] == 0
    assert gold["donation_credit"] == 150_000


def test_receipt_settlement_sign_and_exact_won():
    s = minimal()
    s["paid_national_tax"] = 100_000_000
    s["paid_local_tax"] = 10_000_000
    gold, _ = engine.calculate(s)
    assert gold["settlement_national_tax"] < 0
    assert gold["settlement_local_tax"] < 0
    assert gold["settlement_national_tax"] == gold["final_national_tax"] - s["paid_national_tax"]
    assert gold["settlement_local_tax"] == gold["final_local_tax"] - s["paid_local_tax"]
    assert (
        gold["settlement_total"] == gold["settlement_national_tax"] + gold["settlement_local_tax"]
    )


def test_standard_choice_removes_special_deductions_and_credits():
    s = minimal()
    s["deduction_choice"] = "standard"
    s["social_insurance"] = {"health": 3_000_000}
    s["insurance"] = [expense(1_000_000, kind="general")]
    gold, _ = engine.calculate(s)
    assert gold["special_income_deduction"] == gold["insurance_credit"] == 0
    assert gold["standard_credit"] == 130_000


def test_engine_does_not_mutate_evidence():
    scenario = generate(92, "hard")
    original = deepcopy(scenario)
    engine.calculate(scenario)
    assert original == scenario
