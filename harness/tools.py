"""Bounded file reads and Python execution inside a staged task workspace.

File path checks are defense in depth, not an OS sandbox. The container backend
is required for untrusted Python. The local backend is explicitly trusted-only.
"""

from __future__ import annotations

import base64
import json
import os
import re
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .paths import open_workspace_file

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read one workspace file. UTF-8 text or base64 binary, capped at 65536 bytes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "max_bytes": {"type": "integer", "minimum": 1, "maximum": 65536},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "python_exec",
            "description": "Run Python in the task workspace with a timeout and bounded output.",
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string", "maxLength": 32768}},
                "required": ["code"],
                "additionalProperties": False,
            },
        },
    },
]


def _bounded_process(command: list[str], cwd: Path, timeout: float, max_output: int) -> dict:
    """Drain one pipe while bounding resident output and terminating its group."""
    output = bytearray()
    timed_out = False
    truncated = False
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    selector = selectors.DefaultSelector()
    assert process.stdout is not None
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        while selector.get_map():
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                timed_out = True
                break
            ready = selector.select(min(remaining, 0.1))
            for key, events in ready:
                chunk = os.read(key.fileobj.fileno(), min(8192, max_output - len(output) + 1))
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                room = max_output - len(output)
                output.extend(chunk[:room])
                if len(chunk) > room:
                    truncated = True
                    break
            if truncated:
                break
        if timed_out or truncated:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=max(0.01, timeout - (time.monotonic() - started)))
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    finally:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        selector.close()
        process.stdout.close()
    return {
        "exit_code": process.returncode,
        "stdout": output.decode("utf-8", errors="replace"),
        "timed_out": timed_out,
        "output_truncated": truncated,
    }


class WorkspaceTools:
    """Use execution_backend='container' for model-generated code.

    execution_backend='local' requires trusted_local=True. Arbitrary local
    Python can read the host filesystem and network, irrespective of cwd.
    """

    def __init__(
        self,
        workspace: Path,
        *,
        execution_backend: str = "container",
        trusted_local: bool = False,
        image: str = "python:3.12-slim",
        timeout: float = 10,
        max_output: int = 65536,
    ):
        if Path(workspace).is_symlink():
            raise ValueError("Workspace cannot be a symlink")
        self.workspace = Path(workspace).resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError("Workspace must be a directory")
        if execution_backend not in {"container", "local"}:
            raise ValueError("Python backend must be container or local")
        if execution_backend == "local" and not trusted_local:
            raise ValueError("Local Python is trusted-only and provides no host isolation")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/@-]*", image):
            raise ValueError("Invalid container image name")
        if not 0 < timeout <= 120 or not 0 < max_output <= 1048576:
            raise ValueError("Invalid tool resource limits")
        self.execution_backend = execution_backend
        self.image = image
        self.timeout = timeout
        self.max_output = max_output

    @property
    def tool_specs(self) -> list[dict]:
        return json.loads(json.dumps(TOOL_SPECS))

    def read_file(self, path: str, max_bytes: int = 65536) -> dict:
        if type(max_bytes) is not int or not 0 < max_bytes <= 65536:
            raise ValueError("max_bytes must be an integer between 1 and 65536")
        with open_workspace_file(self.workspace, path) as stream:
            content = stream.read(max_bytes + 1)
        truncated = len(content) > max_bytes
        content = content[:max_bytes]
        try:
            text = content.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            text = base64.b64encode(content).decode("ascii")
            encoding = "base64"
        return {"path": path, "content": text, "encoding": encoding, "truncated": truncated}

    def python_exec(self, code: str) -> dict:
        if not isinstance(code, str) or not code or len(code) > 32768:
            raise ValueError("Python code must contain 1 to 32768 characters")
        if self.execution_backend == "local":
            return _bounded_process(
                [sys.executable, "-I", "-u", "-c", code],
                self.workspace,
                self.timeout,
                self.max_output,
            )
        docker = shutil.which("docker")
        if not docker:
            raise RuntimeError("Docker is required for untrusted Python execution")
        if "," in str(self.workspace) or "\n" in str(self.workspace):
            raise ValueError("Container mount paths cannot contain commas or newlines")
        with tempfile.TemporaryDirectory(prefix="krt-container-") as temporary:
            cidfile = Path(temporary) / "cid"
            command = [
                docker,
                "run",
                "--rm",
                "--pull=never",
                "--cidfile",
                str(cidfile),
                "--network=none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--pids-limit=64",
                "--memory=256m",
                "--cpus=1",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                "--mount",
                f"type=bind,source={self.workspace},target=/workspace",
                "--workdir=/workspace",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=64m",
                self.image,
                "python",
                "-I",
                "-u",
                "-c",
                code,
            ]
            try:
                return _bounded_process(command, self.workspace, self.timeout, self.max_output)
            finally:
                if cidfile.is_file():
                    container_id = cidfile.read_text(encoding="ascii").strip()
                    if re.fullmatch(r"[0-9a-f]{12,64}", container_id):
                        subprocess.run(
                            [docker, "rm", "-f", container_id],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=10,
                            check=False,
                        )

    def call(self, name: str, arguments: dict) -> dict:
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object")
        if name == "read_file" and set(arguments) <= {"path", "max_bytes"}:
            return self.read_file(**arguments)
        if name == "python_exec" and set(arguments) == {"code"}:
            return self.python_exec(**arguments)
        raise ValueError(f"Unknown tool or invalid arguments: {name}")
