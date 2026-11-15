# Is Anyone There? — Room Occupancy Estimation

## Live Demo

- **App (Streamlit):** https://is-anyone-there.streamlit.app/
- **API docs (FastAPI):** https://room-occupancy-api-7gja.onrender.com/docs

> The demo runs on free hosting. If it has been idle, the first load can take about a minute while the API wakes up.
> This is a research/demo prototype and should not be used for automatic room-availability decisions.

Estimate **how many people (0, 1, 2 or 3) are in a room** from sensor readings only: temperature, light, sound level, CO₂ and motion. **No cameras and no audio recordings.**

> **Research/demo prototype.** This is not a reliable system for deciding room availability automatically. See [Results and limitations](#results-and-limitations).

## Why this project?

Meeting, study and co-working rooms are often booked but nobody shows up, or people leave early. Knowing whether a room is really in use helps. This project predicts the **number of people** in a room. Connecting it to an actual booking system is a possible future extension and is **not** part of the current version.

## What is in this repo

- **Notebook:** EDA, preprocessing, modeling, evaluation and final model selection.
- **FastAPI service:** `GET /health`, `POST /predict` and interactive docs at `/docs`.
- **Streamlit app:** a small game. Read the sensor "clues", guess how many people are in the room, then see if you can beat the AI. English and Arabic.
- **Tests:** API tests, including checks against real dataset rows.
- **Saved model:** the fitted pipeline in `models/`.

## Model

- **Model:** tuned Logistic Regression, **Feature Set C** (all 16 sensor features).
- **Pipeline:** `StandardScaler` + `LogisticRegression` saved together in one fitted scikit-learn `Pipeline` (`class_weight="balanced"`, `max_iter=2000`, `random_state=42`, `C=1.0129197956845732`).
- **Training data:** December 2017 only (8,084 samples).
- **Classes:** 0, 1, 2, 3 people.
- **Features (in order):** `S1_Temp`, `S2_Temp`, `S3_Temp`, `S4_Temp`, `S1_Light`, `S2_Light`, `S3_Light`, `S4_Light`, `S1_Sound`, `S2_Sound`, `S3_Sound`, `S4_Sound`, `S5_CO2`, `S5_CO2_Slope`, `S6_PIR`, `S7_PIR`. The order is stored in `models/features.joblib`.
- Date and time are **not** model inputs.

## Results and limitations

- **Data:** UCI *Room Occupancy Estimation*, 10,129 samples. About 81% of the readings are an empty room.
- **Split:** December 2017 for training (8,084 samples) and January 2018 for testing (2,045 samples). January contains 1,751 empty, **0 one-person**, 93 two-person and 201 three-person readings.
- **December validation:** Logistic Regression with Feature Set C had the highest time-aware CV Macro F1 (about 0.553) and the highest forward-day Macro F1 (0.9905).
- **January (descriptive):** the final model reached Macro F1 = 0.4212 and **missed 184 of 294 occupied readings (62.59%)**. Many January occupied readings have very low light, which was rare in the training data.
- **January scores are descriptive, not an untouched final test.** The January set was scored several times while comparing models. It contains one short occupied session and no one-person readings.
- Feature Set C is not the best choice in every setting, and no model was best on every criterion.

This is why the app is a research/demo prototype and must not be used to decide room availability automatically.

## Project structure

```
room-occupancy-estimation/
├── app/
│   ├── __init__.py
│   └── main.py               # FastAPI service
├── data/
│   └── examples.csv          # real labelled rows used by the app and tests
├── models/
│   ├── model.joblib          # fitted Pipeline (StandardScaler + LogisticRegression)
│   ├── features.joblib       # ordered feature names
│   ├── metadata.json
│   ├── example_input.json
│   └── example_output.json
├── notebooks/                # project notebook
├── scripts/
│   └── make_examples.py      # builds data/examples.csv from the dataset
├── tests/
│   ├── test_api.py
│   └── test_real_samples.py
├── streamlit_app.py          # Streamlit game
├── requirements.txt
├── pytest.ini
└── README.md
```

## Run locally

Python **3.13** is recommended. The model was saved with scikit-learn 1.6.1, so `requirements.txt` pins the same versions.

**1. Create and activate a virtual environment** (from the project root)

```powershell
# Windows PowerShell
py -3.13 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   # this terminal window only
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3.13 -m venv .venv
source .venv/bin/activate
```

**2. Install the dependencies**

```
python -m pip install -r requirements.txt
```

**3. Start the API** (terminal 1)

```
python -m uvicorn app.main:app
```

Open http://127.0.0.1:8000/docs (interactive docs) and http://127.0.0.1:8000/health.

**4. Start the app** (terminal 2: activate the same environment again)

```
python -m streamlit run streamlit_app.py
```

Open http://localhost:8501. The app reads the API address from the `API_URL` environment variable (default `http://127.0.0.1:8000`).

**5. Run the tests**

```
python -m pytest -q
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service and model status |
| POST | `/predict` | Predict the number of people |
| GET | `/docs` | Interactive API documentation |

`POST /predict` expects all 16 numeric features. Missing fields, unknown fields and invalid values (text, null, NaN, negative light/sound/CO₂, PIR other than 0 or 1) are rejected with HTTP 422.

Example request body (`models/example_input.json`):

```json
{
  "S1_Temp": 24.94, "S2_Temp": 24.75, "S3_Temp": 24.56, "S4_Temp": 25.38,
  "S1_Light": 121.0, "S2_Light": 34.0, "S3_Light": 53.0, "S4_Light": 40.0,
  "S1_Sound": 0.08, "S2_Sound": 0.19, "S3_Sound": 0.06, "S4_Sound": 0.06,
  "S5_CO2": 390.0, "S5_CO2_Slope": 0.769230769231,
  "S6_PIR": 0.0, "S7_PIR": 0.0
}
```

Example response (`models/example_output.json`):

```json
{
  "count": 1,
  "occupied": true,
  "probabilities": {"0": 0.0035, "1": 0.9958, "2": 0.0006, "3": 0.0}
}
```

## Data

- Source: [UCI Machine Learning Repository: Room Occupancy Estimation](https://archive.ics.uci.edu/dataset/864/room+occupancy+estimation) (also on [Kaggle](https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation)).
- To rebuild `data/examples.csv` from the original dataset: `python scripts/make_examples.py` (needs internet).
- In the app, every example shows whether it comes from the December (training) or January (test) period, and the true count is shown only for the original, unedited sample.

## Security note

`.joblib` files can run code when loaded. Only load model files you trust, such as the ones in this repo.