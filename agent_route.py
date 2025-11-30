from google.adk.tools import FunctionTool
import requests

# Fallback Haversine distance
from math import radians, cos, sin, asin, sqrt
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    km = 6371*c
    return km

# OTP route fetcher
def otp_route(user_lat, user_lon, place_lat, place_lon):
    otp_url = "http://localhost:8080/otp/routers/default/plan"
    params = {
        "fromPlace": f"{user_lat},{user_lon}",
        "toPlace": f"{place_lat},{place_lon}",
        "mode": "TRANSIT,WALK",
        "numItineraries": 1
    }
    try:
        res = requests.get(otp_url, params=params, timeout=5).json()
        legs = res["plan"]["itineraries"][0]["legs"]
        steps = []
        for leg in legs:
            mode = leg["mode"]
            dist_km = leg["distance"]/1000
            if mode == "BUS":
                steps.append(f"🚌 {leg['route']} {dist_km:.1f} km")
            elif mode == "RAIL":
                steps.append(f"🚇 {leg['route']} {dist_km:.1f} km")
            elif mode == "WALK":
                steps.append(f"🚶 {dist_km:.1f} km")
        return " → ".join(steps)
    except Exception:
        # OTP failed → fallback
        dist_km = haversine(user_lat, user_lon, place_lat, place_lon)
        if dist_km <= 0.5:
            return f"\n**🚶 {dist_km:.1f} km — Walking.**"
        elif dist_km <= 2:
            return f"\n**🛵 {dist_km:.1f} km — Auto/taxi recommended.**"
        else:
            return f"\n**🚇 {dist_km:.1f} km — Metro recommended.**"

# Route suggestion for top 3
def route_suggestions(user_lat, user_lon, top_places):
    if not top_places:
        return "No top places found for routing."
    suggestions = []
    for place in top_places:
        name = place["name"]
        lat = float(place["lat"])
        lon = float(place["lon"])
        route_text = otp_route(user_lat, user_lon, lat, lon)
        suggestions.append(f"{name} → {route_text}")
    return "\n".join(suggestions)

route_tool = FunctionTool(route_suggestions)
