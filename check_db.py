import sqlite3, time, numpy as np
from scipy.spatial import KDTree

dbs = {
    "bus": r"D:\noiseMap_sql_data_copy\bus_station.db",
    "train": r"D:\noiseMap_sql_data_copy\train_station.db",
    "nightlife": r"D:\noiseMap_sql_data_copy\night_life.db",
    "airports": r"D:\noiseMap_sql_data_copy\new_airports.db",
}

for name, path in dbs.items():
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    for (table,) in tables:
        try:
            c.execute(f"SELECT COUNT(*) FROM {table}")
            count = c.fetchone()[0]
            print(f"{name} / {table}: {count:,} rows")
        except Exception as e:
            print(f"{name} / {table}: ERROR {e}")
    conn.close()

print()
print("Testing KDTree build on bus_station...")
t0 = time.time()
conn = sqlite3.connect(dbs["bus"])
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
table = c.fetchone()[0]
print(f"  Reading coords from {table}...")
c.execute(f"SELECT lat, lng FROM {table}")
coords = np.array(c.fetchall())
conn.close()
print(f"  Loaded {len(coords):,} rows in {time.time()-t0:.1f}s")
t1 = time.time()
tree = KDTree(np.radians(coords))
print(f"  KDTree built in {time.time()-t1:.1f}s")
