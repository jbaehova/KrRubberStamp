"""Official table regressions and separately labelled derived/property tests."""

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from hypothesis import given, settings, strategies as st
import openpyxl
import pytest
import yaml

from rules.b_payroll.engine import (
    calculate,
    floor_ten,
    health_employee,
    pension_employee,
    tax_table,
    withholding_tax,
)
from rules.b_payroll.extract_tax_table import extract
from scenarios.b_payroll import generate, INSTRUCTIONS, LABELS


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "payroll"
TAX_EXAMPLES = json.loads((FIXTURES / "official_tax_examples.json").read_text())
PENSION_EXAMPLES = json.loads((FIXTURES / "official_pension_examples.json").read_text())


@pytest.mark.parametrize("case", TAX_EXAMPLES)
def test_official_numeric_tax_example(case):
    result, _ = withholding_tax(
        case["taxable_pay"],
        case["family_count"],
        case["eligible_children"],
        case["payment_date"],
        case["withholding_percent"],
    )
    assert case["kind"] in ("official_table_cell", "official_worked_example")
    assert result == case["expected"]


@pytest.mark.parametrize("case", PENSION_EXAMPLES)
def test_official_numeric_pension_example(case):
    premium, _ = pension_employee(case["notified_income"], case["month"])
    assert case["kind"] == "official_worked_example"
    assert premium == case["expected_employee_premium"]


def test_all_7106_tax_cells_match_primary_pdf_and_independent_nts_spreadsheet():
    evidence = ROOT / "rules" / "b_payroll" / "evidence"
    pdf = evidence / "income_tax_table_2026.pdf"
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == tax_table()["source_sha256"]
    assert extract(pdf) == tax_table()
    book = openpyxl.load_workbook(evidence / "income_tax_table_2023.xlsx", data_only=True)
    spreadsheet_rows = []
    for row in book.worksheets[0].values:
        if isinstance(row[0], int) and isinstance(row[1], int) and row[0] < row[1]:
            spreadsheet_rows.append(
                [
                    row[0] * 1000,
                    row[1] * 1000,
                    *[row[i] for i in (2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20)],
                ]
            )
    assert len(spreadsheet_rows) == 646
    assert spreadsheet_rows == tax_table()["rows"]


def test_derived_table_interval_boundary_and_high_income_formula():
    assert withholding_tax(3519999)[0] == 127220
    assert withholding_tax(3520000)[0] > 127220
    assert withholding_tax(9999999)[0] == 1503990
    assert withholding_tax(10000000)[0] == 1507400
    assert withholding_tax(10000001)[0] == 1532400
    # Annex high-income calculation. These are derived, not official worked examples.
    for pay, addition in [
        (14000000, 1397000),
        (28000000, 6610600),
        (30000000, 7394600),
        (45000000, 13394600),
        (87000000, 31034600),
        (88000000, 31484600),
    ]:
        assert withholding_tax(pay)[0] == 1507400 + addition


def test_derived_month_specific_child_credit_boundary():
    assert withholding_tax(3500000, 4, 2, "2026-02-28")[0] == 20180
    assert withholding_tax(3500000, 4, 2, "2026-03-01")[0] == 3510
    assert withholding_tax(3500000, 4, 3, "2026-03-01")[0] == 0


def test_derived_small_tax_waiver_and_election_order():
    assert withholding_tax(1060000, 1, 0, "2026-10-25", 80)[0] == 0
    assert withholding_tax(1060000, 1, 0, "2026-10-25", 100)[0] == 1040
    assert withholding_tax(3500000, 4, 2, "2026-10-25", 120)[0] == 4210


@pytest.mark.parametrize(
    "month,low,high",
    [(1, 400000, 6370000), (6, 400000, 6370000), (7, 410000, 6590000), (12, 410000, 6590000)],
)
def test_derived_pension_half_year_caps_and_thousand_won_rounding(month, low, high):
    assert pension_employee(0, month)[1] == low
    assert pension_employee(high + 1, month)[1] == high
    assert pension_employee(2000999, month)[1] == 2000000
    assert pension_employee(high + 1000000, month)[0] == floor_ten(Fraction(high * 475, 10000))
    assert pension_employee(2000000, month, False)[0] == 0


def _hourly_case() -> dict:
    scenario = generate(11, "easy")
    scenario.update(
        {
            "pay_basis": "hourly",
            "base_salary": 0,
            "fixed_allowance": 0,
            "meal_allowance": 0,
            "variable_allowance": 0,
            "hourly_rate": 12000,
            "monthly_divisor_hours": 0,
            "weekly_holiday_included": False,
            "regular_minutes": 40 * 4 * 60,
            "weekly_hours": 40,
            "qualifying_weeks": 4,
            "overtime_minutes": 0,
            "night_minutes": 0,
            "holiday_shifts": [],
            "pension_notified_income": 2000000,
            "health_notified_income": 2000000,
            "employment_notified_income": 2000000,
        }
    )
    return scenario


def test_derived_premium_stacking_and_holiday_per_day_boundary():
    scenario = _hourly_case()
    scenario.update(
        {
            "overtime_minutes": 120,
            "night_minutes": 240,
            "holiday_shifts": [{"minutes": 600, "holiday_night_minutes": 120}],
        }
    )
    result, _ = calculate(scenario)
    assert result["overtime_pay"] == 36000
    assert result["night_pay"] == 24000
    assert result["holiday_pay"] == 192000  # 8h*1.5 + 2h*2, no extra holiday/overtime double count.
    scenario["holiday_shifts"] = [
        {"minutes": 300, "holiday_night_minutes": 120},
        {"minutes": 300, "holiday_night_minutes": 0},
    ]
    assert calculate(scenario)[0]["holiday_pay"] == 180000  # Each separate day is <=8h.


def test_derived_under_five_workers_do_not_receive_statutory_premiums():
    scenario = _hourly_case()
    scenario.update(
        {
            "workplace_employee_count": 4,
            "overtime_minutes": 120,
            "night_minutes": 120,
            "holiday_shifts": [{"minutes": 600, "holiday_night_minutes": 0}],
        }
    )
    result, _ = calculate(scenario)
    assert (result["overtime_pay"], result["night_pay"], result["holiday_pay"]) == (
        24000,
        0,
        120000,
    )
    assert result["weekly_holiday_pay"] == 384000


def test_derived_weekly_holiday_threshold_and_monthly_inclusion():
    scenario = _hourly_case()
    scenario["weekly_hours"] = 14
    assert calculate(scenario)[0]["weekly_holiday_pay"] == 0
    scenario["weekly_hours"] = 15
    assert calculate(scenario)[0]["weekly_holiday_pay"] == 144000
    scenario["weekly_hours"] = 20
    assert calculate(scenario)[0]["weekly_holiday_pay"] == 192000
    assert calculate(generate(2, "easy"))[0]["weekly_holiday_pay"] == 0


def test_derived_meal_allowance_ordinary_and_tax_rules_are_independent():
    scenario = generate(13, "easy")
    result, _ = calculate(scenario)
    scenario["employer_provides_meals"] = True
    with_food, _ = calculate(scenario)
    assert result["ordinary_monthly_wage"] == with_food["ordinary_monthly_wage"]
    assert result["non_taxable_pay"] == scenario["meal_allowance"]
    assert with_food["non_taxable_pay"] == 0
    assert with_food["taxable_pay"] == result["taxable_pay"] + scenario["meal_allowance"]


def test_derived_health_bounds_and_long_term_care_exact_ratio():
    assert health_employee(0) == 10080
    assert health_employee(3000000) == 107850
    assert health_employee(10**10) == 4591740
    assert health_employee(3000000, False) == 0
    scenario = generate(8, "easy")
    scenario["health_notified_income"] = 1026800
    result, _ = calculate(scenario)
    assert result["health_insurance"] == 36910
    # Exact ratio yields 4,850; the rounded 13.14% ratio would incorrectly yield 4,840.
    assert result["long_term_care"] == floor_ten(Fraction(36910 * 9448, 71900))
    assert result["long_term_care"] != floor_ten(Fraction(36910 * 1314, 10000))


def test_derived_fractional_hourly_wage_not_truncated_before_allowance_calculation():
    scenario = generate(1, "easy")
    scenario.update(
        {
            "base_salary": 2500001,
            "fixed_allowance": 0,
            "meal_allowance": 0,
            "overtime_minutes": 60,
            "night_minutes": 0,
        }
    )
    result, _ = calculate(scenario)
    exact = Fraction(2500001, 209) * Fraction(3, 2)
    assert result["overtime_pay"] == -(-exact.numerator // exact.denominator)
    assert result["overtime_pay"] > int(Fraction(2500001, 209)) * Fraction(3, 2)


def test_trace_rule_ids_all_have_complete_source_records():
    records = yaml.safe_load((ROOT / "rules" / "b_payroll" / "sources.yaml").read_text())
    ids = {record["rule_id"] for record in records}
    for record in records:
        assert {"rule_id", "description", "source", "effective_period", "verified"} <= record.keys()
        assert type(record["verified"]) is bool
    for difficulty in ("easy", "medium", "hard"):
        _, trace = calculate(generate(321, difficulty))
        assert {record["rule_id"] for record in trace} <= ids
        assert all({"rule_id", "inputs", "output"} <= record.keys() for record in trace)
        json.dumps(trace)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_generation_determinism_variation_labels_and_exception_count(difficulty):
    assert len(INSTRUCTIONS) >= 15
    observed = set()
    for seed in range(100):
        scenario = generate(seed, difficulty)
        assert scenario == generate(seed, difficulty)
        observed.add(json.dumps(scenario, sort_keys=True))
        assert all(key in LABELS for key in scenario)
        assert len(scenario["exceptions"]) == {"easy": 0, "medium": 1}.get(
            difficulty, len(scenario["exceptions"])
        )
        if difficulty == "hard":
            assert len(scenario["exceptions"]) >= 2
        assert scenario["employee_name"].startswith("가상")
        assert scenario["company_name"].startswith("가상")
        result, trace = calculate(scenario)
        assert all(type(value) is int and value >= 0 for value in result.values())
        assert result["gross_pay"] - result["total_deductions"] == result["net_pay"]
        assert json.dumps(result, sort_keys=True) == json.dumps(
            calculate(deepcopy(scenario))[0], sort_keys=True
        )
        assert len(trace) == 16
    assert len(observed) == 100


def test_visible_table_excerpt_covers_taxable_pay_with_neighbors_or_formula():
    table = tax_table()
    for difficulty in ("easy", "medium", "hard"):
        for seed in range(150):
            scenario = generate(seed, difficulty)
            pay = calculate(scenario)[0]["taxable_pay"]
            reference = scenario["withholding_reference"]
            if pay >= 10000000:
                assert len(reference["high_income_formulas"]) == 6
                assert len(reference["tax_at_ten_million"]) == 11
            else:
                assert any(
                    r["wage_from_won"] <= pay < r["wage_below_won"] for r in reference["table_rows"]
                )
            for row in reference["table_rows"]:
                official = next(r for r in table["rows"] if r[0] == row["wage_from_won"])
                assert [row[f"family_tax_{i}"] for i in range(1, 12)] == official[2:]


@given(st.integers(0, 100000000), st.integers(1, 12))
def test_property_pension_monotone_and_caps(base, month):
    amount, bounded = pension_employee(base, month)
    higher, _ = pension_employee(base + 1000, month)
    assert 0 <= amount <= higher <= 313020
    assert 400000 <= bounded <= 6590000
    assert amount % 10 == 0


@given(st.integers(0, 1000000000))
def test_property_health_monotone_and_caps(base):
    assert 10080 <= health_employee(base) <= health_employee(base + 1000) <= 4591740


@given(st.integers(0, 100000000), st.integers(1, 10))
def test_property_more_family_does_not_increase_withholding(pay, families):
    assert withholding_tax(pay, families + 1)[0] <= withholding_tax(pay, families)[0]


@given(st.integers(0, 100000000), st.integers(0, 7))
def test_property_more_eligible_children_does_not_increase_withholding(pay, children):
    assert withholding_tax(pay, 10, children + 1)[0] <= withholding_tax(pay, 10, children)[0]


@settings(max_examples=150)
@given(st.integers(0, 2**32), st.sampled_from(["easy", "medium", "hard"]))
def test_property_generated_payroll_nonnegative_and_conservation(seed, difficulty):
    scenario = generate(seed, difficulty)
    result, _ = calculate(scenario)
    assert all(type(value) is int and value >= 0 for value in result.values())
    assert result["net_pay"] + result["total_deductions"] == result["gross_pay"]
    assert result["taxable_pay"] + result["non_taxable_pay"] == result["gross_pay"]


def test_invalid_inputs_rejected_instead_of_silent_estimates():
    with pytest.raises(ValueError):
        withholding_tax(3000000, 0)
    with pytest.raises(ValueError):
        withholding_tax(3000000, 2, 2)
    with pytest.raises(ValueError):
        withholding_tax(3000000, 1, 0, "2025-10-25")
    with pytest.raises(ValueError):
        pension_employee(-1, 1)
    scenario = _hourly_case()
    scenario["holiday_shifts"] = [{"minutes": 60, "holiday_night_minutes": 120}]
    with pytest.raises(ValueError):
        calculate(scenario)
