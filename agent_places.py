import os
import requests
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Load .env
load_dotenv("./.env")

def search_places(lat: float, lng: float, query: str):
    radius_deg = 0.05
    viewbox = [lng - radius_deg, lat - radius_deg, lng + radius_deg, lat + radius_deg]

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 10,
        "viewbox": ",".join(map(str, viewbox)),
        "bounded": 1,
        "addressdetails": 1
    }

    res = requests.get(url, params=params, headers={"User-Agent": "multi-agent-app"}).json()
    if not res:
        return []

    # Return structured data
    output = []
    for p in res:
        name = p.get("display_name", "Unknown")
        lat_p = p.get("lat")
        lon_p = p.get("lon")
        link = f"https://www.openstreetmap.org/?mlat={lat_p}&mlon={lon_p}&zoom=15"
        output.append({
            "name": name,
            "lat": lat_p,
            "lng": lon_p,
            "link": link,
            "rating": round(4 + (0.5 * len(name) % 1), 1)  
        })

    return output

places_tool = FunctionTool(search_places)

places_agent = Agent(
    name="places_agent",
    model="gemini-2.5-flash",
    description="Finds nearby places based on user location.",
    instruction="Answer only using places_tool for nearby places queries.",
    tools=[places_tool]
)
