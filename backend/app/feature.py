import os
import sqlite3
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from math import radians, sin, cos, sqrt, atan2, log1p


DB_DIR = os.getenv("NOISE_DB_DIR", "data/databases")

_default_cities_csv = os.path.join(os.path.dirname(__file__), "worldcities.csv")
CITIES_CSV = os.getenv("CITIES_CSV_PATH", _default_cities_csv)

DBS = {
    "airports": os.path.join(DB_DIR, "new_airports.db"),
    "nightlife": os.path.join(DB_DIR, "night_life.db"),
    "bus": os.path.join(DB_DIR, "bus_station.db"),
    "train": os.path.join(DB_DIR, "train_station.db"),
}

cities_df = pd.read_csv(CITIES_CSV)
cities_df = cities_df.dropna(subset=["lat", "lng", "population"])
city_tree = KDTree(cities_df[["lat", "lng"]].values)


_nightlife_conn = sqlite3.connect(DBS["nightlife"])
_nightlife_cursor = _nightlife_conn.cursor()
_nightlife_table = None
_nightlife_coords = []

for row in _nightlife_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    table = row[0]
    _nightlife_cursor.execute(f"PRAGMA table_info({table})")
    cols = [col[1].lower() for col in _nightlife_cursor.fetchall()]
    if "lat" in cols and "lng" in cols:
        _nightlife_table = table
        break

if _nightlife_table:
    for row in _nightlife_cursor.execute(f"SELECT lat, lng FROM {_nightlife_table}"):
        _nightlife_coords.append(row)
    _nightlife_tree = KDTree(np.radians(_nightlife_coords)) if _nightlife_coords else None
else:
    _nightlife_tree = None


_feature_trees = {}
for key in ["airports", "bus", "train"]:
    path = DBS[key]
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in [r[0] for r in cursor.fetchall()]:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [col[1].lower() for col in cursor.fetchall()]
        if "lat" in cols and "lng" in cols:
            cursor.execute(f"SELECT lat, lng FROM {table}")
            coords = cursor.fetchall()
            if coords:
                _feature_trees[key] = KDTree(np.radians(coords))
            break
    conn.close()


def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def estimate_city_density(lat, lng):
    _, idx = city_tree.query([lat, lng])
    city = cities_df.iloc[idx]
    pop = city["population"]
    area_km2 = max((pop ** 0.5) / 2, 3)
    return round(pop / area_km2, 2)


def proximity_score_km(lat, lng, db_key, max_km):
    tree = _feature_trees.get(db_key)
    if not tree:
        return 0.0
    dist_rad, _ = tree.query(np.radians([lat, lng]))
    dist_km = dist_rad * 6371
    return round(max(0, 1 - dist_km / max_km), 3)


def distance_to_nearest_airport(lat, lng):
    return proximity_score_km(lat, lng, "airports", 20)


def distance_to_nearest_bus(lat, lng):
    return proximity_score_km(lat, lng, "bus", 1)


def distance_to_nearest_train(lat, lng):
    return proximity_score_km(lat, lng, "train", 3)


def batch_proximity_score(lat_arr, lng_arr, db_key, max_km):
    tree = _feature_trees.get(db_key)
    if not tree:
        return np.zeros(len(lat_arr))
    coords_rad = np.radians(np.column_stack([lat_arr, lng_arr]))
    dist_rad, _ = tree.query(coords_rad)
    dist_km = dist_rad * 6371
    return np.round(np.clip(1 - dist_km / max_km, 0, 1), 3)


def nightlife_score_estimate(lat, lng, radius_km=2.0):
    if not _nightlife_tree:
        return 1.0
    latlng_rad = np.radians([lat, lng])
    idxs = _nightlife_tree.query_ball_point(latlng_rad, radius_km / 6371)
    raw_score = len(idxs)
    adjusted = min(log1p(raw_score), 10.0)
    return round(1.0 + 9.0 * (adjusted / 10.0), 1)
