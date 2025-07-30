from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from app.nightlife_score import compute_places_factors
from app.location_insight import get_location_summary

router = APIRouter()



class NoiseFactor(BaseModel):
    label: str
    value: float
    color: str

class NoiseScoreResponse(BaseModel):
    location: str
    lat: float
    lng: float
    score: float
    reason: str
    factors: List[NoiseFactor]


@router.get("/noise", response_model=NoiseScoreResponse)
def get_noise_score(
    lat: float = Query(...),
    lng: float = Query(...),
    location: str = Query("Unknown")
):
    scores = compute_places_factors(lat, lng)

    score = float(scores.get("combined_score", 1.0))
    reason = "Score based on nearby places (nightlife, airport, train, bus)"
    factors = [
        NoiseFactor(label="Nightlife", value=scores.get("nightlife", 0), color="#ff3366"),
        NoiseFactor(label="Airport", value=scores.get("airport", 0), color="#ffaa00"),
        NoiseFactor(label="Train", value=scores.get("train", 0), color="#0099ff"),
        NoiseFactor(label="Bus", value=scores.get("bus", 0), color="#00cc88"),
    ]

    return NoiseScoreResponse(
        location=location,
        lat=lat,
        lng=lng,
        score=score,
        reason=reason,
        factors=factors
    )


@router.get("/score_analysis")
def get_score_analysis(lat: float = Query(...), lng: float = Query(...)):
    scores = compute_places_factors(lat, lng)
    return {
        "nightlife": float(scores.get("nightlife", 0)),
        "airport": float(scores.get("airport", 0)),
        "train": float(scores.get("train", 0)),
        "bus": float(scores.get("bus", 0)),
        "combined_score": float(scores.get("combined_score", 1.0))
    }

@router.get("/location_insight")
def location_insight(lat: float = Query(...), lng: float = Query(...)):
    result = get_location_summary(lat, lng)

    return JSONResponse(content={
        "summary": result.get("summary", "No summary available."),
        "factors": result.get("factors", [])
    })