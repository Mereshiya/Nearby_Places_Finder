import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from agent_router import root_agent  # Multi-agent router

async def main():
    print("📍 Nearby Finder CLI (Multi-Agent)")
    lat = input("Enter latitude: ")
    lng = input("Enter longitude: ")
    query = input("Enter your query (places/weather/both): ")

    # Initialize session and runner
    session = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name="cli_multi_agent", session_service=session)
    await session.create_session(user_id="user", session_id="cli", app_name=runner.app_name)

    enriched_prompt = f"My location is {lat}, {lng}. {query}"
    msg = Content(role="user", parts=[Part(text=enriched_prompt)])

    print("\nSearching...\n")
    async for event in runner.run_async(user_id="user", session_id="cli", new_message=msg):
        if event.content and event.content.parts:
            print(event.content.parts[0].text, end="")

if __name__ == "__main__":
    asyncio.run(main())
