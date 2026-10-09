"""Select one approved complete monthly statement under a private document policy.

Every received revision is validated, including drafts and discarded statements.
Wage, insurance, withholding and cash rules remain in the existing child engines.
"""

from copy import deepcopy
from datetime import date, datetime
import math

from rules.b_payroll import bank_reconciliation, engine, evidence

CONTRACT = "payroll_statement_revision_v1"
RULE_ID = "B_PAYROLL_STATEMENT_REVISION"
TOP_FIELDS = {
    "source_contract",
    "processing_policy",
    "processing_date",
    "as_of_date",
    "statement_records",
    "transfers",
}
STATEMENT_FIELDS = {
    "document_id",
    "payroll_id",
    "employee_id",
    "statement_scope",
    "revision",
    "status",
    "issued_on",
    "facts",
}
FACT_FIELDS = {
    "source_contract",
    "company_name",
    "employee_name",
    "pay_basis",
    "base_salary",
    "fixed_allowance",
    "meal_allowance",
    "variable_allowance",
    "monthly_divisor_hours",
    "hourly_rate",
    "weekly_hours",
    "weekly_holiday_included",
    "workplace_employee_count",
    "work_records",
    "holiday_dates",
    "week_attendance",
    "payment_records",
    "meal_service",
    "pension_notified_income",
    "health_notified_income",
    "employment_notified_income",
    "pension_due",
    "health_due",
    "employment_due",
    "insurance_assessment_month",
    "family_count",
    "eligible_children",
    "withholding_percent",
    "scope",
}
OPTIONAL_FACT_FIELDS = {"employee_age", "regular_schedule", "paid_holiday_records"}


def _object(value, fields, name, optional=frozenset()):
    if type(value) is not dict or not fields <= value.keys() or value.keys() - fields - optional:
        raise ValueError(f"Revision {name} has unknown or missing fields")


def _text(value, name):
    if type(value) is not str or not value.strip():
        raise ValueError(f"Revision {name} must be nonempty text")
    return value


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"Revision {name} must be a strict integer >= {minimum}")
    return value


def _enum(value, choices, name):
    if type(value) is not str or value not in choices:
        raise ValueError(f"Revision {name} has unsupported value")


def _date(value):
    _text(value, "date")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Revision dates must use YYYY-MM-DD")
    return parsed


def _clock(value):
    _text(value, "clock")
    parsed = datetime.strptime(value, "%Y-%m-%d %H:%M")
    if parsed.strftime("%Y-%m-%d %H:%M") != value:
        raise ValueError("Revision clocks must use YYYY-MM-DD HH:MM")
    return parsed


def _rows(value, fields, name, limit=None):
    if type(value) is not list or (limit is not None and len(value) > limit):
        raise ValueError(f"Revision {name} must be a bounded list")
    for row in value:
        _object(row, fields, name)
    return value


def _typed(value):
    """Include nested primitive types so bool/int and float/int never alias."""
    if type(value) is dict:
        return ("dict", tuple((key, _typed(value[key])) for key in sorted(value)))
    if type(value) is list:
        return ("list", tuple(_typed(item) for item in value))
    return (type(value).__name__, value)


def _validate_facts(facts):
    _object(facts, FACT_FIELDS, "facts", OPTIONAL_FACT_FIELDS)
    _enum(facts["source_contract"], {evidence.CONTRACT}, "child contract")
    for key in ("company_name", "employee_name", "scope"):
        _text(facts[key], key)
    _enum(facts["pay_basis"], {"monthly", "hourly"}, "pay_basis")
    for key in (
        "base_salary",
        "fixed_allowance",
        "meal_allowance",
        "variable_allowance",
        "workplace_employee_count",
        "pension_notified_income",
        "health_notified_income",
        "employment_notified_income",
        "eligible_children",
    ):
        _integer(facts[key], key)
    _integer(facts["monthly_divisor_hours"], "monthly_divisor_hours", 1)
    _integer(facts["family_count"], "family_count", 1)
    if facts["eligible_children"] >= facts["family_count"]:
        raise ValueError("Revision children must be fewer than family count")
    _integer(facts["weekly_hours"], "weekly_hours")
    if facts["weekly_hours"] > 40:
        raise ValueError("Revision weekly hours exceed 40")
    _integer(facts["withholding_percent"], "withholding_percent")
    if facts["withholding_percent"] not in {80, 100, 120}:
        raise ValueError("Unsupported withholding percentage")
    rate = facts["hourly_rate"]
    if (
        type(rate) not in {int, float}
        or rate < 0
        or (type(rate) is float and not math.isfinite(rate))
    ):
        raise ValueError("Revision hourly_rate must be finite nonnegative int or float")
    for key in ("weekly_holiday_included", "pension_due", "health_due", "employment_due"):
        if type(facts[key]) is not bool:
            raise ValueError(f"Revision {key} must be strict bool")
    if "employee_age" in facts:
        _integer(facts["employee_age"], "employee_age")
    month = _text(facts["insurance_assessment_month"], "insurance_assessment_month")
    if len(month) != 7 or _date(month + "-01").year != 2026:
        raise ValueError("Revision insurance month must be 2026 YYYY-MM")
    if "regular_schedule" in facts:
        schedule = facts["regular_schedule"]
        _object(schedule, {"working_days", "minutes_per_day", "unpaid_absences"}, "schedule")
        _integer(schedule["working_days"], "working_days")
        _integer(schedule["minutes_per_day"], "minutes_per_day")
        for row in _rows(schedule["unpaid_absences"], {"record_id", "date", "minutes"}, "absence"):
            _text(row["record_id"], "absence record_id")
            _date(row["date"])
            _integer(row["minutes"], "absence minutes")
    for row in _rows(
        facts["work_records"],
        {"record_id", "revision", "status", "category", "start", "end", "breaks"},
        "work",
    ):
        _text(row["record_id"], "work record_id")
        _integer(row["revision"], "work revision", 1)
        _enum(row["status"], {"approved", "superseded", "draft"}, "work status")
        _enum(row["category"], {"regular", "additional"}, "work category")
        _clock(row["start"])
        _clock(row["end"])
        for pause in _rows(row["breaks"], {"start", "end"}, "break"):
            _clock(pause["start"])
            _clock(pause["end"])
        evidence._segments(row)  # Validate even work records the interpreter discards.
    if type(facts["holiday_dates"]) is not list:
        raise ValueError("Revision holiday_dates must be a list")
    for value in facts["holiday_dates"]:
        _date(value)
    for row in _rows(
        facts["week_attendance"], {"week_id", "scheduled_days", "attended_days"}, "week"
    ):
        _text(row["week_id"], "week_id")
        scheduled = _integer(row["scheduled_days"], "scheduled_days")
        attended = _integer(row["attended_days"], "attended_days")
        if attended > scheduled or scheduled > 7:
            raise ValueError("Invalid weekly attendance")
    for row in _rows(facts["payment_records"], {"revision", "status", "date"}, "payment"):
        _integer(row["revision"], "payment revision")
        _enum(row["status"], {"executed", "approved", "cancelled"}, "payment status")
        _date(row["date"])
    _enum(facts["meal_service"], {"none", "employer_catering"}, "meal_service")
    for row in _rows(
        facts.get("paid_holiday_records", []),
        {
            "date",
            "kind",
            "four_week_scheduled_minutes",
            "normal_worker_four_week_days",
            "included_in_regular_pay",
        },
        "paid holiday",
    ):
        _date(row["date"])
        _enum(row["kind"], {"public_holiday", "labor_day"}, "paid holiday kind")
        _integer(row["four_week_scheduled_minutes"], "four_week_scheduled_minutes")
        _integer(row["normal_worker_four_week_days"], "normal_worker_four_week_days", 1)
        if type(row["included_in_regular_pay"]) is not bool:
            raise ValueError("Paid holiday inclusion must be strict bool")
    normalized = evidence.interpret(deepcopy(facts))
    engine.calculate(normalized)  # Full legacy arithmetic/negative-net guards for every revision.


def calculate(source):
    """Select approved source documents, then use the unchanged monthly bank join."""
    _object(source, TOP_FIELDS, "source")
    _enum(source["source_contract"], {CONTRACT}, "source_contract")
    _text(source["processing_policy"], "processing_policy")
    processing = _date(source["processing_date"])
    _date(source["as_of_date"])
    records = _rows(source["statement_records"], STATEMENT_FIELDS, "statement_records", 128)
    transfers = _rows(
        source["transfers"],
        {"transfer_id", "payroll_id", "employee_id", "date", "status", "amount"},
        "transfers",
        200,
    )
    documents, copies = {}, set()
    for row in records:
        identity = _text(row["document_id"], "document_id")
        _text(row["payroll_id"], "payroll_id")
        _text(row["employee_id"], "employee_id")
        _enum(row["statement_scope"], {"complete_monthly"}, "statement_scope")
        _integer(row["revision"], "revision", 1)
        _enum(row["status"], {"approved", "draft", "superseded"}, "status")
        if _date(row["issued_on"]) > processing:
            raise ValueError("Statement issued after processing_date")
        _validate_facts(row["facts"])
        if identity in documents:
            if _typed(documents[identity]) != _typed(row):
                raise ValueError("Conflicting typed duplicate document_id")
            copies.add(identity)
        documents[identity] = deepcopy(row)
    if len(documents) > 64:
        raise ValueError("At most 64 unique statement documents")
    groups, payroll_groups = {}, {}
    for row in documents.values():
        group = (row["employee_id"], row["facts"]["insurance_assessment_month"])
        payroll = row["payroll_id"]
        if payroll in payroll_groups and payroll_groups[payroll] != group:
            raise ValueError("Stable payroll_id reused across employee/month groups")
        payroll_groups[payroll] = group
        groups.setdefault(group, []).append(row)
    if len(groups) > 16:
        raise ValueError("At most 16 employee/month groups")
    selected, group_trace = [], []
    for (employee, month), rows in sorted(groups.items()):
        if len({row["payroll_id"] for row in rows}) != 1:
            raise ValueError("An employee/month group requires one stable payroll_id")
        rows.sort(key=lambda row: row["revision"])
        if len({row["revision"] for row in rows}) != len(rows):
            raise ValueError("Different documents claim the same group revision")
        if any(rows[i]["issued_on"] > rows[i + 1]["issued_on"] for i in range(len(rows) - 1)):
            raise ValueError("Higher revision issued_on reverses document chronology")
        approved = [row for row in rows if row["status"] == "approved"]
        chosen = approved[-1] if approved else None
        if chosen:
            selected.append(chosen)
        group_trace.append(
            {
                "employee_id": employee,
                "insurance_assessment_month": month,
                "payroll_id": rows[0]["payroll_id"],
                "selected_document_id": chosen["document_id"] if chosen else None,
                "selected_revision": chosen["revision"] if chosen else None,
                "document_ids": sorted(row["document_id"] for row in rows),
            }
        )
    if not selected:
        raise ValueError("At least one approved complete monthly statement is required")
    transfer_ids = {_text(row["transfer_id"], "transfer_id") for row in transfers}
    if len(transfer_ids) > 100:
        raise ValueError("At most 100 unique bank transfers")
    bank_source = {
        "source_contract": bank_reconciliation.CONTRACT,
        "processing_policy": source["processing_policy"],
        "as_of_date": source["as_of_date"],
        "payrolls": [
            {
                "payroll_id": row["payroll_id"],
                "employee_id": row["employee_id"],
                "facts": deepcopy(row["facts"]),
            }
            for row in sorted(selected, key=lambda row: row["payroll_id"])
        ],
        "transfers": deepcopy(transfers),
    }
    answer, bank_trace = bank_reconciliation.calculate(bank_source)
    selected_ids = sorted(row["document_id"] for row in selected)
    canonical = deepcopy(source)
    canonical["statement_records"] = sorted(documents.values(), key=lambda row: row["document_id"])
    # Identical transfer copies are recorded by the unchanged bank trace.
    canonical["transfers"] = sorted(
        {row["transfer_id"]: deepcopy(row) for row in transfers}.values(),
        key=lambda row: row["transfer_id"],
    )
    trace = {
        "rule_id": RULE_ID,
        "inputs": canonical,
        "output": {
            "deduplicated_document_ids": sorted(copies),
            "selected_document_ids": selected_ids,
            "excluded_document_ids": sorted(set(documents) - set(selected_ids)),
            "groups": group_trace,
            "selected_payrolls": deepcopy(bank_source["payrolls"]),
        },
    }
    return deepcopy(answer), deepcopy([trace, *bank_trace])
