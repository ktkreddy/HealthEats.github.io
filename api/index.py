"""
Vercel FastAPI entry: must live under api/ for functions config + routing.
Local: uvicorn api.index:app --host 127.0.0.1 --port 8080 --reload
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from FastAPI_Backend.main import app  # noqa: E402

__all__ = ["app"]
