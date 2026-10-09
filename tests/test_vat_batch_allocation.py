"""Independent literal expectations and conservation for actual batch payment sources."""

from copy import deepcopy
from pathlib import Path
import yaml
import pytest
from rules.c_vat.batch_allocation import calculate, CONTRACT, RULE_ID

EXAMPLES = yaml.safe_load(
    (Path(__file__).parent / "fixtures/vat_batch_allocation.yaml").read_text()
)


def source():
    return deepcopy(EXAMPLES[0]["facts"])


@pytest.mark.parametrize("example", EXAMPLES)
def test_whole_literal_independent_examples(example):
    facts = deepcopy(example["facts"])
    answer, trace = calculate(facts)
    assert answer == example["manual_expected"]
    assert facts == example["facts"]
    assert trace[0]["rule_id"] == RULE_ID
    assert (
        trace[0]["output"]["bank_reconciliation_trace"][0]["rule_id"] == "C_VAT_BANK_RECONCILIATION"
    )


def test_fee_changes_gross_bank_cash_but_no_tax_principal_or_balance():
    facts = source()
    before, _ = calculate(facts)
    facts["bank_executions"][0]["bank_fee"] += 100
    facts["bank_executions"][0]["amount"] += 100
    after, _ = calculate(facts)
    assert after["registration_settlements"] == before["registration_settlements"]
    assert after["filing_calculations"] == before["filing_calculations"]
    assert after["bank_cash_totals"]["fee_total"] == before["bank_cash_totals"]["fee_total"] + 100
    assert (
        after["bank_cash_totals"]["settlement_net_outflow"]
        == before["bank_cash_totals"]["settlement_net_outflow"]
    )


def test_fixed_execution_total_different_explicit_allocation_changes_two_balances():
    facts = source()
    before, _ = calculate(facts)
    facts["allocation_instructions"][0]["amount"] -= 5000
    facts["allocation_instructions"][1]["amount"] += 5000
    after, _ = calculate(facts)
    assert after["bank_cash_totals"] == before["bank_cash_totals"]
    assert after["balance_total"] == before["balance_total"]
    assert sorted(r["balance"] for r in after["registration_settlements"]) == [-5000, 5000]


@pytest.mark.parametrize("status,day", [("planned", "2026-07-27"), ("executed", "2026-08-11")])
def test_whole_execution_status_and_cutoff_propagate_to_all_instructions(status, day):
    facts = source()
    facts["bank_executions"][0].update(status=status, date=day)
    answer, _ = calculate(facts)
    assert answer["paid_total"] == 0
    assert answer["balance_total"] == 171400
    assert answer["bank_cash_totals"]["debit_total"] == 0
    assert answer["execution_reconciliations"][0]["allocated_principal"] == 171400
    assert answer["execution_reconciliations"][0]["included"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("bank_fee", True),
        ("amount", -1),
        ("status", "draft"),
        ("direction", "withdraw"),
        ("date", "2026-7-27"),
    ],
)
def test_malformed_execution_is_rejected_even_when_planned(field, value):
    facts = source()
    facts["bank_executions"][0]["status"] = "planned"
    facts["bank_executions"][0][field] = value
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize(
    "field,value",
    [
        ("amount", True),
        ("amount", 0),
        ("amount", -5),
        ("kind", "settlement_refund"),
        ("filing_id", "missing"),
        ("registration_id", "wrong"),
        ("execution_id", "missing"),
    ],
)
def test_invalid_instruction_is_rejected_even_when_future(field, value):
    facts = source()
    facts["bank_executions"][0]["date"] = "2026-09-01"
    facts["allocation_instructions"][0][field] = value
    with pytest.raises(ValueError):
        calculate(facts)


@pytest.mark.parametrize("group", ["bank_executions", "allocation_instructions"])
def test_duplicate_original_id_requires_no_arbitrary_priority(group):
    facts = source()
    facts[group].append(deepcopy(facts[group][0]))
    with pytest.raises(ValueError):
        calculate(facts)


def test_incomplete_or_inconsistent_bank_composition_is_not_inferred():
    for mutation in ("amount", "remove", "empty"):
        facts = source()
        if mutation == "amount":
            facts["bank_executions"][0]["amount"] += 1
        elif mutation == "remove":
            facts["allocation_instructions"].pop()
        else:
            facts["allocation_instructions"] = []
        with pytest.raises(ValueError):
            calculate(facts)


def test_refund_execution_cannot_have_fee_or_debit_purpose():
    facts = source()
    facts["bank_executions"][0]["direction"] = "credit"
    with pytest.raises(ValueError):
        calculate(facts)
    facts["bank_executions"][0]["bank_fee"] = 0
    with pytest.raises(ValueError):
        calculate(facts)


def test_sorted_source_permutations_and_result_mutations_do_not_alias():
    facts = deepcopy(EXAMPLES[1]["facts"])
    before, trace_before = calculate(facts)
    for group in ("filings", "bank_executions", "allocation_instructions"):
        facts[group].reverse()
    answer, trace = calculate(facts)
    assert answer == before and trace == trace_before
    answer["bank_cash_totals"]["fee_total"] = 999
    assert trace[0]["output"]["result"] == before
    trace[0]["inputs"]["bank_executions"][0]["amount"] = 0
    assert facts["bank_executions"][0]["amount"] > 0


@pytest.mark.parametrize(
    "group,maximum", [("bank_executions", 20), ("allocation_instructions", 60)]
)
def test_bounded_finite_source_rows(group, maximum):
    facts = source()
    facts[group] = [deepcopy(facts[group][0]) for _ in range(maximum + 1)]
    with pytest.raises(ValueError):
        calculate(facts)


def test_unknown_top_field_nested_parent_and_precomputed_child_decision_rejected():
    facts = source()
    facts["balance_total"] = 0
    with pytest.raises(ValueError):
        calculate(facts)
    facts = source()
    facts["filings"][0]["facts"]["source_contract"] = CONTRACT
    with pytest.raises(ValueError):
        calculate(facts)
    facts = source()
    facts["filings"][0]["facts"]["payable_vat"] = 100000
    with pytest.raises(ValueError):
        calculate(facts)


def test_one_unused_execution_and_same_taxpayer_two_filings_rejected():
    facts = source()
    facts["bank_executions"].append({**facts["bank_executions"][0], "execution_id": "unused"})
    with pytest.raises(ValueError):
        calculate(facts)
    facts = source()
    facts["filings"][1]["taxpayer_id"] = facts["filings"][0]["taxpayer_id"]
    with pytest.raises(ValueError):
        calculate(facts)


def test_actual_refund_and_assessment_within_complete_batch_conserve_cash():
    facts = source()
    facts["filings"][0]["facts"]["prepaid_assessed_vat"] = 500000
    facts["filings"][0]["facts"]["scope_note"] = (
        "적법한 고지50만원을 이미 신고에 반영한다. 별도 정산 환급과 원금은 원본 실행에서 확인한다."
    )
    eid = facts["bank_executions"][0]["execution_id"]
    fid = facts["filings"][0]["filing_id"]
    reg = facts["filings"][0]["registration_id"]
    facts["bank_executions"][0]["amount"] += 500000
    facts["allocation_instructions"].append(
        {
            "instruction_id": "assessed",
            "execution_id": eid,
            "filing_id": fid,
            "registration_id": reg,
            "kind": "assessed_prepayment",
            "amount": 500000,
        }
    )
    facts["bank_executions"].append(
        {
            "execution_id": "refund",
            "date": "2026-08-09",
            "status": "executed",
            "direction": "credit",
            "amount": 500000,
            "bank_fee": 0,
        }
    )
    facts["allocation_instructions"].append(
        {
            "instruction_id": "return",
            "execution_id": "refund",
            "filing_id": fid,
            "registration_id": reg,
            "kind": "settlement_refund",
            "amount": 500000,
        }
    )
    answer, _ = calculate(facts)
    assert answer["paid_total"] == 171400
    assert answer["received_total"] == 500000
    assert answer["balance_total"] == 0
    assert answer["bank_cash_totals"] == {
        "debit_total": 671900,
        "credit_total": 500000,
        "fee_total": 500,
        "assessed_debit_total": 500000,
        "settlement_net_outflow": -328600,
    }


@pytest.mark.parametrize("field", ["filings", "bank_executions", "allocation_instructions"])
def test_unknown_or_missing_row_fields_are_rejected(field):
    facts = source()
    facts[field][0]["unexpected"] = 1
    with pytest.raises(ValueError):
        calculate(facts)
    facts = source()
    facts[field][0].pop(next(iter(facts[field][0])))
    with pytest.raises(ValueError):
        calculate(facts)
