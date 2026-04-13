# NoiseMap AI

An interactive web app that lets you search any location in the world and instantly see its noise score (1–10). Designed for travelers, renters, homebuyers, and real estate agents who want to evaluate a location's noise environment before committing.

## How It Works

NoiseMap AI calculates a noise score using a trained XGBoost regression model. The model was trained on 5 million crowd-sourced noise measurements from the [NoiseCapture](https://noise-planet.org/noisecapture.html) dataset (MAE: 12.6 dB, R²: 0.41) and uses five geospatial features:

- **Airport proximity** — distance to the nearest large or medium airport
- **Nightlife density** — count of bars, pubs, and nightclubs within 2 km
- **Bus proximity** — distance to the nearest bus stop
- **Train proximity** — distance to the nearest train or subway station
- **Population density** — estimated density of the surrounding urban area

Each location also receives an AI-generated summary (powered by Gemini) explaining the likely noise sources in plain language.

## Project Structure

```
noisemap-ai/
├── backend/                  # FastAPI server
│   ├── app/
│   │   ├── feature.py        # Geospatial feature extraction (SQLite + KDTree)
│   │   ├── ml_model.py       # XGBoost model loading and inference
│   │   ├── location_insight.py  # Gemini AI location summaries
│   │   └── routes.py         # API endpoints
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # React app
│   └── src/
│       └── components/
│           ├── MapPage.jsx         # Mapbox 3D map
│           ├── LocationPopup.jsx   # Score popup panel
│           ├── ScoreAnalysis.jsx   # Factor breakdown chart
│           ├── LocationInsight.jsx # AI-generated summary
│           └── ...
└── ml/                       # ML pipeline (data collection + training)
    ├── data_pipeline/        # Scripts to build feature databases
    ├── training/             # XGBoost training scripts
    └── README.md             # Full ML setup guide
```

## Tech Stack

- **Frontend:** React, Mapbox GL JS, Google Maps Places API
- **Backend:** FastAPI, XGBoost, scikit-learn, SciPy (KDTree)
- **AI:** Google Gemini
- **Data:** NoiseCapture (crowd-sourced noise), OpenStreetMap, OurAirports

## Prerequisites

The backend requires three external dependencies that are not included in this repository:

1. **SQLite feature databases** — built from OpenStreetMap data using the scripts in `ml/data_pipeline/`. See `ml/README.md` for instructions.
2. **Trained model file** — `shuffled_noise_model.pkl`, produced by `ml/training/train_xgboost.py`.
3. **`worldcities.csv`** — available from [simplemaps.com/data/world-cities](https://simplemaps.com/data/world-cities).

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your paths and API keys
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
# Create a .env file with:
# REACT_APP_MAPBOX_TOKEN=your_mapbox_token
# REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_key
npm start
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/noise` | Returns noise score, reason, and factor breakdown |
| GET | `/score_analysis` | Returns individual feature scores |
| GET | `/location_insight` | Returns Gemini-generated area summary |

## Environment Variables

**Backend (`.env`):**

| Variable | Description |
|---|---|
| `NOISE_DB_DIR` | Directory containing the SQLite feature databases |
| `CITIES_CSV_PATH` | Path to `worldcities.csv` |
| `MODEL_PATH` | Path to the trained `.pkl` model file |
| `GEMINI_API_KEY` | Google Gemini API key |

**Frontend (`.env`):**

| Variable | Description |
|---|---|
| `REACT_APP_MAPBOX_TOKEN` | Mapbox public access token |
| `REACT_APP_GOOGLE_MAPS_API_KEY` | Google Maps API key (Places + Geocoding) |
