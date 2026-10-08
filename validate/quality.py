"""Fail-closed source-document roundtrip and answer-first reproducibility checks."""

from collections import Counter
from pathlib import Path
import json
import yaml
from jsonschema import Draft202012Validator
from KrRubberStamp.io import json_bytes
from KrRubberStamp.registry import DOMAINS, PERIODS, calculate, generate_scenario
from KrRubberStamp.tasks import instruction_for, scenario_hash

REQUIRED = {
    "task_id",
    "domain",
    "difficulty",
    "reference_period",
    "instruction",
    "input_files",
    "answer_schema",
    "canary",
    "scenario_seed",
    "scenario_hash",
}


def validate_task(task_dir: Path) -> dict:
    from render import restore_scenario

    task_dir = Path(task_dir)
    result = {"task_id": task_dir.name, "passed": False, "errors": [], "gates": {}}
    errors = result["errors"]
    try:
        task = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
        if not isinstance(task, dict) or REQUIRED - task.keys():
            raise ValueError("task.yaml missing required metadata")
        domain, difficulty = task["domain"], task["difficulty"]
        if domain not in DOMAINS or difficulty not in ("easy", "medium", "hard"):
            raise ValueError("invalid domain or difficulty")
        if task["reference_period"] != PERIODS[domain]:
            raise ValueError("reference_period mismatch")
        if task["task_id"] != task_dir.name or not task["canary"].startswith(
            "KrRubberStamp-canary-"
        ):
            raise ValueError("task identity/canary mismatch")
        inputs = task["input_files"]
        count = len(inputs)
        if not (
            1 <= count <= 3
            if difficulty == "easy"
            else 4 <= count <= 8
            if difficulty == "medium"
            else count >= 9
        ):
            raise ValueError("difficulty document-count mismatch")
        for source in inputs:
            path = (task_dir / source["path"]).resolve()
            if (
                not path.is_relative_to((task_dir / "inputs").resolve())
                or not path.is_file()
                or path.stat().st_size == 0
            ):
                raise ValueError("invalid or empty input file")
            if path.suffix.lower() != "." + source["format"]:
                raise ValueError("input format does not match filename suffix")
        declared = {source["path"]: source["format"] for source in inputs}
        if len(declared) != count:
            raise ValueError("duplicate input file declaration")
        mapping = json.loads((task_dir / "extraction_map.json").read_text(encoding="utf-8"))
        mapped_documents = {doc["path"]: doc["format"] for doc in mapping["documents"]}
        if len(mapped_documents) != len(mapping["documents"]) or declared != mapped_documents:
            raise ValueError("declared inputs differ from rendered extraction-map documents")
        if any(record["file"] not in declared for record in mapping["records"]):
            raise ValueError("reconstruction reads an undeclared source file")
        physical = {
            str(path.relative_to(task_dir))
            for path in (task_dir / "inputs").rglob("*")
            if path.is_file()
        }
        if set(declared) != physical:
            raise ValueError("physical input files differ from declared inputs")
        result["gates"]["metadata"] = True
        gold = json.loads((task_dir / "gold.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(task["answer_schema"])
        schema_errors = list(Draft202012Validator(task["answer_schema"]).iter_errors(gold))
        if schema_errors:
            raise ValueError("gold violates answer_schema: " + schema_errors[0].message)
        result["gates"]["schema"] = True
        authored_case = None
        if "authorship" in task:
            from KrRubberStamp.authoring import recover_case, project_answer

            if task["authorship"].get("method") != "individually_written":
                raise ValueError("Unknown authorship method")
            authored_case = recover_case(task)
            regenerated = authored_case["facts"]
            if task.get("answer_fields") != authored_case["answer_fields"]:
                raise ValueError("Answer request differs from individually authored case")
            planned = {
                f"inputs/{doc['filename']}": doc["format"] for doc in authored_case["documents"]
            }
            if declared != planned:
                raise ValueError("Inputs differ from individually authored document plan")
        else:
            regenerated = generate_scenario(domain, task["scenario_seed"], difficulty)
        expected, expected_trace = calculate(domain, regenerated)
        if authored_case:
            expected = project_answer(expected, authored_case["answer_fields"])
        if json_bytes(expected) != (task_dir / "gold.json").read_bytes():
            raise ValueError("regenerated gold bytes differ")
        if json_bytes(expected_trace) != (task_dir / "trace.json").read_bytes():
            raise ValueError("regenerated trace bytes differ")
        source_file = Path(__file__).resolve().parents[1] / "rules/sources.yaml"
        if source_file.is_file():
            source_registry = yaml.safe_load(source_file.read_text(encoding="utf-8"))
            known_ids = {entry["rule_id"] for entry in source_registry["rules"]}
            unknown = {step["rule_id"] for step in expected_trace} - known_ids
            if unknown:
                raise ValueError(f"trace contains unknown source rule IDs: {sorted(unknown)}")
            result["gates"]["source_coverage"] = True
        if scenario_hash(regenerated) != task["scenario_hash"]:
            raise ValueError("scenario hash mismatch")
        result["gates"]["reproducibility"] = True
        restored = restore_scenario(task_dir)
        if restored != regenerated:
            raise ValueError("source document reconstruction differs from generated scenario")
        reconstructed_gold, _ = calculate(domain, restored)
        if authored_case:
            reconstructed_gold = project_answer(reconstructed_gold, authored_case["answer_fields"])
        if json_bytes(reconstructed_gold) != json_bytes(gold):
            raise ValueError("source-only answer differs from gold")
        result["gates"]["solvability"] = True
        expected_instruction = (
            authored_case["instruction"]
            if authored_case
            else instruction_for(domain, difficulty, task["scenario_seed"])
        )
        if task["instruction"] != expected_instruction:
            raise ValueError("instruction contradicts deterministic wording/period")
        exceptions = (
            authored_case["exceptions"] if authored_case else regenerated.get("exceptions", [])
        )
        if difficulty == "medium" and len(exceptions) != 1:
            raise ValueError("medium must have exactly one scenario exception")
        if difficulty == "hard" and len(exceptions) < 2:
            raise ValueError("hard must have at least two scenario exceptions")
        if difficulty == "easy" and exceptions:
            raise ValueError("easy must have no exception")
        result["gates"]["instruction_consistency"] = True
        result["passed"] = True
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
    return result


def validate_batch(batch_dir: Path) -> dict:
    batch_dir = Path(batch_dir)
    results = [validate_task(task.parent) for task in sorted(batch_dir.glob("*/*/task.yaml"))]
    failures = Counter(error for result in results for error in result["errors"])
    hashes = []
    counts = Counter()
    canaries = []
    for task in sorted(batch_dir.glob("*/*/task.yaml")):
        meta = yaml.safe_load(task.read_text(encoding="utf-8"))
        hashes.append(meta["scenario_hash"])
        canaries.append(meta["canary"])
        counts[(meta["domain"], meta["difficulty"])] += 1
    if len(hashes) != len(set(hashes)):
        failures["duplicate scenario hash"] += len(hashes) - len(set(hashes))
    if len(canaries) != len(set(canaries)):
        failures["duplicate canary"] += len(canaries) - len(set(canaries))
    passed = sum(r["passed"] for r in results)
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": passed / len(results) if results else 0,
        "all_passed": bool(results) and passed == len(results) and not failures,
        "failure_reasons": dict(failures),
        "counts": {
            f"{domain}/{difficulty}": count
            for (domain, difficulty), count in sorted(counts.items())
        },
        "results": results,
    }
