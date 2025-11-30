import requests
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

load_dotenv("./.env")

def get_weather(lat: float, lng: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lng, "current_weather": True, "alerts": True}
    try:
        res = requests.get(url, params=params).json()
        cw = res.get("current_weather", {})
        temp = cw.get("temperature")
        wind = cw.get("windspeed")

        alert = None
        if "alerts" in res and res["alerts"]:
            events = [a.get("event") for a in res["alerts"] if a.get("event")]
            if events:
                alert = "⚠️ " + ", ".join(events)

        return {"temperature": temp, "wind": wind, "alert": alert}
    except:
        return {"temperature": None, "wind": None, "alert": None}

weather_tool = FunctionTool(get_weather)

weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="Provides current weather and alerts for a location.",
    instruction="Answer only using weather_tool when user asks about weather or alerts.",
    tools=[weather_tool]
)
