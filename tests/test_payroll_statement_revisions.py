"""Strict original validation and independently hand-worked full monthly revisions."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from rules.b_payroll import bank_reconciliation
from rules.b_payroll.statement_revisions import RULE_ID, calculate

EXPECTED = {
    "absence_correction": {
        "payroll_calculations": [
            {
                "payroll_id": "EX-ABSENCE-NOV",
                "employee_id": "EX-ABSENCE-101",
                "calculation": {
                    "effective_payment_date": "2026-11-25",
                    "ordinary_monthly_wage": 0,
                    "ordinary_hourly_wage_floor": 12500,
                    "base_pay": 250000,
                    "fixed_allowance": 0,
                    "meal_allowance": 0,
                    "variable_allowance": 0,
                    "overtime_pay": 0,
                    "night_pay": 0,
                    "holiday_pay": 0,
                    "weekly_holiday_pay": 50000,
                    "paid_holiday_pay": 0,
                    "gross_pay": 300000,
                    "taxable_pay": 300000,
                    "non_taxable_pay": 0,
                    "pension_base_income": 410000,
                    "national_pension": 0,
                    "health_insurance": 0,
                    "long_term_care": 0,
                    "employment_insurance": 2700,
                    "income_tax": 0,
                    "local_income_tax": 0,
                    "total_deductions": 2700,
                    "net_pay": 297300,
                },
            }
        ],
        "employee_settlements": [
            {
                "payroll_id": "EX-ABSENCE-NOV",
                "employee_id": "EX-ABSENCE-101",
                "effective_payment_date": "2026-11-25",
                "insurance_assessment_month": "2026-11",
                "gross_pay": 300000,
                "total_deductions": 2700,
                "net_pay": 297300,
                "paid": 290000,
                "balance": 7300,
            }
        ],
        "gross_total": 300000,
        "deductions_total": 2700,
        "net_total": 297300,
        "paid_total": 290000,
        "balance_total": 7300,
    },
    "ordinary_and_clock_revision": {
        "payroll_calculations": [
            {
                "payroll_id": "EX-CLOCK-NOV",
                "employee_id": "EX-CLOCK-202",
                "calculation": {
                    "effective_payment_date": "2026-11-25",
                    "ordinary_monthly_wage": 2612500,
                    "ordinary_hourly_wage_floor": 12500,
                    "base_pay": 2508000,
                    "fixed_allowance": 104500,
                    "meal_allowance": 0,
                    "variable_allowance": 0,
                    "overtime_pay": 37500,
                    "night_pay": 6250,
                    "holiday_pay": 0,
                    "weekly_holiday_pay": 0,
                    "paid_holiday_pay": 0,
                    "gross_pay": 2656250,
                    "taxable_pay": 2656250,
                    "non_taxable_pay": 0,
                    "pension_base_income": 2500000,
                    "national_pension": 118750,
                    "health_insurance": 89870,
                    "long_term_care": 11800,
                    "employment_insurance": 22500,
                    "income_tax": 43970,
                    "local_income_tax": 4390,
                    "total_deductions": 291280,
                    "net_pay": 2364970,
                },
            }
        ],
        "employee_settlements": [
            {
                "payroll_id": "EX-CLOCK-NOV",
                "employee_id": "EX-CLOCK-202",
                "effective_payment_date": "2026-11-25",
                "insurance_assessment_month": "2026-11",
                "gross_pay": 2656250,
                "total_deductions": 291280,
                "net_pay": 2364970,
                "paid": 2400000,
                "balance": -35030,
            }
        ],
        "gross_total": 2656250,
        "deductions_total": 291280,
        "net_total": 2364970,
        "paid_total": 2400000,
        "balance_total": -35030,
    },
}

FIXTURE = Path(__file__).parent / "fixtures/payroll_statement_revisions.json"


def source(name="absence_correction"):
    return json.loads(FIXTURE.read_text())[name]


def current(facts):
    return facts["statement_records"][1]["facts"]


def old(facts):
    return facts["statement_records"][0]["facts"]


@pytest.mark.parametrize(
    "name,expected",
    [
        ("absence_correction", [300000, 2700, 297300, 290000, 7300]),
        ("ordinary_and_clock_revision", [2656250, 291280, 2364970, 2400000, -35030]),
    ],
)
def test_handworked_all_answer_fields_and_unchanged_child_trace(name, expected):
    facts = source(name)
    answer, trace = calculate(facts)
    selected = facts["statement_records"][1]
    child_source = {
        "source_contract": bank_reconciliation.CONTRACT,
        "processing_policy": facts["processing_policy"],
        "as_of_date": facts["as_of_date"],
        "payrolls": [
            {key: deepcopy(selected[key]) for key in ("payroll_id", "employee_id", "facts")}
        ],
        "transfers": deepcopy(facts["transfers"]),
    }
    full_expected = EXPECTED[name]
    assert json.dumps(answer) == json.dumps(full_expected)
    assert [
        answer[key]
        for key in ("gross_total", "deductions_total", "net_total", "paid_total", "balance_total")
    ] == expected
    _, unchanged_child_trace = bank_reconciliation.calculate(child_source)
    assert json.dumps(trace[1:]) == json.dumps(unchanged_child_trace)
    assert trace[0]["rule_id"] == RULE_ID
    assert trace[0]["output"]["selected_document_ids"] == [selected["document_id"]]


def test_source_order_invariance_and_exact_typed_copy_deduplication():
    facts = source("ordinary_and_clock_revision")
    baseline = calculate(facts)
    facts["statement_records"].reverse()
    facts["transfers"].reverse()
    assert calculate(facts) == baseline
    facts["statement_records"].append(deepcopy(facts["statement_records"][0]))
    facts["transfers"].append(deepcopy(facts["transfers"][0]))
    answer, trace = calculate(facts)
    assert answer == baseline[0]
    assert trace[0]["output"]["deduplicated_document_ids"] == ["EX-CLOCK-DRAFT3"]
    assert trace[1]["output"]["deduplicated_transfer_ids"] == ["EX-CLOCK-EXEC"]


@pytest.mark.parametrize("status", ["draft", "superseded"])
def test_highest_nonapproved_revision_does_not_replace_lower_approved(status):
    facts = source("ordinary_and_clock_revision")
    facts["statement_records"][-1]["status"] = status
    answer, trace = calculate(facts)
    assert answer["net_total"] == 2364970
    assert trace[0]["output"]["selected_document_ids"] == ["EX-CLOCK-REV2"]


def test_draft_only_other_group_is_validated_but_not_selected_and_cannot_receive_cash():
    facts = source()
    draft = deepcopy(facts["statement_records"][0])
    draft.update(
        document_id="OTHER", employee_id="OTHER-EMP", payroll_id="OTHER-PAY", status="draft"
    )
    facts["statement_records"].append(draft)
    assert calculate(facts)[0]["net_total"] == 297300
    transfer = deepcopy(facts["transfers"][0])
    transfer.update(
        transfer_id="OTHER-CASH", payroll_id="OTHER-PAY", employee_id="OTHER-EMP", status="planned"
    )
    facts["transfers"].append(transfer)
    with pytest.raises(ValueError, match="references"):
        calculate(facts)


def test_same_employee_distinct_months_have_separate_stable_payrolls():
    facts = source()
    other = deepcopy(facts["statement_records"][1])
    other.update(document_id="DEC", payroll_id="DEC", revision=1)
    other["facts"]["insurance_assessment_month"] = "2026-12"
    facts["statement_records"].append(other)
    assert calculate(facts)[0]["net_total"] == 594600


def test_private_processing_date_is_not_cash_cutoff():
    facts = source()
    facts["as_of_date"] = "2026-11-24"
    answer, _ = calculate(facts)
    assert answer["net_total"] == 297300 and answer["paid_total"] == 0


@pytest.mark.parametrize("change", ["identity", "month", "same_revision", "chronology", "future"])
def test_reference_number_and_issuance_rejections(change):
    facts = source()
    row = facts["statement_records"][1]
    if change == "identity":
        row["payroll_id"] = "DIFFERENT"
    elif change == "month":
        row["facts"]["insurance_assessment_month"] = "2026-12"
    elif change == "same_revision":
        row["revision"] = 1
    elif change == "chronology":
        row["issued_on"] = "2026-11-20"
    else:
        row["issued_on"] = "2026-11-27"
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize(
    "key,value",
    [
        ("revision", True),
        ("revision", 0),
        ("status", "cancelled"),
        ("statement_scope", "partial"),
        ("issued_on", "20261126"),
        ("employee_id", " "),
        ("document_id", None),
    ],
)
def test_statement_shape_and_types(key, value):
    facts = source()
    facts["statement_records"][0][key] = value
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize(
    "key,value",
    [
        ("base_salary", True),
        ("fixed_allowance", 1.0),
        ("meal_allowance", -1),
        ("hourly_rate", float("nan")),
        ("hourly_rate", float("inf")),
        ("hourly_rate", False),
        ("monthly_divisor_hours", 0),
        ("weekly_hours", 41),
        ("weekly_hours", 20.0),
        ("family_count", 0),
        ("eligible_children", 1),
        ("withholding_percent", 100.0),
        ("pension_due", 0),
        ("weekly_holiday_included", 0),
        ("scope", " "),
        ("company_name", []),
        ("employee_name", ""),
        ("employee_age", True),
        ("insurance_assessment_month", "2026-1"),
        ("source_contract", bank_reconciliation.CONTRACT),
        ("regular_minutes", 1200),
        ("payment_date", "2026-11-25"),
    ],
)
def test_discarded_facts_strict_types_and_derived_field_rejection(key, value):
    facts = source()
    old(facts)[key] = value
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize("where", ["work", "break", "absence", "week", "payment", "paid_holiday"])
@pytest.mark.parametrize("mutation", ["unknown", "wrong_type", "bad_date"])
def test_every_nested_discarded_original_row_checked(where, mutation):
    facts = source("ordinary_and_clock_revision")
    f = facts["statement_records"][-1]["facts"]  # Never selected draft statement.
    if where == "work":
        row = f["work_records"][0]
        key, value = (
            ("revision", True) if mutation == "wrong_type" else ("start", "2026-11-05 9:00")
        )
    elif where == "break":
        row = {"start": "2026-11-05 21:10", "end": "2026-11-05 21:20"}
        f["work_records"][0]["breaks"].append(row)
        key, value = "start", None if mutation == "wrong_type" else "2026-11-05 21:60"
    elif where == "absence":
        row = {"record_id": "A", "date": "2026-11-05", "minutes": 5}
        f["regular_schedule"]["unpaid_absences"].append(row)
        key, value = ("minutes", False) if mutation == "wrong_type" else ("date", "2026-11-31")
    elif where == "week":
        row = {"week_id": "W", "scheduled_days": 5, "attended_days": 5}
        f["week_attendance"].append(row)
        key, value = ("attended_days", 5.0) if mutation == "wrong_type" else ("week_id", "")
    elif where == "payment":
        row = f["payment_records"][0]
        key, value = ("revision", False) if mutation == "wrong_type" else ("date", "20261125")
    else:
        row = {
            "date": "2026-11-08",
            "kind": "public_holiday",
            "four_week_scheduled_minutes": 9600,
            "normal_worker_four_week_days": 20,
            "included_in_regular_pay": True,
        }
        f["holiday_dates"].append("2026-11-08")
        f["paid_holiday_records"] = [row]
        key, value = (
            ("included_in_regular_pay", 1) if mutation == "wrong_type" else ("date", "2026-11-31")
        )
    if mutation == "unknown":
        row["gold"] = 0
    else:
        row[key] = value
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize("bad", ["interval", "break", "category", "negative_net", "pay_basis"])
def test_unselected_statement_and_unselected_work_full_validation(bad):
    facts = source("ordinary_and_clock_revision")
    f = facts["statement_records"][-1]["facts"]
    row = f["work_records"][0]
    row["status"] = "draft"  # Also skipped inside the discarded complete statement.
    if bad == "interval":
        row["end"] = row["start"]
    elif bad == "break":
        row["breaks"] = [{"start": "2026-11-05 20:00", "end": "2026-11-05 21:00"}]
    elif bad == "category":
        row["category"] = "invented"
    elif bad == "negative_net":
        f.update(base_salary=1, fixed_allowance=0)
    else:
        f["pay_basis"] = "hourly"
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize("kind", ["value", "type"])
def test_document_copy_conflict_even_unselected_valid_types(kind):
    facts = source("ordinary_and_clock_revision")
    duplicate = deepcopy(facts["statement_records"][-1])
    if kind == "value":
        duplicate["facts"]["scope"] += " conflicting"
    else:
        duplicate["facts"]["hourly_rate"] = 0.0  # Individually valid, typed copy conflict.
    facts["statement_records"].append(duplicate)
    with pytest.raises(ValueError, match="typed duplicate"):
        calculate(facts)


@pytest.mark.parametrize("status", ["draft", "superseded"])
def test_distinct_document_same_revision_rejected_even_same_contents(status):
    facts = source()
    duplicate = deepcopy(facts["statement_records"][1])
    duplicate.update(document_id="ANOTHER", status=status)
    facts["statement_records"].append(duplicate)
    with pytest.raises(ValueError, match="same group revision"):
        calculate(facts)


@pytest.mark.parametrize("all_draft", [False, True])
def test_no_selected_statement_rejected(all_draft):
    facts = source()
    if all_draft:
        for row in facts["statement_records"]:
            row["status"] = "draft"
    else:
        facts["statement_records"] = []
    with pytest.raises(ValueError, match="approved complete"):
        calculate(facts)


@pytest.mark.parametrize(
    "change", ["executed_date", "planned_ref", "duplicate_conflict", "bool_amount"]
)
def test_bank_rules_unchanged_and_all_transfers_checked(change):
    facts = source()
    facts["as_of_date"] = "2026-11-01"
    row = facts["transfers"][0]
    if change == "executed_date":
        row["date"] = "2026-11-24"
    elif change == "planned_ref":
        row.update(status="planned", employee_id="WRONG")
    elif change == "duplicate_conflict":
        facts["transfers"].append({**row, "amount": row["amount"] + 1})
    else:
        row["amount"] = True
    with pytest.raises(ValueError):
        calculate(facts)


def test_payout_date_can_correct_but_bank_must_match_selected_actual_payday():
    facts = source()
    old(facts)["payment_records"][0]["date"] = "2026-11-24"
    assert calculate(facts)[0]["paid_total"] == 290000
    current(facts)["payment_records"][0]["date"] = "2026-11-26"
    with pytest.raises(ValueError, match="another payday"):
        calculate(facts)


@pytest.mark.parametrize(
    "where", ["raw_statements", "unique_statements", "groups", "raw_transfers", "unique_transfers"]
)
def test_finite_bounds(where):
    facts = source()
    if where == "raw_statements":
        facts["statement_records"] = [deepcopy(facts["statement_records"][0])] * 129
    elif where == "raw_transfers":
        facts["transfers"] *= 201
    elif where == "unique_transfers":
        facts["transfers"] = [{**facts["transfers"][0], "transfer_id": f"T{i}"} for i in range(101)]
    elif where == "unique_statements":
        first = facts["statement_records"][0]
        facts["statement_records"] = [
            {**deepcopy(first), "document_id": f"D{i}", "revision": i + 1} for i in range(65)
        ]
    else:
        first = facts["statement_records"][0]
        facts["statement_records"] = [
            {
                **deepcopy(first),
                "document_id": f"D{i}",
                "employee_id": f"E{i}",
                "payroll_id": f"P{i}",
            }
            for i in range(17)
        ]
    with pytest.raises(ValueError):
        calculate(facts)


def test_caller_answer_and_trace_share_no_mutable_containers():
    facts = source()
    original = deepcopy(facts)
    answer, trace = calculate(facts)
    assert facts == original
    expected_answer, expected_trace = deepcopy(answer), deepcopy(trace)
    current(facts)["regular_schedule"]["working_days"] = 100
    assert (answer, trace) == (expected_answer, expected_trace)
    answer["payroll_calculations"][0]["calculation"]["net_pay"] = -1
    assert trace == expected_trace
    trace[0]["output"]["selected_payrolls"][0]["facts"]["work_records"].append({})
    assert trace[0]["inputs"]["statement_records"][1]["facts"]["work_records"] == []
    trace[1]["output"]["settlement"]["employee_settlements"][0]["paid"] = -1
    assert answer["employee_settlements"] == expected_answer["employee_settlements"]


@pytest.mark.parametrize(
    "key,value",
    [
        ("processing_date", "20261126"),
        ("as_of_date", "2026-11-31"),
        ("processing_policy", ""),
        ("statement_records", {}),
        ("transfers", None),
        ("source_contract", "bad"),
    ],
)
def test_source_required_shape(key, value):
    facts = source()
    facts[key] = value
    with pytest.raises(ValueError):
        calculate(facts)


def test_missing_and_unknown_object_fields():
    for location, key in [
        ("top", "processing_date"),
        ("statement", "issued_on"),
        ("facts", "scope"),
        ("schedule", "working_days"),
    ]:
        for missing in (True, False):
            facts = source()
            obj = (
                facts
                if location == "top"
                else facts["statement_records"][0]
                if location == "statement"
                else old(facts)
                if location == "facts"
                else old(facts)["regular_schedule"]
            )
            if missing:
                del obj[key]
            else:
                obj["unexpected"] = 1
            with pytest.raises(ValueError):
                calculate(facts)


def test_selected_family_is_used_and_higher_draft_family_is_not_mixed():
    facts = source("ordinary_and_clock_revision")
    current(facts).update(family_count=4, eligible_children=2)
    facts["statement_records"][-1]["facts"].update(family_count=1, eligible_children=0)
    answer, _ = calculate(facts)
    calculation = answer["payroll_calculations"][0]["calculation"]
    # The family4 row is below the March two-child credit of 45,830.
    assert calculation["income_tax"] == 0 and calculation["local_income_tax"] == 0
    assert calculation["total_deductions"] == 242920
    assert answer["net_total"] == 2413330 and answer["balance_total"] == 13330


@pytest.mark.parametrize(
    "election,income,local,net", [(80, 35170, 3510, 2374650), (120, 52760, 5270, 2355300)]
)
def test_selected_withholding_election_preserves_existing_truncation(election, income, local, net):
    facts = source("ordinary_and_clock_revision")
    current(facts)["withholding_percent"] = election
    answer, _ = calculate(facts)
    row = answer["payroll_calculations"][0]["calculation"]
    assert (row["income_tax"], row["local_income_tax"], row["net_pay"]) == (income, local, net)


def test_selected_insurance_fact_is_kept_whole_and_draft_not_combined():
    facts = source("ordinary_and_clock_revision")
    current(facts)["pension_due"] = False
    answer, _ = calculate(facts)
    row = answer["payroll_calculations"][0]["calculation"]
    assert row["national_pension"] == 0
    assert row["health_insurance"] == 89870 and row["employment_insurance"] == 22500
    assert answer["net_total"] == 2483720
    assert len(answer["employee_settlements"]) == 1
