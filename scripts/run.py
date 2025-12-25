#!/usr/bin/env python
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
import venv


ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = ROOT / ".venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_venv() -> Path:
    python_path = venv_python()
    if python_path.exists():
        return python_path
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(VENV_DIR)
    return python_path


def run(*args: str) -> None:
    subprocess.check_call(list(args), cwd=str(ROOT))


def main() -> int:
    python_path = ensure_venv()
    run(str(python_path), "-m", "pip", "install", "-r", "requirements.txt")
    run(str(python_path), "manage.py", "migrate")
    run(str(python_path), "manage.py", "runserver", "0.0.0.0:9999")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
