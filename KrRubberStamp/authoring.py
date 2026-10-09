"""Build individually written cases without generating their facts or wording."""

from collections import Counter
from pathlib import Path
import json
import re
import shutil
import tempfile
import yaml

from .io import write_json
from .registry import DOMAINS, PERIODS, calculate
from .tasks import canary_for, make_schema, scenario_hash

AUTHORIZED_BATCHES = (1, 2)


def check_batch(batch):
    if type(batch) is not int or batch not in AUTHORIZED_BATCHES:
        raise ValueError("Select one of the two authorized 1,200-case batches")


def authored_root():
    checkout = Path(__file__).resolve().parents[1] / "authored"
    return checkout if checkout.is_dir() else Path(__file__).parent / "resources/authored"


def check_case(case):
    required = {
        "case_id",
        "domain",
        "difficulty",
        "title",
        "instruction",
        "work_goal",
        "design_rationale",
        "exceptions",
        "facts",
        "documents",
        "answer_fields",
    }
    if not isinstance(case, dict) or required - case.keys():
        raise ValueError(f"Authored case lacks fields: {required - case.keys()}")
    if case["domain"] not in DOMAINS or not re.fullmatch(r"[ABCD][0-9]{3,}", case["case_id"]):
        raise ValueError("Invalid authored identity")
    if case["case_id"][0] != case["domain"][0]:
        raise ValueError("Case ID and domain disagree")
    difficulty = case["difficulty"]
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Invalid authored difficulty")
    for key in ("title", "instruction", "work_goal", "design_rationale"):
        if not isinstance(case[key], str) or not case[key].strip():
            raise ValueError(f"Missing independently written {key}")
        if "·" in case[key] or "—" in case[key]:
            raise ValueError(f"Prohibited punctuation in {key}")
    exceptions = case["exceptions"]
    if not isinstance(exceptions, list) or any(not isinstance(x, str) or not x for x in exceptions):
        raise ValueError("Invalid authored exceptions")
    if (
        (difficulty == "easy" and exceptions)
        or (difficulty == "medium" and len(exceptions) != 1)
        or (difficulty == "hard" and len(exceptions) < 2)
    ):
        raise ValueError("Authored exception count does not match difficulty")
    count = len(case["documents"])
    if not (
        1 <= count <= 3
        if difficulty == "easy"
        else 4 <= count <= 8
        if difficulty == "medium"
        else count >= 9
    ):
        raise ValueError("Authored document count does not match difficulty")
    if not isinstance(case["facts"], dict) or not case["facts"]:
        raise ValueError("Authored facts must be a literal object")
    if {"seed", "scenario_seed", "generation_seed", "exceptions"} & case["facts"].keys():
        raise ValueError("Seed and editorial exception metadata do not belong in evidence")
    answer, _ = calculate(case["domain"], case["facts"])
    project_answer(answer, case["answer_fields"])
    return case


def project_answer(answer, fields):
    if (
        not isinstance(fields, list)
        or not fields
        or len(fields) != len(set(fields))
        or any(not isinstance(key, str) or key not in answer for key in fields)
    ):
        raise ValueError("Authored answer_fields must select unique engine output fields")
    return {key: answer[key] for key in fields}


def load_cases(batch=1, source_root=None, file_name=None, domain=None):
    check_batch(batch)
    source_root = Path(source_root) if source_root else authored_root()
    result, seen = [], set()
    for path in sorted((source_root / f"batch_{batch}").glob("*/*.json")):
        if domain and path.parent.name != domain:
            continue
        if file_name and path.name != file_name:
            continue
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError(f"Authored source is not a case list: {path}")
        for case in records:
            check_case(case)
            if case["case_id"] in seen:
                raise ValueError(f"Duplicate authored case ID: {case['case_id']}")
            seen.add(case["case_id"])
            result.append((case, path.relative_to(source_root).as_posix()))
    return sorted(result, key=lambda record: record[0]["case_id"])


def recover_case(metadata):
    provenance = metadata["authorship"]
    relative = Path(provenance["source_file"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Invalid authored source path")
    path = authored_root() / relative
    records = json.loads(path.read_text(encoding="utf-8"))
    cases = [case for case in records if case["case_id"] == provenance["case_id"]]
    if len(cases) != 1:
        raise ValueError("Authored source case is missing or ambiguous")
    case = check_case(cases[0])
    if scenario_hash(case) != provenance["case_sha256"]:
        raise ValueError("Authored source has changed since this task was built")
    if case["domain"] != metadata["domain"] or case["difficulty"] != metadata["difficulty"]:
        raise ValueError("Authored case metadata differs")
    return case


def _build_authored_at(output, *, batch=1, preview=False, file_name=None, domain=None):
    from render.authored import render_authored
    from validate import validate_task

    check_batch(batch)
    if (file_name or domain) and not preview:
        raise ValueError("A source-file or domain subset is only permitted for a preview")
    if domain and domain not in DOMAINS:
        raise ValueError("Unknown preview domain")
    cases = load_cases(batch, file_name=file_name, domain=domain)
    if not cases:
        raise ValueError("No individually authored cases found")
    counts = Counter((case["domain"], case["difficulty"]) for case, _ in cases)
    if not preview and any(
        counts[domain, difficulty] != expected
        for domain in DOMAINS
        for difficulty, expected in (("easy", 90), ("medium", 135), ("hard", 75))
    ):
        raise ValueError(
            "Release requires 300 individually authored cases per domain with 90/135/75 difficulty counts; use --preview for an incomplete editorial set"
        )
    instructions = [case["instruction"] for case, _ in cases]
    if len(set(instructions)) != len(instructions):
        raise ValueError("Repeated authored instructions require editorial revision")
    hashes = [scenario_hash(case["facts"]) for case, _ in cases]
    if len(set(hashes)) != len(hashes):
        raise ValueError("Repeated authored facts require editorial revision")
    if not preview:
        previous = [case for number in range(1, batch) for case, _ in load_cases(number)]
        previous_instructions = {case["instruction"] for case in previous}
        previous_hashes = {scenario_hash(case["facts"]) for case in previous}
        if previous_instructions.intersection(instructions) or previous_hashes.intersection(hashes):
            raise ValueError("Authored instructions and facts must differ from previous batches")
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to replace task set: {output}")
    output.mkdir(parents=True, exist_ok=True)
    manifest = []
    for case, source in cases:
        digest = scenario_hash(case)
        task_id = f"B{batch}_{case['case_id']}_{digest[:8]}"
        task_dir = output / case["domain"] / task_id
        task_dir.mkdir(parents=True)
        answer, trace = calculate(case["domain"], case["facts"])
        gold = project_answer(answer, case["answer_fields"])
        write_json(task_dir / "gold.json", gold)
        write_json(task_dir / "trace.json", trace)
        layout_seed = int(digest[:16], 16)
        files = render_authored(
            case["facts"], task_dir, case["domain"], case["documents"], layout_seed
        )
        task = {
            "task_id": task_id,
            "domain": case["domain"],
            "difficulty": case["difficulty"],
            "reference_period": PERIODS[case["domain"]],
            "instruction": case["instruction"],
            "input_files": files,
            "answer_schema": make_schema(gold),
            "canary": canary_for(f"authored/{batch}/{case['case_id']}/{digest}"),
            "scenario_seed": layout_seed,
            "scenario_hash": scenario_hash(case["facts"]),
            "authorship": {
                "method": "individually_written",
                "case_id": case["case_id"],
                "case_sha256": digest,
                "source_file": source,
            },
            "answer_fields": case["answer_fields"],
        }
        (task_dir / "task.yaml").write_text(
            yaml.safe_dump(task, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        validation = validate_task(task_dir)
        if not validation["passed"]:
            raise ValueError(
                f"Authored case {case['case_id']} failed gates: {validation['errors']}"
            )
        manifest.append(
            {
                "task_id": task_id,
                "case_id": case["case_id"],
                "domain": case["domain"],
                "difficulty": case["difficulty"],
                "scenario_hash": task["scenario_hash"],
                "path": str(task_dir.relative_to(output)),
            }
        )
    summary = {
        "batch": batch,
        "authorship": "individually_written",
        "preview": preview,
        "requested": len(cases),
        "accepted": len(manifest),
        "rejected_attempts": 0,
        "failure_reasons": {},
        "tasks": manifest,
    }
    write_json(output / "manifest.json", summary)
    return summary


def build_authored(output, *, batch=1, preview=False, file_name=None, domain=None):
    """Publish only a complete validated build, leaving failed work unpublished."""
    output = Path(output)
    if output.is_symlink() or output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to replace task set: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        summary = _build_authored_at(
            staging, batch=batch, preview=preview, file_name=file_name, domain=domain
        )
        if output.exists():
            output.rmdir()
        staging.rename(output)
        return summary
    finally:
        if staging.exists():
            shutil.rmtree(staging)
