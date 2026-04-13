from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from app.ml_model import predict_noise_score
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
    location: str = Query("Unknown"),
):
    result = predict_noise_score(lat, lng)
    return NoiseScoreResponse(
        location=location,
        lat=lat,
        lng=lng,
        score=result["score"],
        reason=result["reason"],
        factors=[NoiseFactor(**f) for f in result["factors"]],
    )


@router.get("/score_analysis")
def get_score_analysis(lat: float = Query(...), lng: float = Query(...)):
    result = predict_noise_score(lat, lng)
    raw = result["raw"]
    return {
        "airport": round(raw["airport"] * 10, 1),
        "nightlife": round(raw["nightlife"], 1),
        "bus": round(raw["bus"] * 10, 1),
        "train": round(raw["train"] * 10, 1),
        "density": round(min(raw["density"] / 10000.0 * 10, 10.0), 1),
        "combined_score": result["score"],
    }


@router.get("/location_insight")
def location_insight(lat: float = Query(...), lng: float = Query(...)):
    result = get_location_summary(lat, lng)
    return JSONResponse(content={
        "summary": result.get("summary", "No summary available."),
        "factors": result.get("factors", []),
    })
