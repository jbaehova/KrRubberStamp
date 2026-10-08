"""Observable attendance facts must drive the payable time and applicable date."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from KrRubberStamp.registry import calculate
from rules.b_payroll.evidence import CONTRACT, DERIVED, interpret


def source():
    return {
        "source_contract": CONTRACT,
        "regular_schedule": {
            "working_days": 22,
            "minutes_per_day": 240,
            "unpaid_absences": [{"record_id": "absence", "date": "2026-04-15", "minutes": 240}],
        },
        "week_attendance": [
            {"week_id": "w1", "scheduled_days": 5, "attended_days": 5},
            {"week_id": "w2", "scheduled_days": 5, "attended_days": 4},
            {"week_id": "w3", "scheduled_days": 5, "attended_days": 5},
            {"week_id": "w4", "scheduled_days": 0, "attended_days": 0},
        ],
        "work_records": [],
        "holiday_dates": ["2026-02-22"],
        "payment_records": [
            {"revision": 9, "status": "cancelled", "date": "2026-02-27"},
            {"revision": 10, "status": "approved", "date": "2026-03-04"},
            {"revision": 2, "status": "executed", "date": "2026-03-03"},
        ],
        "meal_service": "none",
    }


def record(identity="h22", revision=2, status="approved", **overrides):
    return {
        "record_id": identity,
        "revision": revision,
        "status": status,
        "category": "additional",
        "start": "2026-02-22 14:00",
        "end": "2026-02-23 01:30",
        "breaks": [
            {"start": "2026-02-22 18:30", "end": "2026-02-22 19:00"},
            {"start": "2026-02-22 21:00", "end": "2026-02-22 21:30"},
        ],
        **overrides,
    }


def test_absence_weekly_completion_and_execution_are_derived_not_given():
    raw = source()
    original = deepcopy(raw)
    result = interpret(raw)
    assert result["regular_minutes"] == 5040
    assert result["qualifying_weeks"] == 2
    assert result["payment_date"] == "2026-03-03"
    assert result["employer_provides_meals"] is False
    assert raw == original
    raw["week_attendance"][1]["attended_days"] = 5
    assert interpret(raw)["qualifying_weeks"] == 3


def test_latest_approval_deduplicates_and_breaks_reduce_overnight_work():
    raw = source()
    raw["work_records"] = [
        record(revision=1, end="2026-02-22 23:00"),
        record(),
        record(identity="draft", status="draft"),
    ]
    result = interpret(raw)
    assert result["holiday_shifts"] == [{"minutes": 630, "holiday_night_minutes": 210}]
    assert result["night_minutes"] == 210
    assert result["overtime_minutes"] == 0
    raw["work_records"][1]["breaks"].append(
        {"start": "2026-02-22 23:00", "end": "2026-02-22 23:30"}
    )
    result = interpret(raw)
    assert result["holiday_shifts"][0]["minutes"] == 600
    assert result["night_minutes"] == 180


def test_separate_blocks_on_one_holiday_share_eight_hour_boundary():
    raw = source()
    raw["work_records"] = [
        record(identity="morning", start="2026-02-22 08:00", end="2026-02-22 13:00", breaks=[]),
        record(identity="afternoon", start="2026-02-22 14:00", end="2026-02-22 19:00", breaks=[]),
    ]
    assert interpret(raw)["holiday_shifts"] == [{"minutes": 600, "holiday_night_minutes": 0}]


def test_regular_clock_record_night_and_early_morning_boundaries():
    raw = source()
    del raw["regular_schedule"]
    raw["work_records"] = [
        record(category="regular", start="2026-02-20 04:30", end="2026-02-20 08:30", breaks=[])
    ]
    result = interpret(raw)
    assert result["regular_minutes"] == 240
    assert result["night_minutes"] == 90
    assert result["overtime_minutes"] == 0
    raw["work_records"][0]["category"] = "additional"
    assert interpret(raw)["overtime_minutes"] == 240


@pytest.mark.parametrize("key", sorted(DERIVED))
def test_raw_source_rejects_precomputed_central_fields(key):
    raw = source()
    raw[key] = 0
    with pytest.raises(ValueError, match="precomputed"):
        interpret(raw)


@pytest.mark.parametrize(
    "records,message",
    [
        ([record(), record(end="2026-02-23 02:30")], "Conflicting"),
        ([record(), record(identity="another")], "overlap"),
        ([record(breaks=[{"start": "2026-02-22 12:00", "end": "2026-02-22 13:00"}])], "Breaks"),
        ([record(end="2026-02-24 01:30")], "24 hours"),
        ([record(category="regular")], "double count"),
    ],
)
def test_contradictory_clock_evidence_is_rejected(records, message):
    raw = source()
    raw["work_records"] = records
    with pytest.raises(ValueError, match=message):
        interpret(raw)


def test_conflicting_execution_dates_cannot_be_selected_arbitrarily():
    raw = source()
    raw["payment_records"].append({"revision": 2, "status": "executed", "date": "2026-03-05"})
    with pytest.raises(ValueError, match="Conflicting authoritative"):
        interpret(raw)


def test_incomplete_or_duplicate_attendance_is_rejected():
    raw = source()
    raw["week_attendance"][0]["attended_days"] = 6
    with pytest.raises(ValueError, match="Invalid weekly"):
        interpret(raw)
    raw = source()
    raw["week_attendance"].append(deepcopy(raw["week_attendance"][0]))
    with pytest.raises(ValueError, match="Duplicate weekly"):
        interpret(raw)


def test_payroll_preview_uses_raw_evidence_trace_and_preserves_known_results():
    path = Path(__file__).resolve().parents[1] / "authored/batch_1/B_payroll/preview.json"
    cases = json.loads(path.read_text())
    absence, holiday = cases[1:]
    answer, trace = calculate("B_payroll", absence["facts"])
    assert answer["base_pay"] == 1848000
    assert answer["weekly_holiday_pay"] == 264000
    assert answer["net_pay"] == 1864320
    assert trace[0]["rule_id"] == "B.EVIDENCE_RECONCILIATION"
    answer, trace = calculate("B_payroll", holiday["facts"])
    assert answer["holiday_pay"] == 331867
    assert answer["night_pay"] == 48804
    assert answer["net_pay"] == 4010685
    assert trace[0]["output"]["payment_date"] == "2026-03-03"


def _authored(identity):
    root = Path(__file__).resolve().parents[1] / "authored/batch_1/B_payroll"
    for name in ("cases_004_053.json", "cases_054_103.json", "cases_104_153.json"):
        for case in json.loads((root / name).read_text()):
            if case["case_id"] == identity:
                return deepcopy(case["facts"])
    raise AssertionError(identity)


def test_june_insurance_assessment_is_independent_of_july_execution():
    raw = _authored("B089")
    answer, _ = calculate("B_payroll", raw)
    assert answer["effective_payment_date"] == "2026-07-03"
    assert answer["pension_base_income"] == 6370000
    assert answer["national_pension"] == 302570
    raw["payment_records"][1]["date"] = "2026-06-30"
    moved, _ = calculate("B_payroll", raw)
    assert moved["effective_payment_date"] == "2026-06-30"
    assert moved["national_pension"] == answer["national_pension"]
    raw["insurance_assessment_month"] = "2026-07"
    assert calculate("B_payroll", raw)[0]["national_pension"] == 308750


@pytest.mark.parametrize("month", [None, "2026-7", "2026-13", "2025-06", 6])
def test_missing_or_invalid_insurance_assessment_month_is_rejected(month):
    raw = _authored("B089")
    raw["insurance_assessment_month"] = month
    with pytest.raises((ValueError, TypeError)):
        calculate("B_payroll", raw)


def test_substitute_public_holiday_paid_wage_is_separate_from_work_premium():
    raw = _authored("B043")
    original = deepcopy(raw)
    answer, trace = calculate("B_payroll", raw)
    assert answer["paid_holiday_pay"] == 71000
    assert answer["holiday_pay"] == 294650
    assert answer["gross_pay"] == 1863750
    assert raw == original
    assert any(row["rule_id"] == "B.PAID_HOLIDAY" for row in trace)
    raw["paid_holiday_records"][0]["included_in_regular_pay"] = True
    included, _ = calculate("B_payroll", raw)
    assert included["paid_holiday_pay"] == 0
    assert included["gross_pay"] == answer["gross_pay"] - 71000
    assert included["holiday_pay"] == answer["holiday_pay"]


@pytest.mark.parametrize("workers,hours", [(4, 25), (19, 14)])
def test_public_holiday_eligibility_differs_from_labor_day(workers, hours):
    raw = _authored("B043")
    raw["workplace_employee_count"] = workers
    raw["weekly_hours"] = hours
    row = raw["paid_holiday_records"][0]
    row["four_week_scheduled_minutes"] = hours * 4 * 60
    assert interpret(raw)["paid_holiday_minutes"] == 0
    row["date"] = "2026-05-01"
    row["kind"] = "labor_day"
    raw["holiday_dates"].append(row["date"])
    assert interpret(raw)["paid_holiday_minutes"] == hours * 60 // 5


def test_paid_holiday_raw_contract_rejects_duplicate_weekly_and_fractional_time():
    raw = _authored("B043")
    raw["paid_holiday_records"].append(deepcopy(raw["paid_holiday_records"][0]))
    with pytest.raises(ValueError, match="unique"):
        interpret(raw)
    raw = _authored("B043")
    raw["paid_holiday_records"][0]["kind"] = "weekly_holiday"
    with pytest.raises(ValueError, match="Weekly"):
        interpret(raw)
    raw = _authored("B043")
    raw["paid_holiday_records"][0]["normal_worker_four_week_days"] = 19
    with pytest.raises(ValueError, match="whole-minute"):
        interpret(raw)
    raw = _authored("B043")
    raw["paid_holiday_records"][0]["four_week_scheduled_minutes"] = 2400
    with pytest.raises(ValueError, match="conflicts"):
        interpret(raw)


def test_monthly_paid_holiday_base_is_not_added_twice():
    from rules.b_payroll.engine import calculate as payroll_calculate
    from scenarios.b_payroll import generate

    normalized = generate(11, "easy")
    normalized["paid_holiday_minutes"] = 480
    with pytest.raises(ValueError, match="already includes"):
        payroll_calculate(normalized)


def test_declared_holiday_work_cannot_hide_in_normal_clock_records():
    raw = source()
    del raw["regular_schedule"]
    raw["work_records"] = [record(category="regular")]
    with pytest.raises(ValueError, match="additional-work"):
        interpret(raw)
