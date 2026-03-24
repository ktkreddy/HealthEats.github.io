import os
import sys
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from model import output_recommended_recipes, recommend

BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_CANDIDATES = [
    BASE_DIR / "Data" / "dataset.csv.gz",
    BASE_DIR / "Data" / "dataset.csv",
]


def _load_dataset():
    for path in _DATA_CANDIDATES:
        if path.is_file():
            if path.suffix == ".gz":
                return pd.read_csv(path, compression="gzip")
            return pd.read_csv(path)
    raise FileNotFoundError(
        f"No dataset found. Place dataset.csv.gz (or dataset.csv) under {BASE_DIR / 'Data'}. "
        "See the notebook for building it from the Food.com Kaggle dataset."
    )


dataset = _load_dataset()

# Docs at /docs (not /api/docs): on Vercel, /api/* is routed only to api/*.py, not root app.py.
app = FastAPI(
    title="Diet Recommendation API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url=None,
)

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


def _resolve_avoid(p: PredictionIn) -> List[str]:
    if p.ingredients_to_avoid_txt is not None:
        return [x for x in p.ingredients_to_avoid_txt if x and str(x).strip()]
    return [x for x in (p.ingredients_to_avoid or []) if x and str(x).strip()]


def _predict(prediction_input: PredictionIn) -> PredictionOut:
    p = (
        prediction_input.params.model_dump()
        if prediction_input.params is not None
        else {"n_neighbors": 5, "return_distance": False}
    )
    avoid = _resolve_avoid(prediction_input)
    recommendation_dataframe = recommend(
        dataset,
        list(prediction_input.nutrition_input),
        prediction_input.ingredients,
        avoid,
        p,
    )
    output = output_recommended_recipes(recommendation_dataframe)
    if output is None:
        return PredictionOut(output=None)
    return PredictionOut(output=output)


@app.get("/")
@app.get("/health")
def health():
    return {"health_check": "OK"}


@app.post("/predict/", response_model=PredictionOut)
def update_item(prediction_input: PredictionIn):
    return _predict(prediction_input)
