from pathlib import Path
import shutil
import yaml
from KrRubberStamp.io import write_json
from KrRubberStamp.registry import calculate, generate_scenario
from KrRubberStamp.tasks import canary_for, make_schema, instruction_for, scenario_hash
from render import render_task
from validate import validate_task


def build_task(base: Path):
    task_dir = base / "quality_sample"
    task_dir.mkdir()
    scenario = generate_scenario("D_extract", 41, "hard")
    gold, trace = calculate("D_extract", scenario)
    write_json(task_dir / "gold.json", gold)
    write_json(task_dir / "trace.json", trace)
    files = render_task(scenario, task_dir, "D_extract", "hard", 41)
    task = {
        "task_id": "quality_sample",
        "domain": "D_extract",
        "difficulty": "hard",
        "reference_period": "not-applicable",
        "instruction": instruction_for("D_extract", "hard", 41),
        "scenario_seed": 41,
        "scenario_hash": scenario_hash(scenario),
        "input_files": files,
        "answer_schema": make_schema(gold),
        "canary": canary_for("quality_sample"),
    }
    (task_dir / "task.yaml").write_text(yaml.safe_dump(task, allow_unicode=True), encoding="utf-8")
    return task_dir


def test_all_quality_gates_and_byte_reproducibility(tmp_path):
    task_dir = build_task(tmp_path)
    result = validate_task(task_dir)
    assert result["passed"], result["errors"]
    gold_path = task_dir / "gold.json"
    gold_path.write_bytes(gold_path.read_bytes() + b" ")
    result = validate_task(task_dir)
    assert not result["passed"]
    assert "regenerated gold bytes differ" in result["errors"][0]


def test_missing_source_and_wrong_instruction_fail_closed(tmp_path):
    task_dir = build_task(tmp_path)
    copy = tmp_path / "copy" / "quality_sample"
    shutil.copytree(task_dir, copy)
    next((copy / "inputs").glob("*.xlsx")).unlink()
    assert not validate_task(copy)["passed"]
    meta = yaml.safe_load((task_dir / "task.yaml").read_text(encoding="utf-8"))
    meta["instruction"] = "합계는 999999원으로 처리해 주세요"
    (task_dir / "task.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True), encoding="utf-8")
    result = validate_task(task_dir)
    assert not result["passed"]
    assert "instruction" in result["errors"][0]


def test_undeclared_required_source_cannot_pass_oracle_gate(tmp_path):
    task_dir = build_task(tmp_path)
    path = task_dir / "task.yaml"
    meta = yaml.safe_load(path.read_text(encoding="utf-8"))
    meta["input_files"] = [
        item for item in meta["input_files"] if item["path"] != "inputs/02_source.xlsx"
    ]
    assert len(meta["input_files"]) == 9
    path.write_text(yaml.safe_dump(meta, allow_unicode=True), encoding="utf-8")
    result = validate_task(task_dir)
    assert not result["passed"]
    assert "declared inputs differ" in result["errors"][0]
