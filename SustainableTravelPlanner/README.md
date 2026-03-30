# Sustainable Travel Planner

A full-stack Flask web application to help users choose eco-friendly travel plans.

## Features

- Input: source, destination, date, required arrival time
- Mode selection:
  - `Transport Only`
  - `Full Trip Plan`
- Transport dashboard:
  - Train / Flight / Bus comparison (cost, travel time, CO2)
  - Clickable mode filters for detailed options
  - Arrival-time filtering
  - Eco recommendation and CO2 savings message
- Full trip extension:
  - Eco-friendly hotels
  - Sustainable places (parks, gardens, nature spots)
  - Local low-emission transport suggestions

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Database: SQLite
- Maps API: OSRM public routing API with local fallback

## Run Locally

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start app:

```bash
python app.py
```

4. Open:

`http://127.0.0.1:5000`

## Notes

- SQLite database auto-initializes on first run at `data/travel_planner.db`.
- Seed data includes common city routes; unknown routes use generated fallback options.
