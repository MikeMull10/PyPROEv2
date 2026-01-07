import sys
from pathlib import Path

def app_root() -> Path:
    if hasattr(sys, '_MEIPASS'):    # PyInstaller stores files in a temporary folder (_MEIPASS) during execution
        return Path(sys._MEIPASS)
    elif getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "PyPROE X" / "_internal"
    return Path(__file__).resolve().parents[1] / "PyPROEv2"