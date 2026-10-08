"""Read-only replay from either the staged pack or public audit directory.

Run from the repository root: PYTHONPATH=. .venv/bin/python PATH/replay_proof.py
"""

from pathlib import Path
import hashlib
import json

from KrRubberStamp.authoring import check_case, project_answer
from KrRubberStamp.registry import calculate
from render.authored import _prepare
from render.documents import restore_scenario

BASE = Path(__file__).resolve().parent


def read(name):
    return json.loads((BASE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def answer(case, facts=None):
    return project_answer(
        calculate(case["domain"], facts if facts is not None else case["facts"])[0],
        case["answer_fields"],
    )


manifest = read("proof_manifest.json")
for record in manifest["files"]:
    assert sha(BASE / record["path"]) == record["sha256"], record["path"]
cases = {case["case_id"]: case for case in read("post_cases.json")}
old = {case["case_id"]: case for case in read("original_cases.json")}
scope = read("post_scope.json")
for record in scope["records"]:
    case = cases[record["case_id"]]
    check_case(case)
    _prepare(case["facts"], case["documents"], case["domain"])
    assert answer(case) == record["requested_answer"]
for record in scope["changed_records"]:
    case = cases[record["case_id"]]
    if record["change_type"] == "minor_law":
        assert answer(case) == answer(old[record["case_id"]])
    else:
        assert answer(case) == record["independent_arithmetic"]["expected_requested"]
counterfactuals = read("post_counterfactuals.json")
for record in counterfactuals["records"]:
    case = cases[record["case_id"]]
    assert answer(case) == record["before_requested"]
    try:
        after = answer(case, record["changed_facts"])
        observed = "invariant" if after == record["before_requested"] else "change"
        assert after == record["after_requested"]
    except ValueError:
        observed = "reject"
    assert observed == record["expected"]
physical = read("post_physical_checks.json")
for record in physical["results"]:
    identity = record["case_id"]
    out = BASE / ("physical_post" if identity == "C272" else "physical") / identity
    edited = BASE / ("physical_post_cf" if identity == "C272" else "physical_cf") / identity
    assert restore_scenario(out) == cases[identity]["facts"]
    assert restore_scenario(edited) == record["after_recovered_facts"]
    assert answer(cases[identity], restore_scenario(out)) == record["before_requested"]
    assert answer(cases[identity], restore_scenario(edited)) == record["after_requested"]
    assert (out / "extraction_map.json").read_bytes() == (
        edited / "extraction_map.json"
    ).read_bytes()
    for path, expected in record["source_sha256"].items():
        assert sha(out / path) == expected
legal = read("post_legal_checks.json")
for record in legal["records"]:
    if record["kind"] == "individual_business_decline_return":
        assert record["quarter_tax_paid"] * 3 < record["previous_half_tax_paid"]
        assert cases[record["case_id"]]["facts"]["prepaid_assessed_vat"] == 0
    elif record["kind"] == "normal_july_simplified_transition":
        assert record["simplified_valid_from"] == "2025-07-01"
    else:
        assert record["filing_deadline_attested_in_source"]
print(
    json.dumps(
        {
            "cases": len(cases),
            "document_plans": scope["document_plans"],
            "changed_cases": len(scope["changed_records"]),
            "counterfactuals": counterfactuals["counterfactual_count"],
            "physical_cases": physical["case_count"],
            "physical_documents": physical["document_count"],
            "legal_premises": len(legal["records"]),
            "all_replayed_checks_passed": True,
        },
        ensure_ascii=False,
    )
)
