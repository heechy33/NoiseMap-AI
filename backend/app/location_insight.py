import google.generativeai as genai
import json

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=key)

def get_location_summary(lat, lng):
    prompt = f"""
You are an urban noise and zoning expert.

Return only valid JSON in this format:

{{
  "summary": "2-3 sentence description of the area (zoning + environment)",
  "factors": [
    "🚗 Traffic: Very dense traffic from taxis, delivery vans, etc.",
    "🚇 Transit: Subway rumbles, station announcements",
    "🎤 Nightlife: Music and chatter from bars",
    "👥 Pedestrians: Loud crowd presence and tourists"
  ]
}}

No markdown, no prose — just valid JSON. Do not explain anything.
Coordinates: ({lat}, {lng})
"""

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)

        text = response.text.strip()

        return json.loads(text)

    except Exception as e:
        print("Parsing error:", e)
        return {
            "summary": "Failed to generate insight.",
            "factors": []
        }