"""Same mandatory checks locally and in CI."""

import subprocess
import sys
from pathlib import Path

for command in ([sys.executable, "-m", "ruff", "check", "."], [sys.executable, "-m", "pytest"]):
    subprocess.run(command, check=True)

if Path("data/batch_1/manifest.json").is_file():
    subprocess.run(
        [sys.executable, "-m", "KrRubberStamp.cli", "validate", "--batch", "1"], check=True
    )
