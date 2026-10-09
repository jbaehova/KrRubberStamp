"""Private cash joins with independently worked payroll and strict boundaries."""

from copy import deepcopy
import json

import pytest

from rules.b_payroll import engine, evidence
from rules.b_payroll.bank_reconciliation import CONTRACT, RULE_ID, calculate


def _facts():
    return {
        "payment_date": "2026-02-25",
        "insurance_assessment_month": "2026-02",
        "pay_basis": "monthly",
        "base_salary": 500000,
        "fixed_allowance": 0,
        "meal_allowance": 0,
        "variable_allowance": 0,
        "monthly_divisor_hours": 209,
        "hourly_rate": 0,
        "weekly_holiday_included": True,
        "regular_minutes": 9600,
        "workplace_employee_count": 5,
        "weekly_hours": 40,
        "qualifying_weeks": 4,
        "overtime_minutes": 0,
        "night_minutes": 0,
        "holiday_shifts": [],
        "employer_provides_meals": False,
        "pension_notified_income": 500000,
        "health_notified_income": 500000,
        "employment_notified_income": 500000,
        "pension_due": True,
        "health_due": True,
        "employment_due": True,
        "family_count": 1,
        "eligible_children": 0,
        "withholding_percent": 100,
    }


def _source():
    return {
        "source_contract": CONTRACT,
        "processing_policy": "가상 회사의 완전한 월 급여명세와 실행 이체 ID를 대조한다.",
        "as_of_date": "2026-02-28",
        "payrolls": [{"payroll_id": "RUN-A", "employee_id": "EMP-A", "facts": _facts()}],
        "transfers": [],
    }


def _transfer(identity="BANK-1", amount=100000, **changes):
    return {
        "transfer_id": identity,
        "payroll_id": "RUN-A",
        "employee_id": "EMP-A",
        "date": "2026-02-25",
        "status": "executed",
        "amount": amount,
        **changes,
    }


def test_independent_handworked_two_person_complete_monthly_statements():
    source = _source()
    larger = _facts()
    larger.update(
        base_salary=3500000,
        pension_notified_income=2000000,
        health_notified_income=2000000,
        employment_notified_income=2000000,
        family_count=4,
        eligible_children=2,
    )
    source["payrolls"].append({"payroll_id": "RUN-B", "employee_id": "EMP-B", "facts": larger})
    source["transfers"] = [
        _transfer(amount=451420),
        _transfer("BANK-2", 3283470, payroll_id="RUN-B", employee_id="EMP-B"),
    ]
    answer, trace = calculate(source)
    a, b = [row["calculation"] for row in answer["payroll_calculations"]]
    # A: 500000*.0475=23750, floor10(500000*.03595)=17970,
    # floor10(17970*9448/71900)=2360, 500000*.009=4500; tax below 770000 is zero.
    assert [
        a[key]
        for key in (
            "national_pension",
            "health_insurance",
            "long_term_care",
            "employment_insurance",
            "income_tax",
            "local_income_tax",
        )
    ] == [23750, 17970, 2360, 4500, 0, 0]
    assert (a["total_deductions"], a["net_pay"]) == (48580, 451420)
    # B: 95000+71900+9440+18000; official Feb family4/children2 tax=20180,
    # local=floor10(20180/10)=2010. Whole monthly statement remains unsplit.
    assert [
        b[key]
        for key in (
            "national_pension",
            "health_insurance",
            "long_term_care",
            "employment_insurance",
            "income_tax",
            "local_income_tax",
        )
    ] == [95000, 71900, 9440, 18000, 20180, 2010]
    assert (b["total_deductions"], b["net_pay"]) == (216530, 3283470)
    assert [
        answer[key]
        for key in ("gross_total", "deductions_total", "net_total", "paid_total", "balance_total")
    ] == [4000000, 265110, 3734890, 3734890, 0]
    assert all(row["balance"] == 0 for row in answer["employee_settlements"])
    assert trace[0]["rule_id"] == RULE_ID


@pytest.mark.parametrize("paid,balance", [(100000, 351420), (500000, -48580)])
def test_partial_payment_and_signed_overpayment(paid, balance):
    source = _source()
    source["transfers"] = [_transfer(amount=paid)]
    answer, _ = calculate(source)
    assert answer["employee_settlements"][0]["paid"] == paid
    assert answer["balance_total"] == balance
    assert answer["net_total"] - answer["paid_total"] == answer["balance_total"]


def test_duplicate_ids_once_equal_amount_different_ids_independently():
    source = _source()
    one = _transfer()
    source["transfers"] = [one, deepcopy(one), _transfer("BANK-2")]
    answer, trace = calculate(source)
    assert answer["paid_total"] == 200000
    assert trace[0]["output"]["deduplicated_transfer_ids"] == ["BANK-1"]
    assert trace[0]["output"]["accepted_transfer_ids"] == ["BANK-1", "BANK-2"]


def test_conflicting_duplicate_transfer_rejected():
    source = _source()
    source["transfers"] = [_transfer(), _transfer(amount=100001)]
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        calculate(source)


def test_planned_and_future_excluded_but_source_preserved():
    source = _source()
    source["as_of_date"] = "2026-02-24"
    source["transfers"] = [
        _transfer(),
        _transfer("PLAN", 99999, status="planned", date="2026-03-01"),
    ]
    answer, trace = calculate(source)
    assert answer["paid_total"] == 0
    assert answer["balance_total"] == 451420
    assert trace[0]["output"]["excluded_transfer_ids"] == ["BANK-1", "PLAN"]
    assert len(trace[0]["inputs"]["transfers"]) == 2


@pytest.mark.parametrize("status", ["executed", "planned"])
@pytest.mark.parametrize("changes", [{"payroll_id": "missing"}, {"employee_id": "EMP-X"}])
def test_reference_validation_even_for_future_and_planned(status, changes):
    source = _source()
    source["as_of_date"] = "2026-02-01"
    source["transfers"] = [_transfer(status=status, **changes)]
    with pytest.raises(ValueError, match="references must match"):
        calculate(source)


@pytest.mark.parametrize("amount", [True, False, 1.0, -1, "100", None])
def test_transfer_strict_amount_types_including_duplicates(amount):
    source = _source()
    source["transfers"] = [_transfer(amount=1), _transfer(amount=amount)]
    with pytest.raises(ValueError, match="strict integer"):
        calculate(source)


def test_actual_payday_mismatch_rejected_even_after_cutoff():
    source = _source()
    source["as_of_date"] = "2026-02-01"
    source["transfers"] = [_transfer(date="2026-03-01")]
    with pytest.raises(ValueError, match="another payday"):
        calculate(source)


def test_repeated_same_employee_assessment_month_rejected():
    source = _source()
    another = deepcopy(source["payrolls"][0])
    another["payroll_id"] = "RUN-B"
    another["facts"]["payment_date"] = "2026-02-26"
    source["payrolls"].append(another)
    with pytest.raises(ValueError, match="split a monthly statement"):
        calculate(source)


def test_distinct_months_same_employee_allowed_and_independently_matched():
    source = _source()
    another = deepcopy(source["payrolls"][0])
    another["payroll_id"] = "RUN-NEXT"
    another["facts"]["insurance_assessment_month"] = "2026-03"
    another["facts"]["payment_date"] = "2026-03-25"
    source["as_of_date"] = "2026-03-31"
    source["payrolls"].append(another)
    source["transfers"] = [_transfer("NEXT", 451420, payroll_id="RUN-NEXT", date="2026-03-25")]
    answer, _ = calculate(source)
    assert len(answer["employee_settlements"]) == 2
    assert [row["paid"] for row in answer["employee_settlements"]] == [0, 451420]
    assert answer["balance_total"] == 451420


@pytest.mark.parametrize("contract", [CONTRACT, "unknown"])
def test_nested_and_unknown_child_contracts_rejected(contract):
    source = _source()
    source["payrolls"][0]["facts"]["source_contract"] = contract
    with pytest.raises(ValueError, match="nested"):
        calculate(source)


@pytest.mark.parametrize(
    "where,value",
    [
        ("as_of_date", "20260228"),
        ("as_of_date", "2026-2-28"),
        ("as_of_date", "2026-02-30"),
        ("processing_policy", " "),
        ("payrolls", []),
        ("payrolls", {}),
        ("transfers", {}),
    ],
)
def test_required_source_and_strict_dates(where, value):
    source = _source()
    source[where] = value
    with pytest.raises(ValueError):
        calculate(source)


def test_exact_row_shapes_and_unique_payroll_ids():
    source = _source()
    source["payrolls"].append(deepcopy(source["payrolls"][0]))
    with pytest.raises(ValueError, match="Duplicate payroll_id"):
        calculate(source)
    source = _source()
    source["transfers"] = [{**_transfer(), "bank_name": "unmatched"}]
    with pytest.raises(ValueError, match="unknown or missing"):
        calculate(source)


def test_raw_child_derivation_byte_order_and_parent_order_invariance():
    source = _source()
    raw = _facts()
    for key in evidence.DERIVED:
        raw.pop(key, None)
    raw.update(
        source_contract=evidence.CONTRACT,
        work_records=[],
        holiday_dates=[],
        week_attendance=[
            {"week_id": "later", "scheduled_days": 5, "attended_days": 5},
            {"week_id": "earlier", "scheduled_days": 5, "attended_days": 4},
        ],
        payment_records=[
            {"revision": 2, "date": "2026-02-25", "status": "approved"},
            {"revision": 1, "date": "2026-02-24", "status": "cancelled"},
        ],
        meal_service="none",
        regular_schedule={"working_days": 20, "minutes_per_day": 480, "unpaid_absences": []},
    )
    source["payrolls"].append({"payroll_id": "RAW", "employee_id": "EMP-Z", "facts": raw})
    source["transfers"] = [_transfer("B"), _transfer("A"), _transfer("B")]
    original = deepcopy(source)
    answer, trace = calculate(source)
    assert source == original
    normalized = evidence.interpret(raw)
    old_answer, old_trace = engine.calculate(normalized)
    expected_trace = [evidence.derivation_trace(raw, normalized), *old_trace]
    raw_entry = next(row for row in answer["payroll_calculations"] if row["payroll_id"] == "RAW")
    assert raw_entry["calculation"] == old_answer
    child = next(
        row for row in trace[0]["output"]["payroll_derivations"] if row["payroll_id"] == "RAW"
    )
    assert json.dumps(child["trace"]) == json.dumps(expected_trace)
    source["payrolls"].reverse()
    source["transfers"].reverse()
    assert calculate(source) == (answer, trace)


def test_no_shared_mutable_containers_between_source_answer_and_trace():
    source = _source()
    answer, trace = calculate(source)
    baseline_answer, baseline_trace = deepcopy(answer), deepcopy(trace)
    source["payrolls"][0]["facts"]["holiday_shifts"].append({"minutes": 1})
    assert (answer, trace) == (baseline_answer, baseline_trace)
    answer["payroll_calculations"][0]["calculation"]["net_pay"] = -999
    assert trace == baseline_trace
    trace[0]["inputs"]["payrolls"][0]["facts"]["holiday_shifts"].append({"minutes": 2})
    assert len(source["payrolls"][0]["facts"]["holiday_shifts"]) == 1
    trace[0]["output"]["settlement"]["employee_settlements"][0]["paid"] = -888
    assert answer["employee_settlements"] == baseline_answer["employee_settlements"]


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
def test_public_registry_restores_actual_nested_documents(tmp_path, fmt):
    from KrRubberStamp.registry import calculate as registered_calculate
    from render.authored import render_authored
    from render.documents import restore_scenario

    facts = _source()
    documents = [
        {
            "filename": "원본." + fmt,
            "format": fmt,
            "title": "원자료 연결 통합 검산",
            "note": "합성 원자료의 실제 기재를 복원하여 대조합니다.",
            "fields": list(facts),
        }
    ]
    render_authored(facts, tmp_path, "B_payroll", documents)
    restored = restore_scenario(tmp_path)
    assert restored == facts
    answer, trace = registered_calculate("B_payroll", restored)
    assert answer["net_total"] == 451_420 and answer["balance_total"] == 451_420
    assert trace[0]["rule_id"] == RULE_ID
    if fmt == "xlsx":
        import json
        from openpyxl import load_workbook

        mapping = json.loads((tmp_path / "extraction_map.json").read_text())
        workbook = load_workbook(tmp_path / "inputs/원본.xlsx")
        for path, amount in [(["payrolls", 0, "facts", "base_salary"], 600000)]:
            record = next(row for row in mapping["records"] if row["path"] == path)
            selector = record["selector"]
            workbook[selector["sheet"]][selector["cell"]] = amount
        workbook.save(tmp_path / "inputs/원본.xlsx")
        workbook.close()
        after, _ = registered_calculate("B_payroll", restore_scenario(tmp_path))
        assert after["net_total"] == 551_420 and after["balance_total"] == 551_420
