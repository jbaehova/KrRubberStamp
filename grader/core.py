"""Exact answer grading. No model or heuristic judge is involved."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, ValidationError, validators

from rules.common import normalize_text

_MISSING = object()
_TASK_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


def _equal(expected: Any, actual: Any) -> bool:
    """Normalize strings, but never equate booleans, floats, and won integers."""
    if isinstance(expected, str) and isinstance(actual, str):
        return normalize_text(expected) == normalize_text(actual)
    if type(expected) is not type(actual):
        return False
    if isinstance(expected, dict):
        return expected.keys() == actual.keys() and all(
            _equal(value, actual[key]) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return len(expected) == len(actual) and all(
            _equal(left, right) for left, right in zip(expected, actual, strict=True)
        )
    if isinstance(expected, float) and not math.isfinite(expected):
        return False
    return expected == actual


def _normalized_enum(validator, values, instance, schema):
    if not any(_equal(value, instance) for value in values):
        yield ValidationError("Value is outside the allowed enum after string normalization")


def _normalized_const(validator, value, instance, schema):
    if not _equal(value, instance):
        yield ValidationError("Value differs from const after string normalization")


_types = Draft202012Validator.TYPE_CHECKER.redefine(
    "integer", lambda checker, value: type(value) is int
).redefine(
    "number",
    lambda checker, value: type(value) is int or (type(value) is float and math.isfinite(value)),
)
AnswerValidator = validators.extend(
    Draft202012Validator,
    validators={"enum": _normalized_enum, "const": _normalized_const},
    type_checker=_types,
)


def _path(parts: tuple[Any, ...] | list[Any]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(part)):
            result += f".{part}"
        else:
            result += f"[{json.dumps(str(part), ensure_ascii=False)}]"
    return result


def _leaves(value: Any, path: tuple[Any, ...] = ()):
    # Empty containers are fields too. A missing path must never receive credit.
    if isinstance(value, dict) and value:
        for key in sorted(value):
            yield from _leaves(value[key], (*path, key))
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from _leaves(item, (*path, index))
    else:
        yield path, value


def _lookup(value: Any, path: tuple[Any, ...]) -> Any:
    for part in path:
        if isinstance(part, int):
            if not isinstance(value, list) or not 0 <= part < len(value):
                return _MISSING
        elif not isinstance(value, dict) or part not in value:
            return _MISSING
        value = value[part]
    return value


def parse_json(content: str | bytes) -> Any:
    """Parse JSON while rejecting non-JSON numbers and duplicate object keys."""

    def bad_constant(value: str):
        raise ValueError(f"Non-finite number is not valid JSON: {value}")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(
        content,
        parse_constant=bad_constant,
        object_pairs_hook=unique_object,
    )


def read_json(path: Path) -> Any:
    return parse_json(path.read_text(encoding="utf-8"))


def task_metadata(task_dir: Path) -> dict:
    metadata = yaml.safe_load((Path(task_dir) / "task.yaml").read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError(f"Invalid task metadata: {task_dir}")
    task_id = metadata.get("task_id")
    if not isinstance(task_id, str) or not _TASK_ID.fullmatch(task_id):
        raise ValueError("task_id must be a safe ASCII file name")
    if not isinstance(metadata.get("domain"), str):
        raise ValueError(f"Task {task_id} has no domain")
    if not isinstance(metadata.get("answer_schema"), dict):
        raise ValueError(f"Task {task_id} has no answer_schema")
    Draft202012Validator.check_schema(metadata["answer_schema"])

    # Schema validation must remain local and deterministic.
    def reject_remote_refs(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"$ref", "$dynamicRef"} and (
                    not isinstance(child, str) or not child.startswith("#")
                ):
                    raise ValueError("Answer schemas may only use document-local references")
                reject_remote_refs(child)
        elif isinstance(value, list):
            for child in value:
                reject_remote_refs(child)

    reject_remote_refs(metadata["answer_schema"])
    return metadata


def task_directories(batch_dir: Path) -> list[Path]:
    """Enumerate the documented batch/domain/task/task.yaml layout only."""
    return [path.parent for path in sorted(Path(batch_dir).glob("*/*/task.yaml"))]


def grade_task(task_dir: Path, answer: dict) -> dict:
    """Score gold leaf fields and exact full-object agreement independently.

    Strings use NFKC, whitespace removal, and case folding, including enum/const
    schema checks. Won integer fields require Python/JSON integers, never bools
    or integral floats. Invalid schema or extra fields always prevent exact match.
    """
    task_dir = Path(task_dir)
    metadata = task_metadata(task_dir)
    gold = read_json(task_dir / "gold.json")
    errors = []
    submitted = isinstance(answer, dict) and bool(answer)
    if not submitted:
        errors.append(
            {"path": "$", "validator": "submission", "message": "Empty or non-object answer"}
        )
    validation_errors = sorted(
        AnswerValidator(metadata["answer_schema"]).iter_errors(answer),
        key=lambda error: (_path(list(error.absolute_path)), str(error.validator), error.message),
    )
    for error in validation_errors:
        errors.append(
            {
                "path": _path(list(error.absolute_path)),
                "validator": str(error.validator),
                "message": error.message,
            }
        )
    field_results = []
    for path, expected in _leaves(gold):
        actual = _lookup(answer, path)
        correct = bool(submitted and actual is not _MISSING and _equal(expected, actual))
        field_results.append({"path": _path(path), "correct": correct})
    correct_fields = sum(field["correct"] for field in field_results)
    total_fields = len(field_results)
    return {
        "task_id": metadata["task_id"],
        "domain": metadata["domain"],
        "field_accuracy": correct_fields / total_fields if total_fields else 0.0,
        "exact_match": int(submitted and not errors and _equal(gold, answer)),
        "correct_fields": correct_fields,
        "total_fields": total_fields,
        "schema_valid": not validation_errors,
        "errors": errors,
        "field_results": field_results,
    }


def _aggregate(scores: list[dict]) -> dict:
    total_fields = sum(score["total_fields"] for score in scores)
    correct_fields = sum(score["correct_fields"] for score in scores)
    return {
        "task_count": len(scores),
        "exact_match": sum(score["exact_match"] for score in scores) / len(scores)
        if scores
        else 0.0,
        "field_accuracy": correct_fields / total_fields if total_fields else 0.0,
        "correct_fields": correct_fields,
        "total_fields": total_fields,
    }


def grade_batch(batch_dir: Path, answers_dir: Path) -> dict:
    """Grade <answers>/<task_id>/answer.json or <answers>/<task_id>.json.

    The documented nested form wins if both exist. Missing or malformed answers
    remain in the denominator and receive zero credit. Field accuracy is micro
    averaged; exact match is the task-level rate and primary benchmark metric.
    """
    answers_dir = Path(answers_dir)
    scores = []
    seen = set()
    for task_dir in task_directories(batch_dir):
        metadata = task_metadata(task_dir)
        task_id = metadata["task_id"]
        if task_id in seen:
            raise ValueError(f"Duplicate task_id in batch: {task_id}")
        seen.add(task_id)
        answer_path = answers_dir / task_id / "answer.json"
        if not answer_path.is_file():
            answer_path = answers_dir / f"{task_id}.json"
        load_error = None
        try:
            answer = read_json(answer_path)
        except (OSError, UnicodeError, ValueError) as error:
            answer = {}
            load_error = str(error)
        score = grade_task(task_dir, answer)
        if load_error:
            score["errors"].insert(
                0,
                {
                    "path": "$",
                    "validator": "answer_file",
                    "message": load_error,
                },
            )
        scores.append(score)
    domains = sorted({score["domain"] for score in scores})
    return {
        **_aggregate(scores),
        "by_domain": {
            domain: _aggregate([score for score in scores if score["domain"] == domain])
            for domain in domains
        },
        "tasks": scores,
    }
