"""
Trains an XGBoost regression model to predict environmental noise levels (dB).

Features (5):
    - airport_score:   proximity to nearest airport (0–1)
    - nightlife_score: density of nightlife venues within 2 km (1–10)
    - bus_score:       proximity to nearest bus station (0–1)
    - train_score:     proximity to nearest train station (0–1)
    - density:         estimated population density of the nearest city

Target:
    - noise_level: ambient noise in dB from NoiseCapture dataset

Usage:
    Set NOISEMAP_DB to the path of noisemap.db, then run:
        python train_xgboost.py
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.feature import (
    estimate_city_density,
    nightlife_score_estimate,
    batch_proximity_score,
)

DB_PATH = os.getenv("NOISEMAP_DB", "D:/noiseMap_sql_data_copy/noisemap.db")
MODEL_OUTPUT = os.getenv("MODEL_OUTPUT", "shuffled_noise_model.pkl")
CHUNK_SIZE = 10_000
SAMPLE_LIMIT = 5_000_000
ROW_LIMIT = 20_000_000

X_sample = []
y_sample = []
total_seen = 0

print("Streaming and sampling from database...")

with sqlite3.connect(DB_PATH) as conn:
    offset = 0
    while True:
        if total_seen >= ROW_LIMIT:
            print(f"Stopping after {ROW_LIMIT:,} rows.")
            break
        if len(X_sample) >= SAMPLE_LIMIT:
            print(f"Reached sampling cap: {SAMPLE_LIMIT:,} rows.")
            break

        chunk = pd.read_sql_query(
            f"SELECT lat, lng, noise_level FROM data LIMIT {CHUNK_SIZE} OFFSET {offset}",
            conn,
        )
        if chunk.empty:
            break

        chunk = chunk.dropna()
        rows = chunk.values.tolist()

        lats = [r[0] for r in rows]
        lngs = [r[1] for r in rows]
        noises = [r[2] for r in rows]

        try:
            airport_arr = batch_proximity_score(lats, lngs, "airports", 20)
            bus_arr = batch_proximity_score(lats, lngs, "bus", 1)
            train_arr = batch_proximity_score(lats, lngs, "train", 3)
            density_arr = [estimate_city_density(lat, lng) for lat, lng in zip(lats, lngs)]
            nightlife_arr = [nightlife_score_estimate(lat, lng) for lat, lng in zip(lats, lngs)]

            for i in range(len(rows)):
                total_seen += 1
                if total_seen % 10_000 == 0:
                    print(f"Seen: {total_seen:,} | Sampled: {len(X_sample):,}")

                x = [airport_arr[i], nightlife_arr[i], bus_arr[i], train_arr[i], density_arr[i]]
                y = noises[i]

                if len(X_sample) < SAMPLE_LIMIT:
                    X_sample.append(x)
                    y_sample.append(y)
                else:
                    j = np.random.randint(0, total_seen)
                    if j < SAMPLE_LIMIT:
                        X_sample[j] = x
                        y_sample[j] = y

        except Exception as e:
            print(f"Batch error at offset {offset}: {e}")

        offset += CHUNK_SIZE

print(f"Sampled {len(y_sample):,} rows from {total_seen:,} total.")

X = np.array(X_sample)
y = np.array(y_sample)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

print("Training XGBoost model...")
model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    n_jobs=-1,
    verbosity=1,
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE:  {mae:.2f} dB")
print(f"R²:   {r2:.4f}")

joblib.dump(model, MODEL_OUTPUT)
print(f"Model saved to {MODEL_OUTPUT}")
