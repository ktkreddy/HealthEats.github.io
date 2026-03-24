"""
Single Vercel ASGI entry: root main.py handles all routes (FastAPI on Vercel).

Do not use api/*.py for FastAPI — each file under api/ is a separate function and
only serves one path (e.g. /api), so /api/predict returns 404.

Local: uvicorn main:app --host 127.0.0.1 --port 8080 --reload
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from FastAPI_Backend.main import app  # noqa: E402

__all__ = ["app"]
