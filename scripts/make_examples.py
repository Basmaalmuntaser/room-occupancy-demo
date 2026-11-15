"""Build data/examples.csv: a small set of REAL rows from the Room Occupancy dataset.

Run once from the project root:   python scripts/make_examples.py
(Needs internet. The model is NOT retrained - we only read it to store a reference prediction.)

Each row keeps its documented ground truth (Room_Occupancy_Count), its timestamp, and its source
period, so the UI never mixes up December (training period) and January (test period).
"""
import argparse
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
URL = "https://archive.ics.uci.edu/static/public/864/room+occupancy+estimation.zip"
TARGET = "Room_Occupancy_Count"
SEED = 42
PER_CLASS = 3  # examples per (period, class)

parser = argparse.ArgumentParser()
parser.add_argument("--source", default=URL, help="URL or local path of the dataset zip/csv")
args = parser.parse_args()

features = list(joblib.load(ROOT / "models" / "features.joblib"))
model = joblib.load(ROOT / "models" / "model.joblib")

df = pd.read_csv(args.source, compression="zip" if str(args.source).endswith(".zip") else "infer")
print(f"Loaded {len(df):,} rows x {df.shape[1]} columns")

missing = [c for c in features + [TARGET, "Date", "Time"] if c not in df.columns]
assert not missing, f"Missing columns in dataset: {missing}"
assert df[features + [TARGET]].notna().all().all(), "Unexpected missing values"

df["datetime"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Time"].astype(str))
is_dec = (df["datetime"].dt.year == 2017) & (df["datetime"].dt.month == 12)
is_jan = (df["datetime"].dt.year == 2018) & (df["datetime"].dt.month == 1)
df.loc[is_dec, "source"] = "December 2017 (training period)"
df.loc[is_jan, "source"] = "January 2018 (test period)"
df = df.dropna(subset=["source"])

print("\nRows per period / class:")
print(df.groupby(["source", TARGET]).size().unstack(fill_value=0))
print(f"\nDecember: {is_dec.sum():,} rows (expected 8,084) | January: {is_jan.sum():,} rows (expected 2,045)")

parts = []
for (source, cls), group in df.groupby(["source", TARGET]):
    parts.append(group.sample(n=min(PER_CLASS, len(group)), random_state=SEED))
examples = pd.concat(parts).sort_values(["source", TARGET, "datetime"]).reset_index(drop=True)

# Reference prediction from the saved Pipeline (used by tests to catch accidental model changes).
examples["reference_prediction"] = model.predict(examples[features]).astype(int)
examples.insert(0, "sample_id", [f"ex{i + 1:02d}" for i in range(len(examples))])
examples = examples.rename(columns={TARGET: "actual_count"})

cols = ["sample_id", "source", "datetime", *features, "actual_count", "reference_prediction"]
out = ROOT / "data" / "examples.csv"
out.parent.mkdir(exist_ok=True)
examples[cols].to_csv(out, index=False)
print(f"\nSaved {len(examples)} examples -> {out}")
print(examples.groupby(["source", "actual_count"]).size())