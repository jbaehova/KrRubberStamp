"""Review targeted fact relationships; this never generates benchmark content."""

from copy import deepcopy
from pathlib import Path

from KrRubberStamp.authoring import load_cases
from KrRubberStamp.io import write_json
from KrRubberStamp.registry import calculate

ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = {case["case_id"]: case for case, _ in load_cases(file_name="preview.json")}
    checks = []

    def answer(case_id, facts=None):
        case = cases[case_id]
        return calculate(case["domain"], case["facts"] if facts is None else facts)[0]

    baseline = answer("A003")
    changed = deepcopy(cases["A003"]["facts"])
    changed["education"][0]["scholarship"] = 0
    after = answer("A003", changed)
    assert after["education_credit"] - baseline["education_credit"] == 75000
    checks.append(
        {
            "case_id": "A003",
            "relationship": "장학금 차감 여부가 실제 교육비 공제와 세액을 변경",
            "baseline_credit": baseline["education_credit"],
            "omitted_scholarship_credit": after["education_credit"],
        }
    )

    baseline = answer("B002")
    changed = deepcopy(cases["B002"]["facts"])
    missed = next(
        row for row in changed["week_attendance"] if row["attended_days"] < row["scheduled_days"]
    )
    missed["attended_days"] = missed["scheduled_days"]
    after = answer("B002", changed)
    assert after["weekly_holiday_pay"] - baseline["weekly_holiday_pay"] == 88000
    checks.append(
        {
            "case_id": "B002",
            "relationship": "출근이 채워진 주만 주휴 대상에 추가",
            "baseline_weekly_pay": baseline["weekly_holiday_pay"],
            "complete_week_pay": after["weekly_holiday_pay"],
        }
    )

    baseline = answer("B003")
    changed = deepcopy(cases["B003"]["facts"])
    changed["work_records"] = [
        row
        for row in changed["work_records"]
        if row["revision"] != 1 or row["record_id"] != changed["work_records"][1]["record_id"]
    ]
    assert answer("B003", changed) == baseline
    checks.append(
        {
            "case_id": "B003",
            "relationship": "같은 근무의 이전 승인본 제거는 정답 불변",
            "unchanged": True,
        }
    )
    changed = deepcopy(cases["B003"]["facts"])
    for row in changed["payment_records"]:
        if row["status"] == "executed":
            row["date"] = "2026-02-27"
    after = answer("B003", changed)
    assert after["income_tax"] > baseline["income_tax"]
    checks.append(
        {
            "case_id": "B003",
            "relationship": "실제 지급월이 자녀 원천징수 공제의 시행일을 결정",
            "march_tax": baseline["income_tax"],
            "february_tax": after["income_tax"],
        }
    )

    baseline = answer("C002")
    changed = deepcopy(cases["C002"]["facts"])
    meal = next(row for row in changed["activities"] if row["action"] == "meal")
    for participant in meal["participants"]:
        if participant["role"] == "customer":
            participant.update(role="employee", organization=changed["business_name"])
    after = answer("C002", changed)
    assert after["deductible_input_vat"] - baseline["deductible_input_vat"] == 60000
    assert after["net_vat"] == baseline["net_vat"] - 60000
    checks.append(
        {
            "case_id": "C002",
            "relationship": "실제 참석자 소속으로 고객 식사와 직원 식사 구별",
            "deductible_tax_delta": 60000,
            "net_payable_delta": -60000,
        }
    )

    target = ROOT / "reports/authored_semantic_checks.json"
    write_json(
        target,
        {
            "scope": "12-case authored preview, targeted editorial corrections",
            "passed": len(checks),
            "checks": checks,
        },
    )
    print({"passed": len(checks), "report": str(target)})


if __name__ == "__main__":
    main()
