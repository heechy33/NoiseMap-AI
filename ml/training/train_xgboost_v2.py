"""
Extended XGBoost training that adds time-of-day features (hour, weekend flag).

Features (7):
    - airport_score, nightlife_score, bus_score, train_score, density (same as v1)
    - hour:    current hour of day (0–23)
    - weekend: 1 if weekend, 0 if weekday

This version processes rows one at a time (slower) but enables time-aware prediction.
For faster batch processing, use train_xgboost.py instead.
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.feature import (
    estimate_city_density,
    nightlife_score_estimate,
    distance_to_nearest_airport,
    distance_to_nearest_bus,
    distance_to_nearest_train,
)

DB_PATH = os.getenv("NOISEMAP_DB", "D:/noiseMap_sql_data_copy/noisemap.db")
MODEL_OUTPUT = os.getenv("MODEL_OUTPUT", "noise_model_timeaware.pkl")
CHUNK_SIZE = 100_000
SAMPLE_LIMIT = 5_000_000
ROW_LIMIT = 30_000_000


def get_time_features():
    now = datetime.now()
    return now.hour, int(now.weekday() >= 5)


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

        chunk = pd.read_sql_query(
            f"SELECT lat, lng, noise_level FROM data LIMIT {CHUNK_SIZE} OFFSET {offset}",
            conn,
        )
        if chunk.empty:
            break

        chunk = chunk.dropna()

        for lat, lng, noise in chunk.values.tolist():
            total_seen += 1
            if total_seen > ROW_LIMIT:
                break

            airport = distance_to_nearest_airport(lat, lng)
            nightlife = nightlife_score_estimate(lat, lng)
            bus = distance_to_nearest_bus(lat, lng)
            train = distance_to_nearest_train(lat, lng)
            density = estimate_city_density(lat, lng)
            hour, weekend = get_time_features()

            x = [airport, nightlife, bus, train, density, hour, weekend]

            if len(X_sample) < SAMPLE_LIMIT:
                X_sample.append(x)
                y_sample.append(noise)
            else:
                i = np.random.randint(0, total_seen)
                if i < SAMPLE_LIMIT:
                    X_sample[i] = x
                    y_sample[i] = noise

        offset += CHUNK_SIZE
        if offset % 1_000_000 == 0:
            print(f"Processed {offset:,} rows...")

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
