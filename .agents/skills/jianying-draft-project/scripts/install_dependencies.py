from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REQUIREMENTS = SKILL_DIR / "requirements.txt"
DEFAULT_TARGET = SKILL_DIR / ".runtime"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Python runtime used by this skill.")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    target = args.target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--requirement",
        str(REQUIREMENTS),
        "--target",
        str(target),
    ]
    subprocess.run(command, check=True)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
