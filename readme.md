
# Nearby Places Finder - Multi-Agent Dashboard

A smart multi-agent system that discovers nearby places, ranks them by reviews, suggests transportation modes, and provides real-time weather insights.


---

## Overview

This project is a **Concierge-style Multi-Agent Application** built using **Google’s ADK (Agent Developer Kit)** and **Streamlit**.  

It helps users quickly find ATMs, cafes, restaurants, or any place nearby, while also giving:

- Top-rated places based on reviews  
- Recommended mode of transport for each place  
- Real-time weather information  
- Interactive map links for every location  

All of this is coordinated through a **Router Agent** that intelligently orchestrates tasks between Weather, Places, Review, and Transport agents.

---

## Tech Stack

- **Frontend**: Streamlit  
- **Backend / Agents**: Google ADK (Python)  
- **APIs**: OpenStreetMap, Google Maps, or similar for places and routes  
- **Environment Variables**: `.env` file with API keys  

---
## Pipeline Architecture

Link : [Architecture_Overflow](https://drive.google.com/file/d/1gIq-VtYGx7nMBOH9VENjTAmaFmp6cs6J/view?usp=drive_link)


---
## Installation

1. Clone the repo:

```bash
git clone https://github.com/yourusername/nearby-places-finder.git
cd nearby-places-finder
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your API keys to .env:
```bash
GEMINI_API_KEY=<YOUR_KEY_HERE>
```

4. Run the app
```bash
streamlit run app_ui.py

```
---
## Usage

- Open the Streamlit app

- Enter your latitude and longitude or click Use My Location

- Enter your query, e.g., "cafes near me" or "nearest ATM"

- View results with:

    - Interactive map links

    - Top 3 rated places

    - Suggested transport modes

    - Local weather info
---
