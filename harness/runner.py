"""Trusted coordination around strictly separated agent workspaces."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from grader import grade_batch
from grader.core import parse_json, task_directories, task_metadata

from .adapter import ChatAdapter
from .paths import open_workspace_file, safe_relative_path, workspace_path
from .tools import WorkspaceTools

_PRIVATE = {"gold.json", "trace.json", "extraction_map.json", "task.yaml"}


def _write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def stage_task(task_dir: Path, work_root: Path) -> Path:
    """Create a fresh workspace containing only declared inputs and instructions.

    task.yaml, canary metadata, gold, trace, and extraction maps stay outside it.
    The trusted coordinator is the only reader of those private assets.
    """
    task_dir, work_root = Path(task_dir), Path(work_root)
    metadata = task_metadata(task_dir)
    instruction = metadata.get("instruction")
    input_files = metadata.get("input_files")
    if not isinstance(instruction, str) or not isinstance(input_files, list) or not input_files:
        raise ValueError("Task must declare an instruction and at least one input file")
    work_root.mkdir(parents=True, exist_ok=True)
    if work_root.is_symlink():
        raise ValueError("Work root cannot be a symlink")
    workdir = Path(tempfile.mkdtemp(prefix=f"{metadata['task_id']}-", dir=work_root))
    seen = set()
    try:
        for specification in input_files:
            if not isinstance(specification, dict) or not isinstance(
                specification.get("format"), str
            ):
                raise ValueError("Each input file must declare its path and format")
            raw = specification.get("path")
            relative = safe_relative_path(raw)
            if (
                relative.parts[0] != "inputs"
                or len(relative.parts) < 2
                or relative.name in _PRIVATE
                or raw in seen
            ):
                raise ValueError("Only unique non-private inputs/ files may be staged")
            seen.add(raw)
            destination = workdir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open_workspace_file(task_dir, raw) as source:
                with destination.open("xb") as output:
                    shutil.copyfileobj(source, output)
        (workdir / "instruction.txt").write_text(instruction + "\n", encoding="utf-8")
        _write_json(workdir / "answer_schema.json", metadata["answer_schema"])
        return workdir
    except BaseException:
        shutil.rmtree(workdir)
        raise


def _save_answer(answers_dir: Path, task_id: str, answer) -> None:
    answers_dir.mkdir(parents=True, exist_ok=True)
    if answers_dir.is_symlink():
        raise ValueError("Answers root cannot be a symlink")
    destination = answers_dir / task_id
    destination.mkdir(exist_ok=True)
    if destination.is_symlink() or (destination / "answer.json").is_symlink():
        raise ValueError("Answer destination cannot be a symlink")
    _write_json(destination / "answer.json", answer)


def _oracle(task_dir: Path, domain: str) -> dict:
    # Restore facts by parsing the actual rendered input files using their map.
    # This trusted path must never shortcut by loading gold.json or trace.json.
    from KrRubberStamp.registry import calculate
    from render import restore_scenario

    scenario = restore_scenario(task_dir)
    answer, trace = calculate(domain, scenario)
    return answer


def _run_tasks(batch_dir: Path, answers_dir: Path, work_root: Path, solve) -> dict:
    staged = []
    seen = set()
    for task_dir in task_directories(batch_dir):
        metadata = task_metadata(task_dir)
        if metadata["task_id"] in seen:
            raise ValueError(f"Duplicate task_id in batch: {metadata['task_id']}")
        seen.add(metadata["task_id"])
        workdir = stage_task(task_dir, work_root)
        answer = solve(task_dir, metadata, workdir)
        _save_answer(answers_dir, metadata["task_id"], answer)
        staged.append({"task_id": metadata["task_id"], "workdir": str(workdir)})
    return {**grade_batch(batch_dir, answers_dir), "staged_tasks": staged}


def run_fake(
    batch_dir: Path,
    answers_dir: Path,
    solver: str = "oracle",
    work_root: Path | None = None,
) -> dict:
    """Evaluate oracle/null fake solvers. This never constructs or calls a model.

    Oracle restoration happens in the trusted coordinator, outside the staged
    workspace. Specifying work_root retains workspaces for inspection; temporary
    workspaces are removed when work_root is omitted. Answers always persist.
    """
    if solver not in {"oracle", "null"}:
        raise ValueError("Fake solver must be oracle or null")
    batch_dir, answers_dir = Path(batch_dir), Path(answers_dir)

    def solve(task_dir, metadata, workdir):
        return _oracle(task_dir, metadata["domain"]) if solver == "oracle" else {}

    if work_root is None:
        with tempfile.TemporaryDirectory(prefix="krt-harness-") as temporary:
            result = _run_tasks(batch_dir, answers_dir, Path(temporary), solve)
    else:
        result = _run_tasks(batch_dir, answers_dir, Path(work_root), solve)
    return {"solver": solver, "workspaces_retained": work_root is not None, **result}


def _answer_from_workspace(workdir: Path, content) -> dict:
    target = workspace_path(workdir, "answer.json", must_exist=False)
    if target.exists():
        with open_workspace_file(workdir, "answer.json") as stream:
            raw = stream.read(1048577)
        if len(raw) > 1048576:
            raise ValueError("answer.json exceeds the 1 MiB answer limit")
        answer = parse_json(raw.decode("utf-8"))
    elif isinstance(content, str):
        # A final JSON object is a convenient alternative to tool-written files.
        if len(content.encode("utf-8")) > 1048576:
            raise ValueError("Final answer exceeds the 1 MiB answer limit")
        answer = parse_json(content)
    else:
        answer = {}
    if not isinstance(answer, dict):
        raise ValueError("The submitted answer must be a JSON object")
    return answer


def run_with_adapter(
    batch_dir: Path,
    answers_dir: Path,
    adapter: ChatAdapter,
    *,
    work_root: Path | None = None,
    max_turns: int = 20,
    container_image: str = "python:3.12-slim",
) -> dict:
    """Opt-in external-model runner for dataset users, never used in this build.

    It accepts an injected ChatAdapter. Model Python uses the container backend,
    which has only that task directory mounted and no network access. Prepare
    the image separately: the runner never pulls an image or invokes a model
    unless the caller explicitly invokes this function with an adapter.
    """
    if type(max_turns) is not int or not 1 <= max_turns <= 100:
        raise ValueError("max_turns must be between 1 and 100")

    def solve(task_dir, metadata, workdir):
        tools = WorkspaceTools(workdir, image=container_image)
        inputs = [item["path"] for item in metadata["input_files"]]
        messages = [
            {
                "role": "system",
                "content": (
                    "Solve the supplied office task using the staged files and tools. "
                    "Save a JSON object to answer.json or return only that JSON object. "
                    "The answer schema is in answer_schema.json. "
                    "Python runs in /workspace with no network."
                ),
            },
            {
                "role": "user",
                "content": metadata["instruction"] + "\nInput files:\n" + "\n".join(inputs),
            },
        ]
        content = None
        for turn in range(max_turns):
            message = adapter.complete(messages, tools.tool_specs)
            if not isinstance(message, dict) or message.get("role") != "assistant":
                raise ValueError("Adapter must return an assistant message")
            messages.append(message)
            calls = message.get("tool_calls") or []
            content = message.get("content")
            if not calls:
                break
            if not isinstance(calls, list) or len(calls) > 16:
                raise ValueError("A turn may contain at most 16 tool calls")
            for call in calls:
                function = call.get("function", {})
                try:
                    arguments = json.loads(function.get("arguments", "{}"))
                    result = tools.call(function.get("name"), arguments)
                except (OSError, ValueError, TypeError, RuntimeError) as error:
                    result = {"error": str(error)}
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
        try:
            return _answer_from_workspace(workdir, content)
        except (OSError, ValueError, UnicodeError):
            return {}

    batch_dir, answers_dir = Path(batch_dir), Path(answers_dir)
    if work_root is None:
        with tempfile.TemporaryDirectory(prefix="krt-model-") as temporary:
            result = _run_tasks(batch_dir, answers_dir, Path(temporary), solve)
    else:
        result = _run_tasks(batch_dir, answers_dir, Path(work_root), solve)
    return {"solver": "adapter", "workspaces_retained": work_root is not None, **result}
