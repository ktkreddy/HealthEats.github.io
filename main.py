"""
Vercel FastAPI entrypoint: native ASGI `app` (see Vercel FastAPI docs).
Local: from repo root, `uvicorn main:app --reload --port 8080`
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from FastAPI_Backend.main import app  # noqa: E402

__all__ = ["app"]
