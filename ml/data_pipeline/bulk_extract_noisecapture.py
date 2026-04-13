"""
Parses NoiseCapture GeoJSON exports and inserts clean samples into a SQLite database.

Usage:
    Place extracted .geojson files in GEOJSON_DIR, then run this script.
    Output: noisemap.db with a `data` table (lat, lng, noise_level, region).
"""

import os
import math
import sqlite3
import ijson
import random

GEOJSON_DIR = os.getenv("GEOJSON_DIR", "D:/NoiseData/extracted")
SQLITE_FILE = os.getenv("SQLITE_FILE", "noisemap.db")
ACCURACY_THRESHOLD = 13
BATCH_INSERT_SIZE = 10_000
MEMORY_SHUFFLE_CHUNK = 1_000

os.makedirs(os.path.dirname(SQLITE_FILE) or ".", exist_ok=True)

conn = sqlite3.connect(SQLITE_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lat REAL,
    lng REAL,
    noise_level REAL,
    region TEXT
)
""")
cursor.execute("DELETE FROM data")
conn.commit()

inserted = 0
skipped = 0
batch = []

geojson_files = []
for root, _, files in os.walk(GEOJSON_DIR):
    for filename in files:
        if filename.endswith(".geojson"):
            geojson_files.append(os.path.join(root, filename))
random.shuffle(geojson_files)

for path in geojson_files:
    filename = os.path.basename(path)
    region = "_".join(filename.split("_")[:2])
    print(f"Reading {filename}...")

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            features = ijson.items(f, "features.item")
            memory_buffer = []

            for feature in features:
                try:
                    geometry = feature.get("geometry", {})
                    props = feature.get("properties", {})

                    if geometry.get("type") != "Point":
                        continue
                    coords = geometry.get("coordinates", [])
                    if len(coords) < 2:
                        continue

                    lng_val, lat_val = coords[0], coords[1]
                    lat_val = float(lat_val)
                    lng_val = float(lng_val)

                    if (
                        math.isnan(lat_val) or math.isnan(lng_val)
                        or lat_val < -90 or lat_val > 90
                        or lng_val < -180 or lng_val > 180
                    ):
                        continue

                    if "noise_level" not in props or props["noise_level"] is None:
                        continue
                    if "accuracy" not in props or props["accuracy"] is None:
                        continue

                    accuracy = float(props["accuracy"])
                    if accuracy > ACCURACY_THRESHOLD:
                        continue

                    noise = float(props["noise_level"])
                    memory_buffer.append((lat_val, lng_val, noise, region))

                    if len(memory_buffer) >= MEMORY_SHUFFLE_CHUNK:
                        random.shuffle(memory_buffer)
                        batch.extend(memory_buffer)
                        memory_buffer = []

                        if len(batch) >= BATCH_INSERT_SIZE:
                            cursor.executemany(
                                "INSERT INTO data (lat, lng, noise_level, region) VALUES (?, ?, ?, ?)",
                                batch,
                            )
                            conn.commit()
                            inserted += len(batch)
                            print(f"Inserted {inserted:,} rows...")
                            batch = []

                except Exception:
                    skipped += 1

            if memory_buffer:
                random.shuffle(memory_buffer)
                batch.extend(memory_buffer)

    except Exception as e:
        print(f"Failed to process {filename}: {e}")
        continue

if batch:
    cursor.executemany(
        "INSERT INTO data (lat, lng, noise_level, region) VALUES (?, ?, ?, ?)", batch
    )
    conn.commit()
    inserted += len(batch)

conn.close()
print(f"Done: {inserted:,} rows inserted, {skipped:,} rows skipped.")
