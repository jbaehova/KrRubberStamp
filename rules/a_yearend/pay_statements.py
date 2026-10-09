"""Compile submitted 2025 withholding certificates under a private policy.

Revision selection is a synthetic document verification contract, not a new
government tax rule. Tax calculations delegate to the existing year-end engine.
"""

from copy import deepcopy
from datetime import date

from . import engine, evidence

CONTRACT = "yearend_pay_statement_v1"
RULE_ID = "A_PAY_STATEMENT_RECONCILIATION"

_SOURCE_FIELDS = {
    "source_contract",
    "employee_id",
    "processing_policy",
    "calculation_facts",
    "pay_statements",
}
_STATEMENT_FIELDS = {
    "statement_id",
    "employer_id",
    "employee_id",
    "period_start",
    "period_end",
    "revision",
    "status",
    "gross_pay",
    "non_taxable_pay",
    "withheld_national_tax",
    "withheld_local_tax",
}
_AMOUNTS = ("gross_pay", "non_taxable_pay", "withheld_national_tax", "withheld_local_tax")
_ANNUAL_FIELDS = ("annual_gross", "non_taxable", "paid_national_tax", "paid_local_tax")


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Pay statements require nonempty {field}")
    return value


def _date(value, field):
    _text(value, field)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Pay statements require an ISO date for {field}") from exc
    if parsed.isoformat() != value or parsed.year != 2025:
        raise ValueError(f"Pay statements require a 2025 ISO date for {field}")
    return value


def _integer(value, field, *, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError(f"Pay statements require an integer amount or revision for {field}")
    return value


def _validate_statement(row):
    if not isinstance(row, dict) or set(row) != _STATEMENT_FIELDS:
        raise ValueError("Pay statement fields are missing or unsupported")
    for field in ("statement_id", "employer_id", "employee_id"):
        _text(row[field], field)
    start, end = _date(row["period_start"], "period_start"), _date(row["period_end"], "period_end")
    if start > end:
        raise ValueError("Pay statement period is reversed")
    _integer(row["revision"], "revision", positive=True)
    if _text(row["status"], "status") not in {"issued", "draft"}:
        raise ValueError("Pay statement status must be issued or draft")
    for field in _AMOUNTS:
        _integer(row[field], field)
    if row["non_taxable_pay"] > row["gross_pay"]:
        raise ValueError("Pay statement non-taxable pay exceeds gross pay")


def calculate(source: dict) -> tuple[dict, list[dict]]:
    """Return employer/source totals and the unchanged nested A tax answer."""
    if not isinstance(source, dict) or set(source) != _SOURCE_FIELDS:
        raise ValueError("Pay statement source fields are missing or unsupported")
    if source["source_contract"] != CONTRACT:
        raise ValueError("Unknown pay statement contract")
    target = _text(source["employee_id"], "employee_id")
    _text(source["processing_policy"], "processing_policy")
    facts = source["calculation_facts"]
    if not isinstance(facts, dict) or not facts:
        raise ValueError("Pay statements require calculation_facts")
    if type(facts.get("reference_year")) is not int or facts["reference_year"] != 2025:
        raise ValueError("Pay statement calculation facts must declare 2025")
    if set(facts) & set(_ANNUAL_FIELDS):
        raise ValueError("Pay statement calculation facts expose compiled annual amounts")
    if "source_contract" in facts and facts["source_contract"] != evidence.CONTRACT:
        raise ValueError("Only plain or yearend_evidence_v1 calculation facts are supported")
    _text(facts.get("employee_name"), "employee_name")
    if type(facts.get("employee_age")) is not int or facts["employee_age"] < 0:
        raise ValueError("Pay statement calculation facts require an integer employee_age")
    employment_start = _date(facts.get("employment_start"), "employment_start")
    employment_end = _date(facts.get("employment_end"), "employment_end")
    if employment_start > employment_end:
        raise ValueError("Employment interval is reversed")
    rows = source["pay_statements"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Pay statements must be a nonempty list")
    records, duplicates = {}, set()
    for row in rows:
        _validate_statement(row)
        identity = row["statement_id"]
        if identity in records:
            # All fields have already passed exact scalar type checks. In
            # particular True cannot compare equal to a previously accepted 1.
            if records[identity] != row:
                raise ValueError("Conflicting pay statement identity")
            duplicates.add(identity)
        else:
            records[identity] = deepcopy(row)
    groups = {}
    for row in records.values():
        if row["employee_id"] == target and row["status"] == "issued":
            key = (row["employer_id"], row["period_start"], row["period_end"])
            groups.setdefault(key, []).append(row)
    selected = []
    for group in groups.values():
        highest = max(row["revision"] for row in group)
        latest = [row for row in group if row["revision"] == highest]
        if len(latest) != 1:
            raise ValueError("Ambiguous highest issued pay statement revision")
        selected.append(latest[0])
    if not selected:
        raise ValueError("At least one issued target employee statement is required")
    selected.sort(key=lambda row: (row["employer_id"], row["period_start"], row["period_end"]))
    previous = {}
    employer_totals = {}
    for row in selected:
        if not employment_start <= row["period_start"] <= row["period_end"] <= employment_end:
            raise ValueError("Counted pay statement period is outside employment")
        employer = row["employer_id"]
        if employer in previous and row["period_start"] <= previous[employer]:
            raise ValueError("Selected same-employer pay statement periods overlap")
        previous[employer] = row["period_end"]
        total = employer_totals.setdefault(
            employer, {"employer_id": employer, **dict.fromkeys(_AMOUNTS, 0)}
        )
        for field in _AMOUNTS:
            total[field] += row[field]
    totals = [employer_totals[identity] for identity in sorted(employer_totals)]
    annual = {
        destination: sum(row[field] for row in totals)
        for destination, field in zip(_ANNUAL_FIELDS, _AMOUNTS, strict=True)
    }
    compiled = deepcopy(facts)
    compiled.update(annual)
    if compiled.get("source_contract") == evidence.CONTRACT:
        normalized = evidence.interpret(compiled)
        tax_answer, tax_trace = engine.calculate(normalized)
        tax_trace = [evidence.derivation_trace(compiled, normalized), *tax_trace]
    else:
        tax_answer, tax_trace = engine.calculate(compiled)
    used = sorted(row["statement_id"] for row in selected)
    excluded = sorted(set(records) - set(used))
    answer = {
        "employer_totals": totals,
        **annual,
        "tax_calculation": tax_answer,
        "used_statement_ids": used,
        "excluded_statement_ids": excluded,
    }
    canonical = deepcopy(source)
    # Retain duplicate occurrences as full submitted source while making file
    # order immaterial. Conflicting identities have already been rejected.
    canonical["pay_statements"].sort(key=lambda row: row["statement_id"])
    trace = [
        {
            "rule_id": RULE_ID,
            "inputs": canonical,
            "reconciliation": {
                "duplicate_statement_ids": sorted(duplicates),
                "used_statement_ids": used,
                "excluded_statement_ids": excluded,
                "employer_totals": deepcopy(totals),
                "annual_source_amounts": annual,
            },
            "tax_derivations": tax_trace,
            "output": deepcopy(answer),
        }
    ]
    return answer, trace
