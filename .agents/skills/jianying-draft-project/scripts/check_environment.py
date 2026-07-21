from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
LOCAL_RUNTIME = SKILL_DIR / ".runtime"
if LOCAL_RUNTIME.is_dir():
    sys.path.insert(0, str(LOCAL_RUNTIME))


def main() -> int:
    report = {
        "python": sys.executable,
        "python_version": sys.version.split()[0],
        "pyjianyingdraft": importlib.util.find_spec("pyJianYingDraft") is not None,
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "local_runtime": str(LOCAL_RUNTIME),
        "local_runtime_exists": LOCAL_RUNTIME.is_dir(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pyjianyingdraft"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
