import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_location_summary(lat: float, lng: float) -> dict:
    prompt = f"""
You are an urban noise and zoning expert.

Return only valid JSON in this format:

{{
  "summary": "2-3 sentence description of the area (zoning + noise environment)",
  "factors": [
    "Traffic: Very dense traffic from taxis and delivery vehicles",
    "Transit: Subway rumbles and station announcements",
    "Nightlife: Music and chatter from nearby bars",
    "Pedestrians: Loud crowd presence and foot traffic"
  ]
}}

No markdown, no prose — just valid JSON.
Coordinates: ({lat}, {lng})
"""

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        return json.loads(response.text.strip())
    except Exception as e:
        print("Gemini parsing error:", e)
        return {
            "summary": "Failed to generate insight.",
            "factors": [],
        }
