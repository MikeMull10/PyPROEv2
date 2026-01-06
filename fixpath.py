import sys
from pathlib import Path

def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "PyPROE X" / "_internal"
    return Path(__file__).resolve().parents[1] / "PyPROEv2"