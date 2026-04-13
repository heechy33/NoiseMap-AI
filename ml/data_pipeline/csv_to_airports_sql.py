"""
Converts the OurAirports airports.csv into a SQLite database.

Input:  airports.csv (from https://ourairports.com/data/)
Output: new_airports.db with an `airports` table (name, lat, lng)

Only large and medium airports with scheduled service are retained.
"""

import os
import sqlite3
import pandas as pd

CSV_FILE = os.getenv("AIRPORTS_CSV", "data/airports.csv")
OUTPUT_DB = os.getenv("AIRPORTS_DB", "data/databases/new_airports.db")
TABLE_NAME = "airports"

df = pd.read_csv(CSV_FILE)
df = df.rename(columns={"latitude_deg": "lat", "longitude_deg": "lng"})
df = df[
    df["type"].isin(["large_airport", "medium_airport"])
    & (df["scheduled_service"].str.lower() == "yes")
    & df["lat"].notnull()
    & df["lng"].notnull()
][["name", "lat", "lng"]]

os.makedirs(os.path.dirname(OUTPUT_DB), exist_ok=True)

conn = sqlite3.connect(OUTPUT_DB)
cursor = conn.cursor()
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        lat REAL,
        lng REAL
    )
""")
cursor.execute(f"DELETE FROM {TABLE_NAME}")
cursor.executemany(
    f"INSERT INTO {TABLE_NAME} (name, lat, lng) VALUES (?, ?, ?)",
    df[["name", "lat", "lng"]].values.tolist(),
)
conn.commit()
conn.close()

print(f"Inserted {len(df):,} airports into {OUTPUT_DB}")
