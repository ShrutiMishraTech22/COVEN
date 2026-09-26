"""
Lets pytest resolve `from backend.app.X import Y` imports (used in
backend/tests/) when running pytest from the repo root.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
