"""Path checks used for staging and file-reading tools."""

from __future__ import annotations

import os
import stat
from contextlib import contextmanager
from pathlib import Path, PurePosixPath


def safe_relative_path(raw: str) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw or "\x00" in raw:
        raise ValueError("Path must be a nonempty relative POSIX path")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise ValueError("Absolute paths and parent traversal are forbidden")
    if path.as_posix() != raw or ":" in path.parts[0]:
        raise ValueError("Path must use canonical relative POSIX syntax")
    return Path(*path.parts)


def workspace_path(workspace: Path, raw: str, *, must_exist: bool = True) -> Path:
    relative = safe_relative_path(raw)
    workspace = Path(workspace)
    if workspace.is_symlink():
        raise ValueError("Workspace cannot be a symlink")
    root = workspace.resolve(strict=True)
    candidate = root / relative
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlinks are forbidden in workspace paths")
    resolved = candidate.resolve(strict=must_exist)
    if not resolved.is_relative_to(root):
        raise ValueError("Path escapes the workspace")
    return candidate


@contextmanager
def open_workspace_file(workspace: Path, raw: str):
    """Open without following symlinks, including during concurrent path swaps."""
    relative = safe_relative_path(raw)
    if Path(workspace).is_symlink():
        raise ValueError("Workspace cannot be a symlink")
    root = Path(workspace).resolve(strict=True)
    descriptors = []
    try:
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(directory)
        for part in relative.parts[:-1]:
            directory = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=directory,
            )
            descriptors.append(directory)
        descriptor = os.open(
            relative.parts[-1],
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=directory,
        )
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            raise ValueError("Only regular files can be read")
        with os.fdopen(descriptor, "rb") as stream:
            yield stream
    except OSError as error:
        raise ValueError(f"Workspace file cannot be opened safely: {raw}") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
