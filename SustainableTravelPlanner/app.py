from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen
import json
import math

from flask import Flask, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "travel_planner.db"

app = Flask(__name__)


CITY_COORDS = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bengaluru": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "goa": (15.2993, 74.1240),
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def route_distance_from_maps_api(source: str, destination: str) -> float:
    """Try OSRM as a maps API fallback, then estimate locally."""
    s = source.strip().lower()
    d = destination.strip().lower()
    if s in CITY_COORDS and d in CITY_COORDS:
        slat, slon = CITY_COORDS[s]
        dlat, dlon = CITY_COORDS[d]
        try:
            # Free public routing API for demo purposes.
            url = (
                "https://router.project-osrm.org/route/v1/driving/"
                f"{slon},{slat};{dlon},{dlat}?overview=false"
            )
            with urlopen(url, timeout=4) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("code") == "Ok" and payload.get("routes"):
                return payload["routes"][0]["distance"] / 1000.0
        except (URLError, TimeoutError, json.JSONDecodeError):
            pass
        # 1.15 multiplier as practical route vs crow distance
        return haversine_distance_km(slat, slon, dlat, dlon) * 1.15

    seed = int(hashlib.sha256(f"{s}-{d}".encode("utf-8")).hexdigest(), 16)
    return 120 + (seed % 1400)


def parse_time(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS transport_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                mode TEXT NOT NULL,
                service_name TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                duration_min INTEGER NOT NULL,
                cost REAL NOT NULL,
                carbon_per_km REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS eco_hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                name TEXT NOT NULL,
                nightly_cost REAL NOT NULL,
                eco_score INTEGER NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS eco_places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                place_name TEXT NOT NULL,
                category TEXT NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS local_transport (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                mode TEXT NOT NULL,
                notes TEXT NOT NULL,
                carbon_level TEXT NOT NULL
            );
            """
        )

        existing_count = conn.execute(
            "SELECT COUNT(*) AS c FROM transport_options"
        ).fetchone()["c"]
        if existing_count > 0:
            return

        transport_seed = [
            ("delhi", "mumbai", "train", "Rajdhani Green Line", "06:15", 920, 2300, 0.028),
            ("delhi", "mumbai", "train", "Vande Bharat Connect", "13:45", 840, 2800, 0.025),
            ("delhi", "mumbai", "flight", "EcoAir 214", "08:40", 130, 5600, 0.160),
            ("delhi", "mumbai", "flight", "SkyConnect 602", "16:00", 135, 6200, 0.170),
            ("delhi", "mumbai", "bus", "Intercity Electric Coach", "07:30", 1220, 1700, 0.045),
            ("delhi", "mumbai", "bus", "Night Green Sleeper", "21:00", 1280, 1400, 0.052),
            ("bengaluru", "chennai", "train", "Shatabdi Eco", "07:00", 360, 900, 0.024),
            ("bengaluru", "chennai", "flight", "BlueJet 88", "10:10", 60, 2800, 0.155),
            ("bengaluru", "chennai", "bus", "EV Express", "06:30", 430, 700, 0.040),
            ("hyderabad", "goa", "train", "Konkan Saver", "05:50", 760, 1800, 0.027),
            ("hyderabad", "goa", "flight", "AirCoast 71", "11:35", 85, 4300, 0.165),
            ("hyderabad", "goa", "bus", "GreenLine Volvo", "18:00", 810, 1300, 0.049),
        ]
        conn.executemany(
            """
            INSERT INTO transport_options
            (source, destination, mode, service_name, departure_time, duration_min, cost, carbon_per_km)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            transport_seed,
        )

        hotel_seed = [
            ("mumbai", "Harbor Eco Stay", 4200, 92, "Solar power, rainwater harvesting"),
            ("mumbai", "Urban Leaf Residency", 3600, 86, "Plastic-free amenities"),
            ("chennai", "Marina Green Hotel", 3100, 88, "Local organic breakfast"),
            ("goa", "Coastal Bamboo Retreat", 5000, 95, "Low-impact architecture"),
            ("goa", "SeaWind Eco Lodge", 3900, 82, "Greywater recycling"),
        ]
        conn.executemany(
            """
            INSERT INTO eco_hotels (city, name, nightly_cost, eco_score, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            hotel_seed,
        )

        place_seed = [
            ("mumbai", "Sanjay Gandhi National Park", "park", "Nature trails and biodiversity"),
            ("mumbai", "Hanging Gardens", "botanical garden", "Urban green space"),
            ("chennai", "Guindy National Park", "park", "Compact city forest"),
            ("goa", "Salim Ali Bird Sanctuary", "nature spot", "Mangrove ecosystem"),
            ("goa", "Mhadei Wildlife Sanctuary", "nature spot", "Western Ghats biodiversity"),
        ]
        conn.executemany(
            """
            INSERT INTO eco_places (city, place_name, category, notes)
            VALUES (?, ?, ?, ?)
            """,
            place_seed,
        )

        local_transport_seed = [
            ("mumbai", "Walking", "Best for short city hops", "very low"),
            ("mumbai", "Cycling", "Use bike-share near sea face", "very low"),
            ("mumbai", "Metro + Local Train", "High-capacity public transport", "low"),
            ("chennai", "Cycling", "Beach road bike corridors", "very low"),
            ("chennai", "Metro + Bus", "Integrated smart card routes", "low"),
            ("goa", "Walking", "Ideal for local markets", "very low"),
            ("goa", "E-bike Rental", "Low-emission beach travel", "low"),
            ("goa", "Public Bus", "Affordable inter-town travel", "low"),
        ]
        conn.executemany(
            """
            INSERT INTO local_transport (city, mode, notes, carbon_level)
            VALUES (?, ?, ?, ?)
            """,
            local_transport_seed,
        )


initialize_database()


def compute_transport_plan(
    source: str, destination: str, travel_date: str, required_arrival: str
) -> dict[str, Any]:
    distance_km = route_distance_from_maps_api(source, destination)
    required_arrival_dt = parse_time(travel_date, required_arrival)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM transport_options
            WHERE lower(source) = lower(?) AND lower(destination) = lower(?)
            ORDER BY mode, departure_time
            """,
            (source, destination),
        ).fetchall()

    if not rows:
        rows = [
            {
                "mode": "train",
                "service_name": "Regional Eco Rail",
                "departure_time": "07:00",
                "duration_min": int(distance_km * 1.35),
                "cost": 0.95 * distance_km,
                "carbon_per_km": 0.026,
            },
            {
                "mode": "bus",
                "service_name": "Intercity Green Bus",
                "departure_time": "06:30",
                "duration_min": int(distance_km * 1.7),
                "cost": 0.60 * distance_km,
                "carbon_per_km": 0.048,
            },
            {
                "mode": "flight",
                "service_name": "Direct Air Route",
                "departure_time": "09:20",
                "duration_min": int(distance_km * 0.25) + 60,
                "cost": 2.20 * distance_km,
                "carbon_per_km": 0.165,
            },
        ]

    options: list[dict[str, Any]] = []
    for row in rows:
        departure = parse_time(travel_date, row["departure_time"])
        arrival = departure + timedelta(minutes=int(row["duration_min"]))
        carbon_kg = round(float(row["carbon_per_km"]) * distance_km, 2)
        option = {
            "mode": row["mode"],
            "service_name": row["service_name"],
            "departure_time": departure.strftime("%H:%M"),
            "arrival_time": arrival.strftime("%H:%M"),
            "duration_min": int(row["duration_min"]),
            "cost": round(float(row["cost"]), 2),
            "carbon_kg": carbon_kg,
            "is_valid": arrival <= required_arrival_dt,
        }
        options.append(option)

    valid_options = [o for o in options if o["is_valid"]]
    compare_pool = valid_options if valid_options else options
    best_option = min(compare_pool, key=lambda x: x["carbon_kg"]) if compare_pool else None
    worst_option = max(compare_pool, key=lambda x: x["carbon_kg"]) if compare_pool else None
    co2_saved = (
        round(worst_option["carbon_kg"] - best_option["carbon_kg"], 2)
        if best_option and worst_option
        else 0
    )

    by_mode: dict[str, list[dict[str, Any]]] = {"train": [], "flight": [], "bus": []}
    for option in options:
        by_mode.setdefault(option["mode"], []).append(option)

    mode_summary = []
    for mode in ["train", "flight", "bus"]:
        mode_options = by_mode.get(mode, [])
        if not mode_options:
            continue
        cheapest = min(mode_options, key=lambda x: x["cost"])
        greenest = min(mode_options, key=lambda x: x["carbon_kg"])
        mode_summary.append(
            {
                "mode": mode,
                "count": len(mode_options),
                "min_cost": cheapest["cost"],
                "min_duration": min(x["duration_min"] for x in mode_options),
                "min_carbon": greenest["carbon_kg"],
            }
        )

    greener_alternatives = sorted(compare_pool, key=lambda x: x["carbon_kg"])[:3]

    return {
        "distance_km": round(distance_km, 1),
        "all_options": options,
        "valid_options": valid_options,
        "best_option": best_option,
        "co2_saved": co2_saved,
        "mode_summary": mode_summary,
        "options_by_mode": by_mode,
        "greener_alternatives": greener_alternatives,
        "arrival_constraint": required_arrival_dt.strftime("%H:%M"),
    }


def compute_full_trip(destination: str) -> dict[str, list[dict[str, Any]]]:
    with get_connection() as conn:
        hotels = conn.execute(
            """
            SELECT name, nightly_cost, eco_score, notes
            FROM eco_hotels
            WHERE lower(city) = lower(?)
            ORDER BY eco_score DESC, nightly_cost ASC
            LIMIT 5
            """,
            (destination,),
        ).fetchall()

        places = conn.execute(
            """
            SELECT place_name, category, notes
            FROM eco_places
            WHERE lower(city) = lower(?)
            ORDER BY category, place_name
            LIMIT 8
            """,
            (destination,),
        ).fetchall()

        local_transport = conn.execute(
            """
            SELECT mode, notes, carbon_level
            FROM local_transport
            WHERE lower(city) = lower(?)
            ORDER BY
                CASE carbon_level
                    WHEN 'very low' THEN 1
                    WHEN 'low' THEN 2
                    ELSE 3
                END
            """,
            (destination,),
        ).fetchall()

    hotel_data = [dict(x) for x in hotels]
    place_data = [dict(x) for x in places]
    local_data = [dict(x) for x in local_transport]

    if not hotel_data:
        hotel_data = [
            {
                "name": "Community Eco Stay",
                "nightly_cost": 3200,
                "eco_score": 80,
                "notes": "Local sourcing and reduced single-use plastic",
            }
        ]
    if not place_data:
        place_data = [
            {
                "place_name": "City Botanical Park",
                "category": "park",
                "notes": "Low-impact outdoor activity recommendation",
            }
        ]
    if not local_data:
        local_data = [
            {
                "mode": "Walking",
                "notes": "Best for short local trips",
                "carbon_level": "very low",
            },
            {
                "mode": "Public Transport",
                "notes": "Prefer buses and metro over private cabs",
                "carbon_level": "low",
            },
        ]

    return {
        "hotels": hotel_data,
        "places": place_data,
        "local_transport": local_data,
        "low_traffic_route_tip": (
            "Prefer transit corridors and green-walk streets during peak hours "
            "to reduce congestion exposure."
        ),
    }


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/plan", methods=["POST"])
def plan():
    source = request.form.get("source", "").strip()
    destination = request.form.get("destination", "").strip()
    travel_date = request.form.get("travel_date", "").strip()
    required_arrival = request.form.get("required_arrival", "").strip()
    mode = request.form.get("mode", "transport").strip().lower()
    if mode not in {"transport", "full"}:
        mode = "transport"

    if not all([source, destination, travel_date, required_arrival]):
        return render_template(
            "index.html",
            error="Please fill all required fields before generating a plan.",
        )

    try:
        transport_plan = compute_transport_plan(
            source=source,
            destination=destination,
            travel_date=travel_date,
            required_arrival=required_arrival,
        )
    except ValueError:
        return render_template(
            "index.html",
            error="Invalid date/time format. Please choose valid values.",
        )

    full_trip = compute_full_trip(destination) if mode == "full" else None

    return render_template(
        "dashboard.html",
        form_data={
            "source": source,
            "destination": destination,
            "travel_date": travel_date,
            "required_arrival": required_arrival,
            "mode": mode,
        },
        transport_plan=transport_plan,
        full_trip=full_trip,
    )


if __name__ == "__main__":
    app.run(debug=True)
