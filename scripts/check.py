"""Same mandatory checks locally and in CI."""

import subprocess
import sys
from pathlib import Path

for command in ([sys.executable, "-m", "ruff", "check", "."], [sys.executable, "-m", "pytest"]):
    subprocess.run(command, check=True)

for directory in sorted(Path("data").glob("batch_*")):
    if not (directory / "manifest.json").is_file():
        continue
    subprocess.run(
        [sys.executable, "-m", "KrRubberStamp.cli", "validate", "--data", str(directory)],
        check=True,
    )
