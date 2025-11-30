import streamlit as st
import pandas as pd
import asyncio
import json
import re
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from agent_router import root_agent
from itertools import zip_longest

st.set_page_config(
    page_title="Nearby Places Finder (Multi-Agent UI)",
    layout="wide",
    page_icon="📍"
)
st.title("📍 Nearby Places Finder (Multi-Agent Dashboard)")
st.write("Use the sidebar to see outputs from individual agents. Ask your query below.")

# Initialize session_state
if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lng = None

if "runner" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()
    st.session_state.runner = Runner(
        agent=root_agent,
        app_name="map_app",
        session_service=st.session_state.session_service
    )
    asyncio.run(st.session_state.session_service.create_session(
        user_id="user",
        session_id="map_chat",
        app_name="map_app"
    ))
    st.session_state.messages = []

# Structured boxes per agent
sidebar = st.sidebar
sidebar.header("Agent Dialog Boxes")

weather_container = sidebar.container()
weather_container.subheader("🌤 Weather Agent")
weather_alert = weather_container.empty()
weather_temp = weather_container.empty()
weather_wind = weather_container.empty()

places_container = sidebar.container()
places_container.subheader("📍 Places Finder Agent")
places_list = places_container.empty()

reviews_container = sidebar.container()
reviews_container.subheader("⭐ Review Agent")
reviews_list = reviews_container.empty()

transport_container = sidebar.container()
transport_container.subheader("🚗 Transportation Agent")
transport_list = transport_container.empty()

# Automatic geolocation
if st.session_state.user_lat is None:
    get_location_js = """
    <script>
    function sendLocation() {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = pos.coords.latitude + "," + pos.coords.longitude;
                const url = new URL(window.location);
                url.searchParams.set("coords", coords);
                window.history.replaceState({}, "", url);
                window.location.reload();
            },
            (err) => { alert("Location error: " + err.message); }
        );
    }
    </script>
    <button onclick="sendLocation()" style="
        padding:10px 20px;
        background:#4CAF50;
        color:white;
        border:none;
        border-radius:5px;">
    📡 Use My Location
    </button>
    """
    st.components.v1.html(get_location_js, height=100)

# Manual input fallback
if st.session_state.user_lat is None:
    st.info("Enter location manually:")
    col1, col2 = st.columns(2)
    with col1:
        lat_input = st.text_input("Latitude")
    with col2:
        lng_input = st.text_input("Longitude")
    if lat_input and lng_input:
        try:
            st.session_state.user_lat = float(lat_input)
            st.session_state.user_lng = float(lng_input)
            st.success(f"Manual location set: {lat_input}, {lng_input}")
        except:
            st.error("Invalid coordinates!")

def add_empty_line_after_bullets(text):
    """Add <br> after each line/bullet for Streamlit Markdown with HTML."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "<br>".join(lines)


# Read coords from query param
coords = st.query_params.get("coords")
if coords and st.session_state.user_lat is None:
    try:
        lat, lng = map(float, coords[0].split(","))
        st.session_state.user_lat = lat
        st.session_state.user_lng = lng
        st.success(f"Location set: {lat}, {lng}")
    except:
        st.error("Invalid coordinates received.")

# Show map
if st.session_state.user_lat and st.session_state.user_lng:
    st.map(pd.DataFrame([{"lat": st.session_state.user_lat, "lon": st.session_state.user_lng}]))

# Display chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Chat input
if prompt := st.chat_input("Ask about places, weather, reviews, transport..."):
    if st.session_state.user_lat is None:
        st.error("Please set your location first!")
        st.stop()

    enriched_prompt = f"My location is {st.session_state.user_lat},{st.session_state.user_lng}. {prompt}"

    # record user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        async def run_agents():
            full_text = ""
            msg = Content(role="user", parts=[Part(text=enriched_prompt)])

            # stream agent responses into full_text
            async for event in st.session_state.runner.run_async(
                user_id="user",
                session_id="map_chat",
                new_message=msg
            ):
                if event.content and event.content.parts:
                    text = event.content.parts[0].text
                    if text:
                        full_text += text
                        placeholder.markdown(full_text + "▌")

            # Parse agent outputs into sections
            weather_display = {"alert": "None", "temperature": "N/A", "wind": "N/A"}
            places_display = "No places info"
            reviews_display = "No reviews info"
            transport_display = "No transport info"

            try:
                # Weather Agent
                w = re.search(r"\[WEATHER\](.*?)\[PLACES\]", full_text, re.DOTALL)
                weather_data_raw = w.group(1).strip() if w else ""
                if weather_data_raw:
                    try:
                        parsed = json.loads(weather_data_raw.replace("'", '"'))
                    except:
                        parsed = None
                    if isinstance(parsed, dict):
                        weather_display["alert"] = parsed.get("alert", "None")
                        weather_display["temperature"] = parsed.get("temperature", "N/A")
                        weather_display["wind"] = parsed.get("wind", "N/A")
                    else:
                        tmatch = re.search(r"([Tt]emperature[: ]+)(-?\d+\.?\d*)", weather_data_raw)
                        wmatch = re.search(r"([Ww]ind(?: speed)?[: ]+)(-?\d+\.?\d*)", weather_data_raw)
                        if tmatch:
                            weather_display["temperature"] = tmatch.group(2)
                        if wmatch:
                            weather_display["wind"] = wmatch.group(2)
                        alert_match = re.search(r"(⚠️|alert[: ]+([^.\n]+))", weather_data_raw, re.IGNORECASE)
                        if alert_match:
                            weather_display["alert"] = alert_match.group(2) if alert_match.lastindex and alert_match.group(2) else "⚠️"
                        else:
                            if weather_data_raw:
                                weather_display["alert"] = weather_data_raw

                # Place Finder Agent
                p = re.search(r"\[PLACES\](.*?)\[REVIEWS\]", full_text, re.DOTALL)
                if p:
                    ptxt = p.group(1).strip()
                    if ptxt and ptxt.lower() not in ("none", "no places found.", "no places info"):
                        places_display = ptxt

                # Review Agent
                r = re.search(r"\[REVIEWS\](.*?)\[TRANSPORT\]", full_text, re.DOTALL)
                if r:
                    rtxt = r.group(1).strip()
                    if rtxt and rtxt.lower() not in ("none", ""):
                        reviews_display = rtxt

                # Transport Agent
                t = re.search(r"\[TRANSPORT\](.*)", full_text, re.DOTALL)
                if t:
                    ttxt = t.group(1).strip()
                    if ttxt and ttxt.lower() not in ("none", ""):
                        transport_display = ttxt
            except Exception as e:
                print("Parsing error:", e)

            # Populate sidebar with spacing
            def add_empty_line_after_bullets(text):
                """Add one empty line after each bullet/line."""
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                return "\n\n".join(lines)

            weather_alert.markdown(f"**Alert:** {weather_display.get('alert', 'None')}")
            temp_val = weather_display.get('temperature', "N/A")
            try:
                temp_val_display = f"{float(temp_val):.1f}°C"
            except:
                temp_val_display = str(temp_val)
            weather_temp.markdown(f"**Temperature:** {temp_val_display}")
            wind_val = weather_display.get('wind', "N/A")
            try:
                wind_val_display = f"{float(wind_val):.1f} km/h"
            except:
                wind_val_display = str(wind_val)
            weather_wind.markdown(f"**Wind:** {wind_val_display}")

            places_list.markdown(add_empty_line_after_bullets(places_display), unsafe_allow_html=True)
            reviews_list.markdown(add_empty_line_after_bullets(reviews_display), unsafe_allow_html=True)
            transport_list.markdown(add_empty_line_after_bullets(transport_display), unsafe_allow_html=True)

            user_query_lower = prompt.lower()

            user_query_lower = prompt.lower()
            if "weather" in user_query_lower or "temperature" in user_query_lower or "wind" in user_query_lower:
                # Extract individual values
                temp_val = weather_display.get('temperature', 'N/A')
                wind_val = weather_display.get('wind', 'N/A')

                # Format numbers
                try:
                    temp_val = f"{float(temp_val):.1f}"
                except:
                    temp_val = str(temp_val)

                try:
                    wind_val = f"{float(wind_val):.1f}"
                except:
                    wind_val = str(wind_val)

                main_chat_output = f"The current temperature is {temp_val} degrees Celsius with a wind speed of {wind_val} km/h."

            else:
                # Split reviews by ⭐ (each block starts with a star)
                review_blocks = re.split(r"(?=\⭐)", reviews_display)
                review_blocks = [b.strip() for b in review_blocks if b.strip()]

                # Split transport by line first, not by arrow
                transport_entries = [line.strip() for line in transport_display.split("\n") if line.strip()]
                transport_map = {}
                for entry in transport_entries:
                    if "→" in entry:
                        place, info = entry.split("→", 1)
                        transport_map[place.strip()] = info.strip()

                main_chat_output = "**⭐ Top Reviews & 🚗 Transport Suggestions**\n\n"

                for review in review_blocks:
                    main_chat_output += f"{review}\n\n"
                    match = re.search(r"⭐.*?—\s*(.*?)(,|$)", review)
                    place_name = match.group(1).strip() if match else None

            placeholder.markdown(main_chat_output.replace("\n", "<br>"), unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": main_chat_output})

            return full_text

        asyncio.run(run_agents())
