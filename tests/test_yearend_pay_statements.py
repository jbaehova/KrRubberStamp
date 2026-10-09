"""Independent certificate reconciliation and unchanged 2025 calculation tests."""

from copy import deepcopy

import pytest

from rules.a_yearend import engine, evidence
from rules.a_yearend.pay_statements import CONTRACT, RULE_ID, calculate


def statement(**changes):
    return {
        "statement_id": "CERT-A-1",
        "employer_id": "EMPLOYER-A",
        "employee_id": "WORKER-17",
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
        "revision": 1,
        "status": "issued",
        "gross_pay": 30_000_000,
        "non_taxable_pay": 1_000_000,
        "withheld_national_tax": 2_000_000,
        "withheld_local_tax": 120_000,
        **changes,
    }


def source():
    return {
        "source_contract": CONTRACT,
        "employee_id": "WORKER-17",
        "processing_policy": "합성 내부 확인 규약: 같은 사용자와 동일 기간의 발급본 중 최종 수정차수만 집계한다.",
        "calculation_facts": {
            "reference_year": 2025,
            "employee_name": "가상 근로자",
            "employee_age": 40,
            "employment_start": "2025-01-01",
            "employment_end": "2025-12-31",
            "deduction_choice": "standard",
        },
        "pay_statements": [
            statement(),
            statement(
                statement_id="CERT-B-1",
                employer_id="EMPLOYER-B",
                withheld_national_tax=3_000_000,
                withheld_local_tax=280_000,
            ),
        ],
    }


def test_independent_two_employer_receipt_and_separate_local_withholding():
    answer, trace = calculate(source())
    assert answer["employer_totals"] == [
        {
            "employer_id": "EMPLOYER-A",
            "gross_pay": 30_000_000,
            "non_taxable_pay": 1_000_000,
            "withheld_national_tax": 2_000_000,
            "withheld_local_tax": 120_000,
        },
        {
            "employer_id": "EMPLOYER-B",
            "gross_pay": 30_000_000,
            "non_taxable_pay": 1_000_000,
            "withheld_national_tax": 3_000_000,
            "withheld_local_tax": 280_000,
        },
    ]
    assert answer["annual_gross"] == 60_000_000
    assert answer["non_taxable"] == 2_000_000
    assert answer["paid_national_tax"] == 5_000_000
    assert answer["paid_local_tax"] == 400_000
    tax = answer["tax_calculation"]
    # Independently worked: 58m taxable salary, 12.65m earned-income
    # deduction, 45.35m income, 1.5m personal deduction, 43.85m tax base.
    assert tax["total_salary"] == 58_000_000
    assert tax["salary_deduction"] == 12_650_000
    assert tax["salary_income"] == 45_350_000
    assert tax["tax_base"] == 43_850_000
    assert tax["computed_tax"] == 5_317_500
    assert tax["employment_credit"] == 660_000
    assert tax["standard_credit"] == 130_000
    assert tax["final_national_tax"] == 4_527_500
    assert tax["final_local_tax"] == 452_750
    assert tax["settlement_national_tax"] == -472_500
    assert tax["settlement_local_tax"] == 52_750
    assert tax["settlement_total"] == -419_750
    assert answer["used_statement_ids"] == ["CERT-A-1", "CERT-B-1"]
    assert answer["excluded_statement_ids"] == []
    assert len(trace) == 1 and trace[0]["rule_id"] == RULE_ID
    assert trace[0]["output"] == answer


def test_highest_issued_correction_not_later_draft_and_other_employee():
    s = source()
    s["pay_statements"] += [
        statement(statement_id="CERT-A-2", revision=2, gross_pay=31_000_000),
        statement(statement_id="CERT-A-9", revision=9, status="draft", gross_pay=99_000_000),
        statement(statement_id="OTHER", employee_id="WORKER-99", revision=20),
    ]
    answer, _ = calculate(s)
    assert answer["annual_gross"] == 61_000_000
    assert answer["used_statement_ids"] == ["CERT-A-2", "CERT-B-1"]
    assert answer["excluded_statement_ids"] == ["CERT-A-1", "CERT-A-9", "OTHER"]


def test_exact_duplicate_counts_once_and_file_order_does_not_change_trace():
    s = source()
    s["pay_statements"].append(deepcopy(s["pay_statements"][0]))
    answer, trace = calculate(s)
    assert answer == calculate(source())[0]
    assert trace[0]["reconciliation"]["duplicate_statement_ids"] == ["CERT-A-1"]
    assert len(trace[0]["inputs"]["pay_statements"]) == 3
    s["pay_statements"].reverse()
    assert calculate(s) == (answer, trace)


@pytest.mark.parametrize(
    "field,value",
    [
        ("employer_id", "OTHER-EMPLOYER"),
        ("employee_id", "OTHER-WORKER"),
        ("gross_pay", 30_000_001),
        ("period_end", "2025-12-30"),
    ],
)
def test_conflicting_statement_identity_rejected(field, value):
    s = source()
    s["pay_statements"].append(statement(**{field: value}))
    with pytest.raises(ValueError, match="Conflicting"):
        calculate(s)


def test_competing_distinct_highest_revision_rejected():
    s = source()
    s["pay_statements"].append(statement(statement_id="COMPETING"))
    with pytest.raises(ValueError, match="Ambiguous highest"):
        calculate(s)


def test_lower_issued_revision_tie_is_not_a_highest_revision_ambiguity():
    s = source()
    s["pay_statements"] += [
        statement(statement_id="LOWER-TIE"),
        statement(statement_id="SELECTED", revision=2),
    ]
    assert calculate(s)[0]["used_statement_ids"] == ["CERT-B-1", "SELECTED"]


def test_adjacent_periods_sum_but_same_day_overlap_rejected():
    s = source()
    s["pay_statements"] = [
        statement(period_end="2025-06-30"),
        statement(statement_id="SECOND-HALF", period_start="2025-07-01"),
    ]
    assert calculate(s)[0]["annual_gross"] == 60_000_000
    s["pay_statements"][1]["period_start"] = "2025-06-30"
    with pytest.raises(ValueError, match="overlap"):
        calculate(s)


def test_only_counted_periods_must_fit_declared_employment_boundaries():
    s = source()
    s["calculation_facts"]["employment_start"] = "2025-02-01"
    s["calculation_facts"]["employment_end"] = "2025-11-30"
    for row in s["pay_statements"]:
        row["period_start"], row["period_end"] = "2025-02-01", "2025-11-30"
    s["pay_statements"].append(statement(statement_id="UNCOUNTED", status="draft"))
    assert calculate(s)[0]["annual_gross"] == 60_000_000
    s["pay_statements"][0]["period_start"] = "2025-01-31"
    with pytest.raises(ValueError, match="outside employment"):
        calculate(s)


@pytest.mark.parametrize(
    "field,value",
    [
        ("revision", True),
        ("revision", 1.0),
        ("revision", 0),
        ("gross_pay", True),
        ("gross_pay", 30_000_000.0),
        ("gross_pay", -1),
        ("non_taxable_pay", 30_000_001),
        ("withheld_national_tax", False),
        ("withheld_local_tax", 1.5),
        ("period_start", "20250101"),
        ("period_start", "2024-12-31"),
        ("period_end", "2026-01-01"),
        ("period_start", "2025-02-30"),
        ("period_start", "2025-12-31"),
        ("status", "cancelled"),
        ("statement_id", " "),
        ("employee_id", 17),
        ("employer_id", ""),
    ],
)
def test_strict_statement_validation(field, value):
    s = source()
    if field == "period_start" and value == "2025-12-31":
        s["pay_statements"][0]["period_end"] = "2025-12-30"
    s["pay_statements"][0][field] = value
    with pytest.raises(ValueError):
        calculate(s)


def test_bool_duplicate_cannot_compare_equal_to_integer_content():
    s = source()
    s["pay_statements"].append(statement(revision=True))
    with pytest.raises(ValueError, match="integer"):
        calculate(s)


@pytest.mark.parametrize(
    "field", ["annual_gross", "non_taxable", "paid_national_tax", "paid_local_tax"]
)
def test_compiled_annual_amounts_cannot_leak_into_source_facts(field):
    s = source()
    s["calculation_facts"][field] = 0
    with pytest.raises(ValueError, match="compiled annual"):
        calculate(s)


@pytest.mark.parametrize("contract", [CONTRACT, "unknown"])
def test_nested_or_unknown_calculation_contract_rejected(contract):
    s = source()
    s["calculation_facts"]["source_contract"] = contract
    with pytest.raises(ValueError, match="Only plain"):
        calculate(s)


@pytest.mark.parametrize(
    "field,value",
    [
        ("reference_year", 2025.0),
        ("reference_year", 2026),
        ("employee_name", ""),
        ("employee_age", True),
        ("employment_start", "2024-01-01"),
    ],
)
def test_required_calculation_identity_and_scope(field, value):
    s = source()
    s["calculation_facts"][field] = value
    with pytest.raises(ValueError):
        calculate(s)


@pytest.mark.parametrize(
    "rows", [[], [statement(status="draft")], [statement(employee_id="OTHER")]]
)
def test_at_least_one_issued_target_statement_required(rows):
    s = source()
    s["pay_statements"] = rows
    with pytest.raises(ValueError):
        calculate(s)


def test_missing_and_unknown_fields_are_rejected():
    s = source()
    s["pay_statements"][0]["unexpected"] = 1
    with pytest.raises(ValueError, match="fields"):
        calculate(s)
    s = source()
    del s["pay_statements"][0]["gross_pay"]
    with pytest.raises(ValueError, match="fields"):
        calculate(s)
    s = source()
    s["unused"] = True
    with pytest.raises(ValueError, match="fields"):
        calculate(s)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_contract", "unknown"),
        ("employee_id", ""),
        ("processing_policy", " "),
        ("calculation_facts", []),
        ("pay_statements", {}),
        ("pay_statements", [None]),
    ],
)
def test_invalid_source_contract_shape(field, value):
    s = source()
    s[field] = value
    with pytest.raises(ValueError):
        calculate(s)


def test_non_string_status_and_reversed_employment_rejected():
    s = source()
    s["pay_statements"][0]["status"] = []
    with pytest.raises(ValueError):
        calculate(s)
    s = source()
    s["calculation_facts"].update(
        {"employment_start": "2025-12-31", "employment_end": "2025-01-01"}
    )
    with pytest.raises(ValueError, match="reversed"):
        calculate(s)


def test_zero_and_fully_non_taxable_certificate_boundaries():
    s = source()
    s["pay_statements"] = [
        statement(gross_pay=0, non_taxable_pay=0, withheld_national_tax=0, withheld_local_tax=0)
    ]
    answer, _ = calculate(s)
    assert answer["annual_gross"] == answer["non_taxable"] == 0
    assert answer["tax_calculation"]["settlement_total"] == 0
    s["pay_statements"][0].update(gross_pay=1_000_000, non_taxable_pay=1_000_000)
    answer, _ = calculate(s)
    assert answer["annual_gross"] == answer["non_taxable"] == 1_000_000
    assert answer["tax_calculation"]["total_salary"] == 0


def test_supported_receipt_contract_dispatch_and_semantic_array_order():
    s = source()
    s["calculation_facts"].update(
        {
            "source_contract": evidence.CONTRACT,
            "deduction_choice": "itemized",
            "medical": [
                {
                    "person_id": "self",
                    "date": "2025-02-01",
                    "kind": "ordinary",
                    "amount": 2_000_000,
                    "treatment_purpose": "therapeutic",
                },
                {
                    "person_id": "self",
                    "date": "2025-03-01",
                    "kind": "ordinary",
                    "amount": 5_000_000,
                    "treatment_purpose": "cosmetic",
                },
            ],
        }
    )
    answer, trace = calculate(s)
    assert answer["tax_calculation"]["medical_credit"] == 39_000
    assert trace[0]["tax_derivations"][0]["rule_id"] == evidence.RULE_ID
    assert trace[0]["inputs"]["calculation_facts"]["medical"] == s["calculation_facts"]["medical"]
    compiled = deepcopy(s["calculation_facts"])
    compiled.update(
        {
            key: answer[key]
            for key in ("annual_gross", "non_taxable", "paid_national_tax", "paid_local_tax")
        }
    )
    normalized = evidence.interpret(compiled)
    expected, nested_trace = engine.calculate(normalized)
    assert answer["tax_calculation"] == expected
    assert trace[0]["tax_derivations"] == [
        evidence.derivation_trace(compiled, normalized),
        *nested_trace,
    ]


def test_source_immutable_and_returned_trace_does_not_alias_caller():
    s = source()
    before = deepcopy(s)
    answer, trace = calculate(s)
    assert s == before
    trace[0]["inputs"]["calculation_facts"]["employee_name"] = "changed"
    trace[0]["output"]["employer_totals"][0]["gross_pay"] = 0
    assert s == before
    assert answer["employer_totals"][0]["gross_pay"] == 30_000_000


@pytest.mark.parametrize("fmt", ["pdf", "xlsx", "hwpx"])
def test_public_registry_restores_actual_nested_documents(tmp_path, fmt):
    from KrRubberStamp.registry import calculate as registered_calculate
    from render.authored import render_authored
    from render.documents import restore_scenario

    facts = source()
    documents = [
        {
            "filename": "원본." + fmt,
            "format": fmt,
            "title": "원자료 연결 통합 검산",
            "note": "합성 원자료의 실제 기재를 복원하여 대조합니다.",
            "fields": list(facts),
        }
    ]
    render_authored(facts, tmp_path, "A_yearend", documents)
    restored = restore_scenario(tmp_path)
    assert restored == facts
    answer, trace = registered_calculate("A_yearend", restored)
    assert (
        answer["annual_gross"] == 60_000_000
        and answer["tax_calculation"]["settlement_total"] == -419_750
    )
    assert trace[0]["rule_id"] == RULE_ID
    if fmt == "xlsx":
        import json
        from openpyxl import load_workbook

        mapping = json.loads((tmp_path / "extraction_map.json").read_text())
        workbook = load_workbook(tmp_path / "inputs/원본.xlsx")
        for path, amount in [(["pay_statements", 0, "withheld_local_tax"], 220000)]:
            record = next(row for row in mapping["records"] if row["path"] == path)
            selector = record["selector"]
            workbook[selector["sheet"]][selector["cell"]] = amount
        workbook.save(tmp_path / "inputs/원본.xlsx")
        workbook.close()
        after, _ = registered_calculate("A_yearend", restore_scenario(tmp_path))
        assert (
            after["paid_national_tax"] == 5_000_000
            and after["tax_calculation"]["settlement_total"] == -519_750
        )
