"""Read explicit private batch-payment composition, never infer allocations."""

from copy import deepcopy
from datetime import date

from . import bank_reconciliation

CONTRACT = "vat_bank_batch_allocation_v1"
RULE_ID = "C_VAT_BANK_BATCH_ALLOCATION"
SOURCE_FIELDS = {
    "source_contract",
    "processing_policy",
    "as_of_date",
    "filings",
    "bank_executions",
    "allocation_instructions",
}
EXECUTION_FIELDS = {"execution_id", "date", "status", "direction", "amount", "bank_fee"}
INSTRUCTION_FIELDS = {
    "instruction_id",
    "execution_id",
    "filing_id",
    "registration_id",
    "kind",
    "amount",
}


def _text(value):
    if type(value) is not str or not value.strip():
        raise ValueError("Batch allocation identifiers and policy must be nonempty text")
    return value


def _date(value):
    _text(value)
    result = date.fromisoformat(value)
    if result.isoformat() != value:
        raise ValueError("Batch allocation dates must be YYYY-MM-DD")
    return result


def _amount(value, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError("Batch allocation amounts must be strict nonnegative integers")
    return value


def _rows(value, fields, identity, maximum):
    if type(value) is not list or not 1 <= len(value) <= maximum:
        raise ValueError("Batch allocation rows exceed the bounded source contract")
    by_id = {}
    for row in value:
        if type(row) is not dict or set(row) != fields:
            raise ValueError("Batch allocation row has missing or unknown fields")
        key = _text(row[identity])
        if key in by_id:
            raise ValueError("Batch allocation duplicate source ID is unsupported")
        by_id[key] = row
    return by_id


def calculate(source):
    if (
        type(source) is not dict
        or set(source) != SOURCE_FIELDS
        or source.get("source_contract") != CONTRACT
    ):
        raise ValueError("Unknown or malformed VAT batch allocation contract")
    _text(source["processing_policy"])
    cutoff = _date(source["as_of_date"])
    executions = _rows(source["bank_executions"], EXECUTION_FIELDS, "execution_id", 20)
    instructions = _rows(
        source["allocation_instructions"], INSTRUCTION_FIELDS, "instruction_id", 60
    )
    for row in executions.values():
        _date(row["date"])
        _amount(row["amount"])
        _amount(row["bank_fee"])
        if _text(row["status"]) not in {"executed", "planned"}:
            raise ValueError("Unsupported bank execution status")
        if _text(row["direction"]) not in {"debit", "credit"}:
            raise ValueError("Unsupported bank execution direction")
        if row["direction"] == "credit" and row["bank_fee"]:
            raise ValueError("Refund batch fees are outside this contract")
    transfers = []
    composition = {key: [] for key in executions}
    for identity, row in sorted(instructions.items()):
        execution_id = _text(row["execution_id"])
        if execution_id not in executions:
            raise ValueError("Unknown allocation execution reference")
        execution = executions[execution_id]
        _text(row["filing_id"])
        _text(row["registration_id"])
        _amount(row["amount"], positive=True)
        allowed = (
            {"settlement_payment", "assessed_prepayment"}
            if execution["direction"] == "debit"
            else {"settlement_refund"}
        )
        if _text(row["kind"]) not in allowed:
            raise ValueError("Allocation purpose contradicts bank direction")
        composition[execution_id].append(row)
        transfers.append(
            {
                "transfer_id": identity,
                "filing_id": row["filing_id"],
                "registration_id": row["registration_id"],
                "date": execution["date"],
                "status": execution["status"],
                "kind": row["kind"],
                "amount": row["amount"],
            }
        )
    reconciliations = []
    totals = {
        "debit_total": 0,
        "credit_total": 0,
        "fee_total": 0,
        "assessed_debit_total": 0,
        "settlement_net_outflow": 0,
    }
    for identity, row in sorted(executions.items()):
        parts = composition[identity]
        if not parts:
            raise ValueError("Each bank execution needs complete allocation instructions")
        principal = sum(part["amount"] for part in parts)
        if row["amount"] != principal + row["bank_fee"]:
            raise ValueError("Bank gross amount differs from explicit principal and fee")
        assessed = sum(part["amount"] for part in parts if part["kind"] == "assessed_prepayment")
        included = row["status"] == "executed" and _date(row["date"]) <= cutoff
        reconciliations.append(
            {
                "execution_id": identity,
                "direction": row["direction"],
                "amount": row["amount"],
                "bank_fee": row["bank_fee"],
                "allocated_principal": principal,
                "settlement_principal": principal - assessed,
                "assessed_principal": assessed,
                "included": included,
            }
        )
        if included:
            totals[row["direction"] + "_total"] += row["amount"]
            totals["fee_total"] += row["bank_fee"]
            totals["assessed_debit_total"] += assessed
    parent = {
        "source_contract": bank_reconciliation.CONTRACT,
        "processing_policy": source["processing_policy"],
        "as_of_date": source["as_of_date"],
        "filings": deepcopy(source["filings"]),
        "transfers": transfers,
    }
    answer, child_trace = bank_reconciliation.calculate(parent)
    totals["settlement_net_outflow"] = (
        totals["debit_total"]
        - totals["credit_total"]
        - totals["fee_total"]
        - totals["assessed_debit_total"]
    )
    assert totals["settlement_net_outflow"] == answer["paid_total"] - answer["received_total"]
    answer["execution_reconciliations"] = reconciliations
    answer["bank_cash_totals"] = totals
    canonical = deepcopy(source)
    canonical["filings"].sort(key=lambda row: row["filing_id"])
    canonical["bank_executions"] = [deepcopy(executions[key]) for key in sorted(executions)]
    canonical["allocation_instructions"] = [
        deepcopy(instructions[key]) for key in sorted(instructions)
    ]
    trace = [
        {
            "rule_id": RULE_ID,
            "inputs": canonical,
            "output": {"bank_reconciliation_trace": child_trace, "result": deepcopy(answer)},
        }
    ]
    return deepcopy(answer), deepcopy(trace)
