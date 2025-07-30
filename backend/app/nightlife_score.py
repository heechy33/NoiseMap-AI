import requests
import time
from math import radians, cos, sin, sqrt, atan2, exp
import pandas as pd
from scipy.spatial import KDTree
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
NIGHTLIFE_TYPES = ["bar", "night_club", "pub", "casino"]


file_path = os.path.join(os.path.dirname(__file__), "worldcities.csv")
cities_df = pd.read_csv(file_path)
cities_df = cities_df.dropna(subset=["lat", "lng", "population"])
city_tree = KDTree(cities_df[["lat", "lng"]].values)

#Function that calculates the distance between two coordinates
def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371 #Earth Radius
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

#Population density function: used to calculate accurate nightlife score
def estimate_city_density(lat, lng):
    _, idx = city_tree.query([lat, lng])
    city_row = cities_df.iloc[idx]
    population = city_row["population"]
    estimated_area_km2 = max((population ** 0.75) / 12, 10)
    return population / estimated_area_km2

#Helper function for nightlife score: it gives more weight to places that are coser or have more user ratings.
def process_results(results, lat, lng):
    weight_sum = 0.0
    for place in results:
        loc = place.get("geometry", {}).get("location", {})
        lat2, lng2 = loc.get("lat"), loc.get("lng")
        if lat2 is None or lng2 is None:
            continue

        dist_km = haversine_distance_km(lat, lng, lat2, lng2)
        if dist_km > 1.5:
            continue

        user_ratings = place.get("user_ratings_total", 0)
        base_weight = exp(-1.8 * dist_km)
        popularity_boost = min(user_ratings / 30.0, 4.0)
        weight_sum += base_weight * (1.5 + popularity_boost)

    return weight_sum

#Nightlife Score
def nightlife_score_google_places(lat, lng, radius=600):
    total_weight = 0.0
    count_valid = 0

    for place_type in NIGHTLIFE_TYPES:
        url = (
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius={radius}&type={place_type}&key={GOOGLE_MAPS_API_KEY}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {place_type}: {response.text}")
            continue

        data = response.json()
        results = data.get("results", [])
        total_weight += process_results(results, lat, lng)
        count_valid += len(results)

        if "next_page_token" in data:
            time.sleep(2)
            next_url = (
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                f"?pagetoken={data['next_page_token']}&key={GOOGLE_MAPS_API_KEY}"
            )
            response = requests.get(next_url)
            data = response.json()
            results = data.get("results", [])
            total_weight += process_results(results, lat, lng)
            count_valid += len(results)

    if count_valid == 0:
        return 1.0

    city_density = estimate_city_density(lat, lng)
    density_scale = min(city_density / 10000.0, 1.0)
    adjusted_score = min(total_weight * density_scale, 10.0)
    return round(1.0 + 9.0 * (adjusted_score / 10.0), 1)

#Airport Function: fetches nearby airports.
def airport_score_google_places(lat, lng):
    url = (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius=20000&type=airport&key={GOOGLE_MAPS_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code != 200:
        print(f" ailed to fetch airport: {response.text}")
        return 1.0

    results = response.json().get("results", [])
    if not results:
        return 1.0

    loc = results[0]["geometry"]["location"]
    dist_km = haversine_distance_km(lat, lng, loc["lat"], loc["lng"])
    score = max(0.0, 10.0 - (dist_km / 2.0))
    return round(score, 1)

#Transit Funtion: fetches data for either Train or Bus
def transit_score_google_places(lat, lng, types, radius):
    max_score = 0.0
    for place_type in types:
        url = (
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius={radius}&type={place_type}&key={GOOGLE_MAPS_API_KEY}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {place_type}: {response.text}")
            continue

        results = response.json().get("results", [])
        for place in results:
            loc = place["geometry"]["location"]
            dist_km = haversine_distance_km(lat, lng, loc["lat"], loc["lng"])
            score = max(0.0, 10.0 - dist_km * 2)
            max_score = max(max_score, score)

    return round(max_score, 1)

def train_score_google_places(lat, lng):
    return transit_score_google_places(lat, lng, ["train_station", "subway_station"], radius=3000)

def bus_score_google_places(lat, lng):
    return transit_score_google_places(lat, lng, ["bus_station"], radius=1000)

#Compute combined noise score
def compute_places_factors(lat, lng):
    nightlife = nightlife_score_google_places(lat, lng)
    airport = airport_score_google_places(lat, lng)
    train = train_score_google_places(lat, lng)
    bus = bus_score_google_places(lat, lng)

    # How each scores are weighted
    weights = {
        "nightlife": 0.35,
        "airport": 0.25,
        "train": 0.25,
        "bus": 0.15
    }

    # Combined Noise Score with 4 factors
    combined = (
        nightlife * weights["nightlife"] +
        airport * weights["airport"] +
        train * weights["train"] +
        bus * weights["bus"]
    )

    return {
        "nightlife": nightlife,
        "airport": airport,
        "train": train,
        "bus": bus,
        "combined_score": round(combined, 1)
    }

