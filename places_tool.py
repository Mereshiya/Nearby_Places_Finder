import requests

def search_nearby(lat: float, lng: float, query: str):
    """
    Search for places near a given latitude & longitude.
    Returns cleaned, structured objects:
    [
        {
            "name": str,
            "lat": float,
            "lon": float,
            "rating": float,
            "link": str,
            "address": str
        }
    ]
    """

    radius_deg = 0.05
    viewbox = f"{lng - radius_deg},{lat - radius_deg},{lng + radius_deg},{lat + radius_deg}"

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 15,
        "viewbox": viewbox,
        "bounded": 1,
        "extratags": 1,
        "addressdetails": 1
    }

    try:
        res = requests.get(
            url, params=params,
            headers={"User-Agent": "multi-agent-app"},
            timeout=10
        ).json()
    except Exception:
        return []

    places = []

    for p in res:
        # Coordinate extraction
        try:
            lat_val = float(p.get("lat", 0))
            lon_val = float(p.get("lon", 0))
        except:
            continue

        if lat_val == 0 or lon_val == 0:
            continue

        name = p.get("name") or "Unnamed Place"

        address = ""
        if p.get("address"):
            address = ", ".join(list(p["address"].values()))

        extratags = p.get("extratags", {})
        rating_raw = extratags.get("rating")
        try:
            rating = float(rating_raw) if rating_raw else 3.5
        except:
            rating = 3.5

        places.append({
            "name": name,
            "lat": lat_val,
            "lon": lon_val,
            "rating": rating,
            "address": address,
            "link": f"https://www.openstreetmap.org/?mlat={lat_val}&mlon={lon_val}&zoom=16"
        })

    return places

def get_weather(lat: float, lng: float):
    """
    Fetch current weather & alerts for a given lat/lng.
    Returns text: temperature, wind speed, and weather alerts.
    """

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "current_weather": "true",
        "weather_alerts": "true"
    }

    try:
        res = requests.get(url, params=params, timeout=10).json()

        cw = res.get("current_weather", {})
        temp = cw.get("temperature", "?")
        wind = cw.get("windspeed", "?")

        alert_box = res.get("weather_alerts", {})
        alerts = alert_box.get("alert", []) if isinstance(alert_box, dict) else []

        alert_titles = [a.get("event") for a in alerts if a.get("event")]

        if alert_titles:
            alert_msg = "⚠️ Alerts: " + ", ".join(alert_titles)
            weather_msg = f"🌡️ Temp: {temp}°C, 🌬️ Wind: {wind} km/h"
            return f"{alert_msg}\n{weather_msg}"

        return f"🌡️ Temp: {temp}°C, 🌬️ Wind: {wind} km/h"

    except Exception:
        return "Unable to fetch weather."

