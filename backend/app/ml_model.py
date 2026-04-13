import os
import joblib
from app.feature import (
    distance_to_nearest_airport,
    nightlife_score_estimate,
    distance_to_nearest_bus,
    distance_to_nearest_train,
    estimate_city_density,
)

MODEL_PATH = os.getenv("MODEL_PATH", "app/shuffled_noise_model.pkl")
model = joblib.load(MODEL_PATH)

COLOR_SCALE = {
    "airport": "#f39c12",
    "nightlife": "#e74c3c",
    "bus": "#27ae60",
    "train": "#2980b9",
    "density": "#8e44ad",
}


def predict_noise_score(lat: float, lng: float) -> dict:
    airport = distance_to_nearest_airport(lat, lng)
    nightlife = nightlife_score_estimate(lat, lng)
    bus = distance_to_nearest_bus(lat, lng)
    train = distance_to_nearest_train(lat, lng)
    density = estimate_city_density(lat, lng)

    features = [airport, nightlife, bus, train, density]
    raw_score = float(model.predict([features])[0])
    score = round(max(1.0, min(10.0, raw_score)), 1)

    # Normalize all features to a 0–10 display scale
    display_values = [
        round(airport * 10, 1),
        round(nightlife, 1),
        round(bus * 10, 1),
        round(train * 10, 1),
        round(min(density / 10000.0 * 10, 10.0), 1),
    ]

    labels = ["Airport", "Nightlife", "Bus", "Train", "Population Density"]
    colors = [
        COLOR_SCALE["airport"],
        COLOR_SCALE["nightlife"],
        COLOR_SCALE["bus"],
        COLOR_SCALE["train"],
        COLOR_SCALE["density"],
    ]

    top_feature = max(
        zip(["airport", "nightlife", "bus", "train", "density"], display_values),
        key=lambda x: x[1],
    )[0]

    reasons = {
        "airport": "near an airport flight path",
        "nightlife": "active nightlife area",
        "bus": "near a busy bus corridor",
        "train": "near a train or subway station",
        "density": "dense urban center",
    }

    factors = [
        {"label": label, "value": value, "color": color}
        for label, value, color in zip(labels, display_values, colors)
    ]

    return {
        "score": score,
        "reason": reasons[top_feature],
        "factors": factors,
        "raw": {
            "airport": airport,
            "nightlife": nightlife,
            "bus": bus,
            "train": train,
            "density": density,
        },
    }
