"""
Vercel FastAPI entry — root app.py exports `app` (Vercel Python ASGI entrypoint).

Routes (no /api/* prefix — Vercel reserves that for api/ directory):
  GET  /          → health check
  GET  /health    → health check
  POST /predict/  → diet recommendations
  GET  /docs      → Swagger UI

Local: uvicorn app:app --host 127.0.0.1 --port 8080 --reload
"""
import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import output_recommended_recipes, recommend

_BASE = Path(__file__).resolve().parent
for _p in [_BASE / "Data" / "dataset.csv.gz", _BASE / "Data" / "dataset.csv"]:
    if _p.is_file():
        dataset = pd.read_csv(_p, compression="gzip" if _p.suffix == ".gz" else None)
        break
else:
    raise FileNotFoundError(f"Dataset not found in {_BASE / 'Data'}. Add dataset.csv.gz.")

app = FastAPI(title="HealthEats API", docs_url="/docs", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Params(BaseModel):
    n_neighbors: int = 5
    return_distance: bool = False


class PredictionIn(BaseModel):
    nutrition_input: List[float] = Field(..., min_length=9, max_length=9)
    ingredients: List[str] = []
    ingredients_to_avoid: List[str] = []
    ingredients_to_avoid_txt: Optional[List[str]] = None
    params: Optional[Params] = None


class Recipe(BaseModel):
    Name: str
    CookTime: str
    PrepTime: str
    TotalTime: str
    RecipeIngredientParts: List[str]
    Calories: float
    FatContent: float
    SaturatedFatContent: float
    CholesterolContent: float
    SodiumContent: float
    CarbohydrateContent: float
    FiberContent: float
    SugarContent: float
    ProteinContent: float
    RecipeInstructions: List[str]


class PredictionOut(BaseModel):
    output: Optional[List[Recipe]] = None


@app.get("/")
@app.get("/health")
def health():
    return {"health_check": "OK"}


@app.post("/predict/", response_model=PredictionOut)
def predict(prediction_input: PredictionIn):
    p = (
        prediction_input.params.model_dump()
        if prediction_input.params
        else {"n_neighbors": 5, "return_distance": False}
    )
    avoid = [
        x
        for x in (prediction_input.ingredients_to_avoid_txt or prediction_input.ingredients_to_avoid)
        if x and str(x).strip()
    ]
    df = recommend(dataset, list(prediction_input.nutrition_input), prediction_input.ingredients, avoid, p)
    return PredictionOut(output=output_recommended_recipes(df))
