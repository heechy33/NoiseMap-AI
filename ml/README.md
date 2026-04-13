# ML Pipeline

This directory contains the data collection, processing, and model training scripts used to build the XGBoost noise prediction model for NoiseMap AI.

## Overview

The model predicts an environmental noise score (1–10) for any GPS coordinate using five features derived from geospatial data:

| Feature | Source | Description |
|---|---|---|
| Airport proximity | OurAirports CSV | Proximity score to nearest large/medium airport (0–1) |
| Nightlife density | OpenStreetMap PBF | Count of bars, pubs, and nightclubs within 2 km (1–10) |
| Bus proximity | OpenStreetMap PBF | Proximity score to nearest bus stop (0–1) |
| Train proximity | OpenStreetMap PBF | Proximity score to nearest train/subway station (0–1) |
| Population density | WorldCities CSV | Estimated density of the nearest city (people/km²) |

Training data comes from the [NoiseCapture](https://noise-planet.org/noisecapture.html) open dataset (~20M+ crowd-sourced noise measurements). Training on a 5M reservoir sample achieved **MAE: 12.6 dB** and **R²: 0.41** on a held-out 10% test set.

## Directory Structure

```
ml/
├── data_pipeline/
│   ├── bulk_extract_noisecapture.py   # Parse NoiseCapture GeoJSON → SQLite
│   ├── csv_to_airports_sql.py         # OurAirports CSV → SQLite
│   ├── geojson_to_sql.py              # OSM GeoJSON exports → SQLite
│   ├── pbf_to_sql.py                  # OSM .pbf files → SQLite (via pyrosm)
│   └── enrich_bulk_data.py            # Add feature columns to noise dataset
└── training/
    ├── train_xgboost.py               # Primary training script (batch, fast)
    └── train_xgboost_v2.py            # Extended training with time-of-day features
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Collect data

**Noise measurements** — Download NoiseCapture exports from [noise-planet.org](https://noise-planet.org/noisecapture.html) and place `.geojson` files in your `GEOJSON_DIR`.

**Airport data** — Download `airports.csv` from [ourairports.com/data](https://ourairports.com/data/).

**OSM infrastructure data** — Download `.pbf` files for your target regions from [geofabrik.de](https://download.geofabrik.de/).

### 3. Build the feature databases

```bash
# Extract airport data
python data_pipeline/csv_to_airports_sql.py

# Extract train/bus/nightlife from OSM PBF files
python data_pipeline/pbf_to_sql.py

# Or from GeoJSON exports
python data_pipeline/geojson_to_sql.py

# Parse NoiseCapture data into noisemap.db
python data_pipeline/bulk_extract_noisecapture.py

# Enrich noisemap.db with feature scores
python data_pipeline/enrich_bulk_data.py
```

### 4. Train the model

```bash
export NOISEMAP_DB=/path/to/noisemap.db
export MODEL_OUTPUT=shuffled_noise_model.pkl
python training/train_xgboost.py
```

Place the output `.pkl` file in `backend/app/` and set `MODEL_PATH` in your `.env`.

## Environment Variables

| Variable | Description |
|---|---|
| `NOISEMAP_DB` | Path to the SQLite noise dataset |
| `NOISE_DB_DIR` | Directory containing feature databases |
| `GEOJSON_DIR` | Directory with NoiseCapture GeoJSON files |
| `AIRPORTS_CSV` | Path to OurAirports airports.csv |
| `PBF_DIR` | Directory with OSM .pbf files |
| `MODEL_OUTPUT` | Output path for the trained model |
