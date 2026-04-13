"""
Enriches the noisemap.db `data` table with precomputed feature scores.

Adds airport_distance_km, nightlife_score, bus_station_distance_km, and
train_station_distance_km columns by running proximity lookups against
the feature SQLite databases.

Supports resuming via a checkpoint file.
"""

import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.feature import (
    distance_to_nearest_airport,
    nightlife_score_estimate,
    distance_to_nearest_bus,
    distance_to_nearest_train,
)

DB_PATH = os.getenv("NOISEMAP_DB", "D:/noiseMap_sql_data_copy/noisemap.db")
CHECKPOINT_FILE = "update_checkpoint.txt"
BATCH_SIZE = 10_000
NUM_WORKERS = 8

start_rowid = 0
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        try:
            start_rowid = int(f.read().strip())
            print(f"Resuming from rowid > {start_rowid}...")
        except ValueError:
            pass

conn = sqlite3.connect(DB_PATH, timeout=60)
cursor = conn.cursor()
conn.execute("PRAGMA journal_mode=WAL")

total_updated = 0

while True:
    cursor.execute(
        "SELECT rowid, lat, lng FROM data WHERE rowid > ? ORDER BY rowid LIMIT ?",
        (start_rowid, BATCH_SIZE),
    )
    batch = cursor.fetchall()
    if not batch:
        break

    updates = []
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {
            executor.submit(
                lambda r: (
                    r[0],
                    distance_to_nearest_airport(r[1], r[2]),
                    nightlife_score_estimate(r[1], r[2]),
                    distance_to_nearest_bus(r[1], r[2]),
                    distance_to_nearest_train(r[1], r[2]),
                ),
                row,
            ): row
            for row in batch
        }

        for future in as_completed(futures):
            row = futures[future]
            try:
                rowid, airport, nightlife, bus, train = future.result()
                updates.append((airport, nightlife, bus, train, rowid))
            except Exception as e:
                print(f"Skipped row {row[0]}: {e}")

    if updates:
        cursor.executemany(
            """
            UPDATE data
            SET
                airport_distance_km = ?,
                nightlife_score = ?,
                bus_station_distance_km = ?,
                train_station_distance_km = ?
            WHERE rowid = ?
            """,
            updates,
        )
        conn.commit()
        total_updated += len(updates)
        last_rowid = updates[-1][-1]
        start_rowid = last_rowid
        print(f"Updated {total_updated:,} rows. Last rowid = {last_rowid}")

        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(last_rowid))

conn.close()
print(f"Done. Total updated: {total_updated:,}")
