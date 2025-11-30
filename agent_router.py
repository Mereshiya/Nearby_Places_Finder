from google.adk.agents import Agent
from agent_places import places_tool
from agent_weather import weather_tool
from agent_route import route_tool
from google.adk.tools import FunctionTool

def combined_places_review_and_route(user_lat, user_lon, query):
    """
    Fetch places, top 3 by rating, and OTP-based transport suggestions.
    Wrap outputs in structured markers for sidebar.
    """
    # Weather
    weather_info = weather_tool.func(user_lat, user_lon)
    if isinstance(weather_info, dict):
        # Convert to readable string
        weather_text = f"Temperature: {weather_info.get('temperature', 'N/A')}°C\n"
        weather_text += f"Condition: {weather_info.get('condition', 'N/A')}\n"
        weather_text += f"Wind speed: {weather_info.get('wind', 'N/A')} km/h"
    else:
        weather_text = str(weather_info)

    weather_section = f"[WEATHER]\n{weather_text}\n"

    # Place Finder 
    all_places_raw = places_tool.func(user_lat, user_lon, query)
    if not all_places_raw:
        places_section = "[PLACES]\nNo places found.\n"
        top3_section = "[REVIEWS]\nNo reviews info.\n"
        transport_section = "[TRANSPORT]\nNo transport info.\n"
        return weather_section + places_section + top3_section + transport_section

    all_places = []
    for p in all_places_raw:
        lat_val = float(p.get("lat", 0))
        lon_val = float(p.get("lon", 0) or p.get("lng", 0))
        if lat_val == 0 or lon_val == 0:
            continue
        map_link = f"https://www.openstreetmap.org/?mlat={lat_val}&mlon={lon_val}&zoom=15"
        all_places.append({
            "name": p.get("name", "Unknown"),
            "lat": lat_val,
            "lon": lon_val,
            "rating": float(p.get("rating", 0)) if p.get("rating") else 0,
            "link": map_link
        })

    # Places section
    places_section = "[PLACES]\n" + "\n".join(
        [f"• {p['name']} ([map]({p['link']}))" for p in all_places]
    )

    # Top 3 by rating as reviews
    top3 = sorted(all_places, key=lambda x: x["rating"], reverse=True)[:3]
    top3_section = "[REVIEWS]\n" + "\n".join(
        [f"⭐ {p['rating']} — {p['name']} ([map]({p['link']}))" for p in top3]
    )

    # Transport suggestions
    transport_text = route_tool.func(user_lat, user_lon, top3)
    if isinstance(transport_text, dict):
        transport_text = str(transport_text)
    transport_section = f"[TRANSPORT]\n{transport_text.strip()}"

    return weather_section + places_section + top3_section + transport_section


combined_tool = FunctionTool(combined_places_review_and_route)

# Root multi-agent router
root_agent = Agent(
    name="router_agent",
    model="gemini-2.5-flash",
    description="Routes queries to weather, places, reviews, and transport agents.",
    instruction="""
You are a coordinator AI.
- For weather → call weather_tool.
- For nearby places → call combined_tool (all places + top 3 + OTP routes).
- Always return your output in this structured format:
  [WEATHER] ... [PLACES] ... [REVIEWS] ... [TRANSPORT] ...
""",
    tools=[weather_tool, combined_tool]
)
