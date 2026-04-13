"""
Inserts GeoJSON point features into category-specific SQLite databases.

Expects GeoJSON files named with category keywords: train_station, bus_station, night_life.
Output databases: train_station.db, bus_station.db, night_life.db
"""

import os
import json
import sqlite3
from glob import glob

FOLDER = os.getenv("GEOJSON_SQL_DIR", "D:/World_sql")

CATEGORY_MAP = {
    "train_station": "train_station.db",
    "bus_station": "bus_station.db",
    "night_life": "night_life.db",
}

TABLES = {
    "train_station": "train_station",
    "bus_station": "bus_station",
    "night_life": "nightlife",
}


def create_table_if_not_exists(conn, table_name):
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL,
            lng REAL
        )
    """)
    conn.commit()


def insert_geojson_points(db_path, table_name, geojson_path):
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    points = []
    for feature in data["features"]:
        coords = feature["geometry"]["coordinates"]
        lng, lat = coords
        points.append((lat, lng))

    conn = sqlite3.connect(db_path)
    create_table_if_not_exists(conn, table_name)
    conn.executemany(
        f"INSERT INTO {table_name} (lat, lng) VALUES (?, ?)", points
    )
    conn.commit()
    conn.close()

    print(f"Inserted {len(points):,} points from {os.path.basename(geojson_path)} into {os.path.basename(db_path)}")


def main():
    all_files = glob(os.path.join(FOLDER, "*.geojson"))
    for geojson_file in all_files:
        for category, db_name in CATEGORY_MAP.items():
            if category in os.path.basename(geojson_file):
                db_path = os.path.join(FOLDER, db_name)
                insert_geojson_points(db_path, TABLES[category], geojson_file)


if __name__ == "__main__":
    main()
