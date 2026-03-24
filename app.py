"""
Vercel ASGI entry: use app.py (listed first in Vercel Python entrypoints).

One file must expose `app`; do not split FastAPI across api/*.py (each file = one URL).

Local: uvicorn app:app --host 127.0.0.1 --port 8080 --reload
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from FastAPI_Backend.main import app  # noqa: E402

__all__ = ["app"]
