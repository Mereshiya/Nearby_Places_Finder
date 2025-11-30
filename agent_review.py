from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import random

def get_top_reviews(places):
    if not places:
        return "No places found."

    sorted_places = sorted(places, key=lambda x: x["rating"], reverse=True)
    top3 = sorted_places[:3]

    return "\n".join([f"⭐ {p['rating']} — [{p['name']}]({p['link']})" for p in top3])

review_tool = FunctionTool(get_top_reviews)

review_agent = Agent(
    name="review_agent",
    model="gemini-2.5-flash",
    description="Shows top 3 places by rating with links from a list of places.",
    instruction="Only use review_tool to determine top 3 places.",
    tools=[review_tool]
)
