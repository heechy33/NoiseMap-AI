"""
Extracts POIs (train stations, bus stops, nightlife) from OpenStreetMap .pbf files
and stores them in SQLite databases using pyrosm.

Requires: pyrosm, shapely, tqdm
"""

import os
import sqlite3
import logging
from pyrosm import OSM
from shapely.geometry import Point
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("pbf_to_sql.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

PBF_DIR = os.getenv("PBF_DIR", "D:/Bars_nightlife")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "D:/World_sql")
COUNTRY = os.getenv("COUNTRY", "Unknown")

CATEGORIES = {
    "train_station": {
        "tag_key": "railway",
        "tag_values": ["station", "halt", "tram_stop"],
        "output": os.path.join(OUTPUT_DIR, "train_station.db"),
    },
    "bus_station": {
        "tag_key": "highway",
        "tag_values": ["bus_stop", "bus_station"],
        "output": os.path.join(OUTPUT_DIR, "bus_station.db"),
    },
    "night_life": {
        "tag_key": "amenity",
        "tag_values": ["bar", "pub", "nightclub"],
        "output": os.path.join(OUTPUT_DIR, "night_life.db"),
    },
}


def extract_and_store(pbf_path, db_path, tag_key, tag_values, country, city):
    logger.info(f"Extracting {tag_key}={tag_values} from {os.path.basename(pbf_path)}")
    try:
        osm = OSM(pbf_path)
        custom_filter = {tag_key: tag_values}
        pois = osm.get_data_by_custom_criteria(
            custom_filter=custom_filter,
            filter_type="keep",
            keep_nodes=True,
            keep_ways=False,
            keep_relations=False,
            tags_as_columns=[tag_key, "name"],
        )

        if pois is None or pois.empty:
            logger.warning(f"No data found in {pbf_path} for {tag_key}")
            return

        pois = pois.to_crs(epsg=4326)
        records = []
        for row in tqdm(pois.itertuples(), total=len(pois), desc="Saving records"):
            geom = row.geometry
            if isinstance(geom, Point):
                records.append((
                    getattr(row, "name", "Unnamed"),
                    geom.y,
                    geom.x,
                    getattr(row, tag_key, "unknown"),
                    country,
                    city,
                ))

        if not records:
            logger.warning("No valid Point geometry records found.")
            return

        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                lat REAL,
                lng REAL,
                tag TEXT,
                country TEXT,
                city TEXT
            )
        """)
        cursor.executemany(
            "INSERT INTO data (name, lat, lng, tag, country, city) VALUES (?, ?, ?, ?, ?, ?)",
            records,
        )
        conn.commit()
        conn.close()
        logger.info(f"Inserted {len(records):,} records into {os.path.basename(db_path)}")

    except Exception as e:
        logger.error(f"Error processing {os.path.basename(pbf_path)}: {e}")


if __name__ == "__main__":
    files = [f for f in os.listdir(PBF_DIR) if f.endswith(".pbf")]
    if not files:
        logger.error("No .pbf files found in PBF_DIR.")
        exit(1)

    for file in files:
        pbf_path = os.path.join(PBF_DIR, file)
        city = os.path.splitext(file)[0].replace("-", " ").capitalize()
        for cat, cfg in CATEGORIES.items():
            extract_and_store(
                pbf_path=pbf_path,
                db_path=cfg["output"],
                tag_key=cfg["tag_key"],
                tag_values=cfg["tag_values"],
                country=COUNTRY,
                city=city,
            )
