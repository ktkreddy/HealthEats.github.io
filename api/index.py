import os
import sys

# Project root (parent of api/) for FastAPI_Backend imports and Data/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mangum import Mangum

from FastAPI_Backend.main import app

handler = Mangum(app, lifespan="off")
