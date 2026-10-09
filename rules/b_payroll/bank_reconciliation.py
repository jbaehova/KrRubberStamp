"""Match complete monthly payroll statements to synthetic employer bank rows.

This optional agreement reconciles cash only. The unchanged payroll engine owns
all wage, insurance and withholding arithmetic. Split paydays and arrears are
outside this contract, rather than new tax rules inferred from bank records.
"""

from collections import defaultdict
from copy import deepcopy
from datetime import date

from rules.b_payroll import engine, evidence

CONTRACT = "payroll_bank_reconciliation_v1"
RULE_ID = "B_PAYROLL_BANK_RECONCILIATION"


def _text(value, name):
    if type(value) is not str or not value.strip():
        raise ValueError(f"Bank reconciliation requires nonempty {name}")
    return value


def _date(value):
    _text(value, "ISO date")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("Bank reconciliation dates must use YYYY-MM-DD")
    return parsed


def _rows(value, fields, name):
    if type(value) is not list:
        raise ValueError(f"Bank reconciliation {name} must be a list")
    for row in value:
        if type(row) is not dict or set(row) != fields:
            raise ValueError(f"Bank reconciliation {name} has unknown or missing fields")
    return value


def _child(facts):
    if type(facts) is not dict:
        raise ValueError("Payroll facts must be a literal object")
    if "source_contract" in facts:
        if facts["source_contract"] != evidence.CONTRACT:
            raise ValueError("Unsupported or nested payroll source contract")
        normalized = evidence.interpret(facts)
        answer, trace = engine.calculate(normalized)
        trace = [evidence.derivation_trace(facts, normalized), *trace]
    else:
        normalized = facts
        answer, trace = engine.calculate(normalized)
    _date(answer["effective_payment_date"])
    return answer, trace, normalized["insurance_assessment_month"]


def calculate(source: dict) -> tuple[dict, list[dict]]:
    """Return canonical statement calculations, signed cash balances and trace."""
    fields = {"source_contract", "processing_policy", "as_of_date", "payrolls", "transfers"}
    if type(source) is not dict or source.get("source_contract") != CONTRACT:
        raise ValueError("Unknown payroll bank reconciliation source contract")
    if set(source) != fields:
        raise ValueError("Bank reconciliation source has unknown or missing fields")
    policy = _text(source["processing_policy"], "visible processing policy")
    cutoff = _date(source["as_of_date"])
    payrolls = _rows(source["payrolls"], {"payroll_id", "employee_id", "facts"}, "payrolls")
    if not payrolls:
        raise ValueError("Bank reconciliation requires complete monthly payroll statements")
    by_id = {}
    employee_months = set()
    calculations, derivations, settlements = [], [], []
    for payroll in payrolls:
        identity = _text(payroll["payroll_id"], "payroll_id")
        employee = _text(payroll["employee_id"], "employee_id")
        if identity in by_id:
            raise ValueError("Duplicate payroll_id")
        calculation, child_trace, month = _child(deepcopy(payroll["facts"]))
        if (employee, month) in employee_months:
            raise ValueError("Repeated employee assessment month would split a monthly statement")
        employee_months.add((employee, month))
        by_id[identity] = {"employee_id": employee, "calculation": calculation}
        calculations.append(
            {"payroll_id": identity, "employee_id": employee, "calculation": calculation}
        )
        derivations.append({"payroll_id": identity, "trace": child_trace})
        settlements.append(
            {
                "payroll_id": identity,
                "employee_id": employee,
                "effective_payment_date": calculation["effective_payment_date"],
                "insurance_assessment_month": month,
                "gross_pay": calculation["gross_pay"],
                "total_deductions": calculation["total_deductions"],
                "net_pay": calculation["net_pay"],
            }
        )

    transfers = _rows(
        source["transfers"],
        {"transfer_id", "payroll_id", "employee_id", "date", "status", "amount"},
        "transfers",
    )
    unique, duplicates = {}, set()
    for transfer in transfers:
        identity = _text(transfer["transfer_id"], "transfer_id")
        payroll_id = _text(transfer["payroll_id"], "transfer payroll_id")
        employee = _text(transfer["employee_id"], "transfer employee_id")
        if payroll_id not in by_id or employee != by_id[payroll_id]["employee_id"]:
            raise ValueError("Transfer payroll and employee references must match")
        day = _date(transfer["date"])
        if type(transfer["amount"]) is not int or transfer["amount"] < 0:
            raise ValueError("Transfer amount must be a nonnegative strict integer")
        if type(transfer["status"]) is not str or transfer["status"] not in {"executed", "planned"}:
            raise ValueError("Unsupported transfer status")
        if transfer["status"] == "executed":
            effective = by_id[payroll_id]["calculation"]["effective_payment_date"]
            if day.isoformat() != effective:
                raise ValueError("Executed transfer on another payday is outside this contract")
        if identity in unique:
            prior = unique[identity]
            if prior != transfer or any(
                type(prior[key]) is not type(value) for key, value in transfer.items()
            ):
                raise ValueError("Conflicting duplicate transfer_id")
            duplicates.add(identity)
        unique[identity] = transfer

    paid = defaultdict(int)
    accepted, excluded = [], []
    for identity, transfer in sorted(unique.items()):
        if transfer["status"] == "executed" and _date(transfer["date"]) <= cutoff:
            accepted.append(identity)
            paid[transfer["payroll_id"]] += transfer["amount"]
        else:
            excluded.append(identity)
    for settlement in settlements:
        settlement["paid"] = paid[settlement["payroll_id"]]
        settlement["balance"] = settlement["net_pay"] - settlement["paid"]
    settlements.sort(key=lambda row: (row["employee_id"], row["payroll_id"]))
    answer = {
        "payroll_calculations": sorted(calculations, key=lambda row: row["payroll_id"]),
        "employee_settlements": settlements,
        "gross_total": sum(row["gross_pay"] for row in settlements),
        "deductions_total": sum(row["total_deductions"] for row in settlements),
        "net_total": sum(row["net_pay"] for row in settlements),
        "paid_total": sum(row["paid"] for row in settlements),
        "balance_total": sum(row["balance"] for row in settlements),
    }
    canonical_source = deepcopy(source)
    canonical_source["payrolls"].sort(key=lambda row: row["payroll_id"])
    canonical_source["transfers"].sort(key=lambda row: row["transfer_id"])
    trace = {
        "rule_id": RULE_ID,
        "inputs": {**canonical_source, "processing_policy": policy},
        "output": {
            "payroll_derivations": sorted(derivations, key=lambda row: row["payroll_id"]),
            "accepted_transfer_ids": accepted,
            "excluded_transfer_ids": excluded,
            "deduplicated_transfer_ids": sorted(duplicates),
            "cash_by_payroll": [
                {"payroll_id": identity, "paid": paid[identity]} for identity in sorted(by_id)
            ],
            "settlement": deepcopy(answer),
        },
    }
    # No mutable containers are shared between caller facts, returned answer and trace.
    return deepcopy(answer), deepcopy([trace])
