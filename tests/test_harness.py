import json
from pathlib import Path

import httpx
import pytest
import yaml

from harness import WorkspaceTools, run_fake, run_with_adapter, stage_task
from harness.adapter import OpenAICompatibleAdapter
from harness.runner import _oracle


def make_task(tmp_path, task_id="sample", gold=42):
    task = tmp_path / "batch" / "D_extract" / task_id
    inputs = task / "inputs"
    inputs.mkdir(parents=True)
    (inputs / "visible.json").write_text('{"amount": 42}', encoding="utf-8")
    (task / "gold.json").write_text(json.dumps({"amount": gold}), encoding="utf-8")
    (task / "trace.json").write_text('{"private": "trace"}', encoding="utf-8")
    (task / "extraction_map.json").write_text('{"private": "map"}', encoding="utf-8")
    metadata = {
        "task_id": task_id,
        "domain": "D_extract",
        "difficulty": "easy",
        "reference_period": "2026",
        "instruction": "보이는 금액을 합산해 주세요.",
        "input_files": [{"path": "inputs/visible.json", "format": "json"}],
        "answer_schema": {
            "type": "object",
            "properties": {"amount": {"type": "integer"}},
            "required": ["amount"],
            "additionalProperties": False,
        },
        "canary": "NEVER-STAGE-THIS-CANARY",
    }
    (task / "task.yaml").write_text(yaml.safe_dump(metadata, allow_unicode=True), encoding="utf-8")
    return task


def fake_oracle_dependencies(monkeypatch):
    import render
    import KrRubberStamp.registry

    monkeypatch.setattr(
        render,
        "restore_scenario",
        lambda task: json.loads((task / "inputs" / "visible.json").read_text(encoding="utf-8")),
    )
    monkeypatch.setattr(
        KrRubberStamp.registry,
        "calculate",
        lambda domain, facts: (
            {"amount": facts["amount"]},
            {"computed": True},
        ),
    )


def test_stage_contains_only_declared_inputs_instruction_and_schema(tmp_path):
    task = make_task(tmp_path)
    (task / "inputs" / "undeclared.txt").write_text("should not be copied")
    staged = stage_task(task, tmp_path / "work")
    files = sorted(
        path.relative_to(staged).as_posix() for path in staged.rglob("*") if path.is_file()
    )
    assert files == ["answer_schema.json", "inputs/visible.json", "instruction.txt"]
    for path in staged.rglob("*"):
        if path.is_file():
            assert "NEVER-STAGE-THIS-CANARY" not in path.read_text(encoding="utf-8")
    second = stage_task(task, tmp_path / "work")
    assert second != staged


@pytest.mark.parametrize(
    "path",
    [
        "../gold.json",
        "/etc/passwd",
        "inputs/../../gold.json",
        "inputs/gold.json",
        "inputs//visible.json",
        "inputs/./visible.json",
        "inputs\\visible.json",
    ],
)
def test_stage_rejects_traversal_and_private_names(tmp_path, path):
    task = make_task(tmp_path)
    metadata = yaml.safe_load((task / "task.yaml").read_text())
    metadata["input_files"][0]["path"] = path
    (task / "task.yaml").write_text(yaml.safe_dump(metadata))
    with pytest.raises(ValueError):
        stage_task(task, tmp_path / "work")
    assert list((tmp_path / "work").iterdir()) == []


def test_stage_and_file_tools_reject_symlink_escape(tmp_path):
    task = make_task(tmp_path)
    visible = task / "inputs" / "visible.json"
    visible.unlink()
    visible.symlink_to(task / "gold.json")
    with pytest.raises(ValueError):
        stage_task(task, tmp_path / "work")
    workspace = tmp_path / "tools"
    workspace.mkdir()
    (workspace / "leak").symlink_to(task / "gold.json")
    tools = WorkspaceTools(workspace)
    with pytest.raises(ValueError):
        tools.read_file("leak")
    (workspace / "leak_directory").symlink_to(task / "inputs", target_is_directory=True)
    with pytest.raises(ValueError):
        tools.read_file("leak_directory/visible.json")


def test_fake_oracle_and_null_scores_without_model_calls(tmp_path, monkeypatch):
    make_task(tmp_path)
    fake_oracle_dependencies(monkeypatch)
    monkeypatch.setattr(
        httpx.Client, "post", lambda *args, **kwargs: pytest.fail("Model API called")
    )
    oracle = run_fake(tmp_path / "batch", tmp_path / "oracle", "oracle", tmp_path / "work")
    null = run_fake(tmp_path / "batch", tmp_path / "null", "null")
    assert oracle["exact_match"] == oracle["field_accuracy"] == 1
    assert null["exact_match"] == null["field_accuracy"] == 0
    assert oracle["workspaces_retained"]
    assert not null["workspaces_retained"]
    assert not Path(null["staged_tasks"][0]["workdir"]).exists()


def test_oracle_cannot_read_gold_or_trace_to_solve(tmp_path, monkeypatch):
    task = make_task(tmp_path, gold=999)
    fake_oracle_dependencies(monkeypatch)
    original_read_text = Path.read_text

    def guarded_read(path, *args, **kwargs):
        if path.name in {"gold.json", "trace.json"}:
            pytest.fail(f"Oracle read private answer artifact {path.name}")
        return original_read_text(path, *args, **kwargs)

    with monkeypatch.context() as guard:
        guard.setattr(Path, "read_text", guarded_read)
        assert _oracle(task, "D_extract") == {"amount": 42}
    result = run_fake(tmp_path / "batch", tmp_path / "answers", "oracle")
    assert json.loads((tmp_path / "answers" / "sample" / "answer.json").read_text()) == {
        "amount": 42
    }
    assert result["exact_match"] == 0


def test_file_reads_are_bounded_and_binary_explicit(tmp_path):
    (tmp_path / "large.txt").write_text("abcdefghij")
    (tmp_path / "binary.pdf").write_bytes(b"\xff\xfe\x00")
    tools = WorkspaceTools(tmp_path)
    assert tools.read_file("large.txt", 4) == {
        "path": "large.txt",
        "content": "abcd",
        "encoding": "utf-8",
        "truncated": True,
    }
    assert tools.read_file("binary.pdf")["encoding"] == "base64"
    for path in ["../secret", "/etc/passwd", "./large.txt", "large.txt/../large.txt"]:
        with pytest.raises(ValueError):
            tools.read_file(path)
    with pytest.raises(ValueError):
        tools.read_file("large.txt", True)


def test_local_python_requires_trusted_opt_in_and_bounds_output_timeout(tmp_path):
    with pytest.raises(ValueError, match="trusted-only"):
        WorkspaceTools(tmp_path, execution_backend="local")
    tools = WorkspaceTools(tmp_path, execution_backend="local", trusted_local=True, max_output=64)
    result = tools.python_exec("print('hello')")
    assert result["stdout"] == "hello\n" and result["exit_code"] == 0
    noisy = tools.python_exec("print('x' * 10000)")
    assert len(noisy["stdout"]) == 64 and noisy["output_truncated"]
    tools.timeout = 0.1
    assert tools.python_exec("import time; time.sleep(2)")["timed_out"]


def test_default_python_backend_requires_docker_not_host_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr("harness.tools.shutil.which", lambda executable: None)
    with pytest.raises(RuntimeError, match="Docker is required"):
        WorkspaceTools(tmp_path).python_exec("print(1)")


def test_container_command_exposes_only_workspace_and_blocks_network(tmp_path, monkeypatch):
    commands = []
    monkeypatch.setattr("harness.tools.shutil.which", lambda executable: "/fake/docker")

    def fake_process(command, cwd, timeout, max_output):
        commands.append(command)
        return {"exit_code": 0, "stdout": "ok", "timed_out": False, "output_truncated": False}

    monkeypatch.setattr("harness.tools._bounded_process", fake_process)
    WorkspaceTools(tmp_path).python_exec("print('ok')")
    command = commands[0]
    assert "--network=none" in command
    assert "--read-only" in command
    assert "--pull=never" in command
    assert "--cap-drop=ALL" in command
    assert command.count("--mount") == 1
    mount = command[command.index("--mount") + 1]
    assert mount == f"type=bind,source={tmp_path},target=/workspace"
    assert "--env" not in command and "-e" not in command


def test_constructing_api_adapter_performs_no_requests(monkeypatch):
    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: pytest.fail("HTTP request"))
    adapter = OpenAICompatibleAdapter(
        model="user-selected-model", base_url="https://example.invalid/v1"
    )
    assert adapter.model == "user-selected-model"


def test_injected_adapter_has_no_gold_in_context_and_can_return_json(tmp_path, monkeypatch):
    make_task(tmp_path)
    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: pytest.fail("HTTP request"))

    class FakeAdapter:
        def complete(self, messages, tools):
            serialized = json.dumps(messages)
            for private in [
                "gold.json",
                "trace.json",
                "extraction_map.json",
                "NEVER-STAGE-THIS-CANARY",
            ]:
                assert private not in serialized
            assert {tool["function"]["name"] for tool in tools} == {"read_file", "python_exec"}
            return {"role": "assistant", "content": '{"amount":42}'}

    result = run_with_adapter(tmp_path / "batch", tmp_path / "answers", FakeAdapter())
    assert result["exact_match"] == 1


@pytest.mark.parametrize("content", ['{"amount":NaN}', '{"amount":42,"amount":42}'])
def test_injected_adapter_invalid_json_scores_zero(tmp_path, content):
    make_task(tmp_path)

    class FakeAdapter:
        def complete(self, messages, tools):
            return {"role": "assistant", "content": content}

    result = run_with_adapter(tmp_path / "batch", tmp_path / "answers", FakeAdapter())
    assert result["exact_match"] == 0
    assert result["field_accuracy"] == 0
