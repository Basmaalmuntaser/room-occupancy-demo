"""FastAPI service for the "Is Anyone There?" room occupancy model.

Research/demo prototype - not a reliable system for automatic room-availability decisions.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# The saved Pipeline (StandardScaler + LogisticRegression) - no re-training, no separate scaling.
model = joblib.load(MODELS_DIR / "model.joblib")
FEATURES = list(joblib.load(MODELS_DIR / "features.joblib"))


class SensorReadings(BaseModel):
    """The 16 numeric sensor features. Missing, unknown or invalid fields are rejected (HTTP 422)."""

    model_config = ConfigDict(extra="forbid", strict=True)

    S1_Temp: float = Field(allow_inf_nan=False, ge=-50, le=100)
    S2_Temp: float = Field(allow_inf_nan=False, ge=-50, le=100)
    S3_Temp: float = Field(allow_inf_nan=False, ge=-50, le=100)
    S4_Temp: float = Field(allow_inf_nan=False, ge=-50, le=100)
    S1_Light: float = Field(allow_inf_nan=False, ge=0)
    S2_Light: float = Field(allow_inf_nan=False, ge=0)
    S3_Light: float = Field(allow_inf_nan=False, ge=0)
    S4_Light: float = Field(allow_inf_nan=False, ge=0)
    S1_Sound: float = Field(allow_inf_nan=False, ge=0)
    S2_Sound: float = Field(allow_inf_nan=False, ge=0)
    S3_Sound: float = Field(allow_inf_nan=False, ge=0)
    S4_Sound: float = Field(allow_inf_nan=False, ge=0)
    S5_CO2: float = Field(allow_inf_nan=False, ge=0, le=100000)
    S5_CO2_Slope: float = Field(allow_inf_nan=False)
    S6_PIR: float = Field(allow_inf_nan=False)
    S7_PIR: float = Field(allow_inf_nan=False)

    @field_validator("S6_PIR", "S7_PIR")
    @classmethod
    def pir_is_binary(cls, v: float) -> float:
        if v not in (0.0, 1.0):
            raise ValueError("PIR must be 0 or 1")
        return v


class PredictionResponse(BaseModel):
    count: int
    occupied: bool
    probabilities: dict[str, float]


# Fail fast if the API schema and the saved feature list ever drift apart.
if set(SensorReadings.model_fields) != set(FEATURES):
    raise RuntimeError("SensorReadings fields do not match models/features.joblib")

app = FastAPI(
    title="Is Anyone There? - Room Occupancy API",
    description="Predicts the number of people in a room (0-3) from sensor readings. "
    "Research/demo prototype - not for automatic room-availability decisions.",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return 422 with clean messages (never echo the rejected value, e.g. NaN, back in the JSON)."""
    details = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": details})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": True, "n_features": len(FEATURES)}


@app.post("/predict", response_model=PredictionResponse)
def predict(readings: SensorReadings) -> PredictionResponse:
    values = [getattr(readings, name) for name in FEATURES]  # order comes from features.joblib
    if hasattr(model, "feature_names_in_"):
        X = pd.DataFrame([values], columns=FEATURES)
    else:
        X = np.array([values])
    count = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]
    probabilities = {str(int(c)): round(float(p), 4) for c, p in zip(model.classes_, proba)}
    return PredictionResponse(count=count, occupied=count > 0, probabilities=probabilities)