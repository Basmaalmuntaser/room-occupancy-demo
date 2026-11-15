"""API tests for the room occupancy service. Run from the project root:  python -m pytest -v"""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import FEATURES, app

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
client = TestClient(app)


def load_json(name: str) -> dict:
    return json.loads((MODELS_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture
def example_input() -> dict:
    return load_json("example_input.json")


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["n_features"] == 16


def test_example_input_has_all_features_in_saved_order(example_input):
    assert list(example_input) == FEATURES


def test_predict_matches_saved_example(example_input):
    expected = load_json("example_output.json")
    response = client.post("/predict", json=example_input)
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == expected["count"]
    assert body["occupied"] == expected["occupied"]
    assert set(body["probabilities"]) == set(expected["probabilities"])
    for cls, prob in expected["probabilities"].items():
        assert body["probabilities"][cls] == pytest.approx(prob, abs=1e-4)


def test_probabilities_are_valid(example_input):
    body = client.post("/predict", json=example_input).json()
    assert set(body["probabilities"]) == {"0", "1", "2", "3"}
    assert sum(body["probabilities"].values()) == pytest.approx(1.0, abs=1e-3)
    assert body["occupied"] == (body["count"] > 0)


@pytest.mark.parametrize("feature", FEATURES)
def test_rejects_missing_field(example_input, feature):
    del example_input[feature]
    assert client.post("/predict", json=example_input).status_code == 422


def test_rejects_unknown_field(example_input):
    example_input["Unknown_Sensor"] = 1.0
    assert client.post("/predict", json=example_input).status_code == 422


@pytest.mark.parametrize(
    "feature, bad_value",
    [
        ("S1_Temp", "24.9"),   # text instead of a number
        ("S1_Temp", None),     # null
        ("S1_Temp", True),     # boolean
        ("S1_Temp", 500),      # impossible temperature
        ("S1_Light", -5),      # negative light
        ("S1_Sound", -0.1),    # negative sound
        ("S5_CO2", -10),       # negative CO2
        ("S6_PIR", 2),         # PIR must be 0 or 1
        ("S7_PIR", 0.5),       # PIR must be 0 or 1
    ],
)
def test_rejects_invalid_values(example_input, feature, bad_value):
    example_input[feature] = bad_value
    assert client.post("/predict", json=example_input).status_code == 422


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf")])
def test_rejects_nan_and_infinity(example_input, bad_value):
    example_input["S5_CO2"] = bad_value
    response = client.post(
        "/predict",
        content=json.dumps(example_input),  # Python writes NaN/Infinity as bare words
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 422


def test_rejects_non_json_body():
    response = client.post("/predict", content="not json", headers={"content-type": "application/json"})
    assert response.status_code == 422