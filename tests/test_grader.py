import json
from pathlib import Path

import pytest
import yaml

from grader import grade_batch, grade_task
from grader.core import read_json


def make_task(root: Path, gold=None, schema=None, task_id="sample", domain="D_extract"):
    gold = gold if gold is not None else {"amount": 100, "company": "Ａ B"}
    schema = schema or {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "amount": {"type": "integer"},
            "company": {"type": "string", "enum": ["Ａ B"]},
        },
        "required": ["amount", "company"],
        "additionalProperties": False,
    }
    task = root / domain / task_id
    task.mkdir(parents=True)
    (task / "task.yaml").write_text(
        yaml.safe_dump(
            {
                "task_id": task_id,
                "domain": domain,
                "answer_schema": schema,
            }
        ),
        encoding="utf-8",
    )
    (task / "gold.json").write_text(json.dumps(gold), encoding="utf-8")
    return task


def test_strings_normalize_in_grading_and_schema_enum(tmp_path):
    task = make_task(tmp_path)
    score = grade_task(task, {"amount": 100, "company": " a\tb\n "})
    assert score["exact_match"] == score["field_accuracy"] == 1
    assert score["schema_valid"]
    assert score["errors"] == []


@pytest.mark.parametrize("wrong", [True, 100.0, "100", 101, None])
def test_won_integers_are_exact_and_not_boolean_or_float(tmp_path, wrong):
    task = make_task(tmp_path)
    score = grade_task(task, {"amount": wrong, "company": "ab"})
    assert score["exact_match"] == 0
    assert score["correct_fields"] == 1
    if wrong != 101 or type(wrong) is not int:
        assert any(error["path"] == "$.amount" for error in score["errors"])


def test_extra_fields_invalidate_exact_match_but_preserve_field_accuracy(tmp_path):
    task = make_task(tmp_path)
    score = grade_task(task, {"amount": 100, "company": "ab", "extra": 7})
    assert score["exact_match"] == 0
    assert score["field_accuracy"] == 1
    assert not score["schema_valid"]
    assert any(error["validator"] == "additionalProperties" for error in score["errors"])


@pytest.mark.parametrize("answer", [{}, None, [], "", False])
def test_empty_and_nonobject_submissions_always_score_zero(tmp_path, answer):
    task = make_task(tmp_path)
    score = grade_task(task, answer)
    assert score["exact_match"] == score["field_accuracy"] == 0
    assert any(error["validator"] == "submission" for error in score["errors"])


def test_recursive_fields_missing_paths_and_empty_lists(tmp_path):
    gold = {"rows": [{"name": "Ａ", "amount": 4}, {"name": "Ｂ", "amount": 8}], "empty": []}
    schema = {
        "type": "object",
        "properties": {
            "rows": {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "amount": {"type": "integer"},
                    },
                    "required": ["name", "amount"],
                    "additionalProperties": False,
                },
            },
            "empty": {"type": "array", "maxItems": 0},
        },
        "required": ["rows", "empty"],
        "additionalProperties": False,
    }
    task = make_task(tmp_path, gold, schema)
    assert grade_task(task, gold)["total_fields"] == 5
    assert grade_task(task, {"rows": [], "empty": []})["correct_fields"] == 1
    assert grade_task(task, {"rows": {"0": {"name": "a", "amount": 4}}})["correct_fields"] == 0
    score = grade_task(task, {"rows": [{"name": "a", "amount": 4}]})
    assert score["correct_fields"] == 2
    assert score["field_accuracy"] == 0.4
    assert [field["path"] for field in score["field_results"]] == [
        "$.empty",
        "$.rows[0].amount",
        "$.rows[0].name",
        "$.rows[1].amount",
        "$.rows[1].name",
    ]


def test_missing_null_field_cannot_get_credit(tmp_path):
    task = make_task(
        tmp_path,
        {"x": None, "amount": 1},
        {
            "type": "object",
            "properties": {"x": {"type": "null"}, "amount": {"type": "integer"}},
            "required": ["x", "amount"],
            "additionalProperties": False,
        },
    )
    assert grade_task(task, {"amount": 1})["correct_fields"] == 1


def test_string_const_uses_same_normalization(tmp_path):
    task = make_task(
        tmp_path,
        {"text": "Ａ BC"},
        {
            "type": "object",
            "properties": {"text": {"type": "string", "const": "Ａ BC"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    )
    assert grade_task(task, {"text": "a\nbc"})["exact_match"] == 1


def test_batch_missing_malformed_and_flat_answers_remain_in_denominator(tmp_path):
    batch = tmp_path / "batch"
    make_task(batch, task_id="a", domain="A_yearend")
    make_task(batch, task_id="b", domain="B_payroll")
    make_task(batch, task_id="c", domain="B_payroll")
    answers = tmp_path / "answers"
    answers.mkdir()
    (answers / "a.json").write_text('{"amount":100,"company":"a b"}', encoding="utf-8")
    (answers / "b.json").write_text('{"amount":100,"amount":100}', encoding="utf-8")
    score = grade_batch(batch, answers)
    assert score["task_count"] == 3
    assert score["exact_match"] == pytest.approx(1 / 3)
    assert score["field_accuracy"] == pytest.approx(1 / 3)
    assert score["by_domain"]["A_yearend"]["exact_match"] == 1
    assert score["by_domain"]["B_payroll"]["exact_match"] == 0
    assert any("Duplicate JSON key" in error["message"] for error in score["tasks"][1]["errors"])


def test_nested_answer_takes_precedence(tmp_path):
    batch = tmp_path / "batch"
    make_task(batch)
    answers = tmp_path / "answers"
    (answers / "sample").mkdir(parents=True)
    (answers / "sample" / "answer.json").write_text('{"amount":100,"company":"ab"}')
    (answers / "sample.json").write_text("{}")
    assert grade_batch(batch, answers)["exact_match"] == 1


def test_duplicate_task_ids_are_rejected(tmp_path):
    batch = tmp_path / "batch"
    make_task(batch, task_id="same", domain="A_yearend")
    make_task(batch, task_id="same", domain="B_payroll")
    with pytest.raises(ValueError, match="Duplicate task_id"):
        grade_batch(batch, tmp_path / "answers")


def test_remote_schema_refs_cannot_trigger_network_resolution(tmp_path):
    task = make_task(tmp_path, schema={"$ref": "https://example.invalid/schema"})
    with pytest.raises(ValueError, match="document-local"):
        grade_task(task, {"amount": 100, "company": "ab"})


def test_json_nonfinite_numbers_are_rejected(tmp_path):
    answer = tmp_path / "answer.json"
    answer.write_text('{"amount": NaN}')
    with pytest.raises(ValueError, match="Non-finite"):
        read_json(answer)
