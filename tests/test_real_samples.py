"""Compare API output with the saved model on REAL dataset rows (data/examples.csv)."""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import FEATURES, app

ROOT = Path(__file__).resolve().parent.parent
examples = pd.read_csv(ROOT / "data" / "examples.csv")
model = joblib.load(ROOT / "models" / "model.joblib")
client = TestClient(app)


def model_input(payload: dict):
    values = [payload[name] for name in FEATURES]
    if hasattr(model, "feature_names_in_"):
        return pd.DataFrame([values], columns=FEATURES)
    return np.array([values])


def check_row(row: pd.Series) -> None:
    payload = {name: float(row[name]) for name in FEATURES}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    body = response.json()

    X = model_input(payload)
    expected_count = int(model.predict(X)[0])
    expected_proba = model.predict_proba(X)[0]

    assert body["count"] == expected_count
    assert body["count"] == int(row["reference_prediction"])
    assert body["occupied"] == (expected_count > 0)
    for cls, prob in zip(model.classes_, expected_proba):
        assert body["probabilities"][str(int(cls))] == pytest.approx(prob, abs=1e-4)


def first_example(period: str, actual_count: int) -> pd.Series:
    rows = examples[examples["source"].str.startswith(period) & (examples["actual_count"] == actual_count)]
    assert not rows.empty, f"No {period} example with actual count {actual_count}"
    return rows.iloc[0]


# Three real samples: one from December (class 1) and two from January (classes 0 and 3).
@pytest.mark.parametrize("period, actual_count", [("December", 1), ("January", 0), ("January", 3)])
def test_three_real_samples_match_model(period, actual_count):
    check_row(first_example(period, actual_count))


def test_all_examples_match_model():
    for _, row in examples.iterrows():
        check_row(row)


def test_january_examples_have_no_class_1():
    january = examples[examples["source"].str.startswith("January")]
    assert not january.empty
    assert 1 not in set(january["actual_count"])