"""
travel_logic.py - Core logic for Sustainable Travel Planner

Handles:
- Distance estimation between cities
- Carbon footprint calculation per transport mode
- Filtering by arrival time constraints
- Ranking options by user preference
- Generating smart recommendations
"""

import math
import random
from datetime import datetime, timedelta


# ─── Emission factors (kg CO₂ per km per passenger) ──────────────────────────
EMISSION_FACTORS = {
    "flight": 0.15,
    "train": 0.04,
    "bus":   0.06,
    "car":   0.12,
}

# ─── Average speeds (km/h, including typical boarding/delays) ─────────────────
AVERAGE_SPEEDS = {
    "flight": 750,   # includes ~2h airport overhead
    "train":  120,
    "bus":    70,
    "car":    90,
}

# ─── Cost per km (USD approx) ─────────────────────────────────────────────────
COST_PER_KM = {
    "flight": 0.12,
    "train":  0.07,
    "bus":    0.04,
    "car":    0.09,
}

# ─── Fixed overheads (time in hours) ─────────────────────────────────────────
TIME_OVERHEAD = {
    "flight": 2.5,   # airport check-in, security, boarding
    "train":  0.3,
    "bus":    0.25,
    "car":    0.0,
}

# ─── Icons and display names ──────────────────────────────────────────────────
TRANSPORT_META = {
    "flight": {"icon": "✈️",  "label": "Flight"},
    "train":  {"icon": "🚆",  "label": "Train"},
    "bus":    {"icon": "🚌",  "label": "Bus"},
    "car":    {"icon": "🚗",  "label": "Car"},
}

# ─── Eco score thresholds (kg CO₂) ───────────────────────────────────────────
def get_eco_score(co2_kg: float) -> dict:
    """Return eco score label and color class based on CO₂ emissions."""
    if co2_kg < 20:
        return {"label": "Green",    "class": "eco-green",    "badge": "🌿"}
    elif co2_kg < 80:
        return {"label": "Moderate", "class": "eco-moderate", "badge": "🌱"}
    else:
        return {"label": "High",     "class": "eco-high",     "badge": "⚠️"}


# ─── City coordinates (lat, lon) – a curated lookup table ────────────────────
CITY_COORDS = {
    # India
    "mumbai":     (19.076, 72.877),
    "delhi":      (28.613, 77.209),
    "bangalore":  (12.972, 77.594),
    "bengaluru":  (12.972, 77.594),
    "chennai":    (13.083, 80.270),
    "hyderabad":  (17.385, 78.486),
    "kolkata":    (22.572, 88.363),
    "pune":       (18.520, 73.857),
    "ahmedabad":  (23.023, 72.572),
    "jaipur":     (26.912, 75.787),
    "goa":        (15.299, 74.124),
    # International
    "london":     (51.507, -0.127),
    "paris":      (48.856, 2.352),
    "new york":   (40.712, -74.006),
    "tokyo":      (35.689, 139.692),
    "dubai":      (25.204, 55.270),
    "singapore":  (1.352,  103.820),
    "sydney":     (-33.868, 151.209),
    "berlin":     (52.520, 13.405),
    "rome":       (41.902, 12.496),
    "barcelona":  (41.385, 2.173),
    "amsterdam":  (52.370, 4.895),
    "bangkok":    (13.756, 100.502),
    "toronto":    (43.653, -79.383),
    "los angeles":(34.052, -118.243),
    "chicago":    (41.878, -87.630),
    "san francisco":(37.774, -122.419),
    "kuala lumpur":(3.140, 101.686),
    "hong kong":  (22.320, 114.169),
    "istanbul":   (41.008, 28.978),
    "moscow":     (55.751, 37.618),
    "beijing":    (39.904, 116.407),
    "shanghai":   (31.230, 121.473),
    "cairo":      (30.044, 31.236),
    "cape town":  (-33.924, 18.424),
    "nairobi":    (-1.286, 36.817),
    "sao paulo":  (-23.550, -46.633),
    "buenos aires":(-34.603, -58.381),
    "mexico city":(19.432, -99.133),
}


def haversine_distance(city1: str, city2: str) -> float:
    """
    Calculate great-circle distance (km) between two cities using Haversine formula.
    Falls back to a pseudo-random plausible distance if cities not in lookup.
    """
    c1 = CITY_COORDS.get(city1.lower().strip())
    c2 = CITY_COORDS.get(city2.lower().strip())

    if c1 and c2:
        lat1, lon1 = math.radians(c1[0]), math.radians(c1[1])
        lat2, lon2 = math.radians(c2[0]), math.radians(c2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return round(c * 6371, 1)  # Earth radius = 6371 km

    # Fallback: generate a plausible distance seeded by city names for consistency
    seed = sum(ord(ch) for ch in city1 + city2)
    random.seed(seed)
    return round(random.uniform(200, 2500), 1)


def calculate_carbon(distance_km: float, mode: str) -> float:
    """Calculate CO₂ emissions in kg for given distance and transport mode."""
    factor = EMISSION_FACTORS.get(mode, 0.10)
    return round(distance_km * factor, 2)


def calculate_travel_time(distance_km: float, mode: str) -> float:
    """
    Calculate travel time in hours including mode-specific overheads.
    Returns float hours.
    """
    speed = AVERAGE_SPEEDS[mode]
    overhead = TIME_OVERHEAD[mode]
    raw_time = distance_km / speed
    return round(raw_time + overhead, 2)


def calculate_cost(distance_km: float, mode: str) -> float:
    """Estimate one-way ticket cost in USD."""
    base = distance_km * COST_PER_KM[mode]
    # Flights have a minimum base price
    if mode == "flight":
        base = max(base, 60)
    elif mode == "train":
        base = max(base, 10)
    elif mode == "bus":
        base = max(base, 5)
    elif mode == "car":
        base = max(base, 8)
    return round(base, 2)


def hours_to_display(hours: float) -> str:
    """Convert decimal hours to 'Xh Ym' display string."""
    h = int(hours)
    m = int((hours - h) * 60)
    if h == 0:
        return f"{m}m"
    elif m == 0:
        return f"{h}h"
    return f"{h}h {m}m"


def parse_arrival_constraint(travel_date: str, arrival_time: str):
    """
    Parse the arrival deadline from date + time strings.
    Returns a datetime or None if parsing fails.
    """
    if not travel_date or not arrival_time:
        return None
    try:
        dt_str = f"{travel_date} {arrival_time}"
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except Exception:
        return None


def filter_by_arrival(options: list, departure_dt: datetime, arrival_deadline) -> list:
    """
    Remove transport options that cannot meet the arrival deadline.
    Assumes departure at 08:00 on travel date if not specified.
    """
    if not arrival_deadline:
        return options  # No constraint – return all

    valid = []
    for opt in options:
        arrival_dt = departure_dt + timedelta(hours=opt["travel_time_hours"])
        if arrival_dt <= arrival_deadline:
            opt["meets_deadline"] = True
            valid.append(opt)
        else:
            opt["meets_deadline"] = False

    return valid


def rank_options(options: list, preference: str) -> list:
    """
    Sort options by user preference:
    - eco      → lowest CO₂
    - fastest  → shortest travel time
    - cheapest → lowest cost
    """
    key_map = {
        "eco":      lambda x: x["co2_kg"],
        "fastest":  lambda x: x["travel_time_hours"],
        "cheapest": lambda x: x["cost_usd"],
    }
    sort_key = key_map.get(preference, key_map["eco"])
    return sorted(options, key=sort_key)


def build_recommendation(ranked: list, preference: str, all_options: list) -> dict:
    """
    Build smart recommendation text comparing best vs worst option.
    """
    if not ranked:
        return {}

    best = ranked[0]
    worst = max(all_options, key=lambda x: x["co2_kg"])

    co2_saved = round(worst["co2_kg"] - best["co2_kg"], 1)
    co2_pct   = round((co2_saved / worst["co2_kg"]) * 100) if worst["co2_kg"] > 0 else 0

    pref_labels = {
        "eco":      "most eco-friendly",
        "fastest":  "fastest",
        "cheapest": "most budget-friendly",
    }

    explanation = f"The {best['label']} is the {pref_labels.get(preference, 'best')} option. "
    if co2_saved > 0:
        explanation += f"It saves {co2_saved} kg CO₂ ({co2_pct}%) compared to flying."

    return {
        "mode":        best["mode"],
        "label":       best["label"],
        "icon":        best["icon"],
        "explanation": explanation,
        "co2_saved":   co2_saved,
        "co2_pct":     co2_pct,
    }


def build_alternatives(ranked: list) -> list:
    """
    Generate greener alternative suggestion messages.
    """
    alts = []
    if len(ranked) < 2:
        return alts

    best_eco = min(ranked, key=lambda x: x["co2_kg"])
    flight   = next((o for o in ranked if o["mode"] == "flight"), None)
    train    = next((o for o in ranked if o["mode"] == "train"), None)
    bus      = next((o for o in ranked if o["mode"] == "bus"), None)

    if flight and train:
        pct = round(((flight["co2_kg"] - train["co2_kg"]) / flight["co2_kg"]) * 100)
        alts.append({
            "icon": "🚆",
            "text": f"Taking the train reduces emissions by {pct}% compared to flying.",
            "saving_pct": pct,
        })

    if flight and bus:
        pct = round(((flight["co2_kg"] - bus["co2_kg"]) / flight["co2_kg"]) * 100)
        alts.append({
            "icon": "🚌",
            "text": f"The bus cuts your carbon footprint by {pct}% versus a flight.",
            "saving_pct": pct,
        })

    if train and best_eco and best_eco["mode"] != "train":
        alts.append({
            "icon": "🌱",
            "text": f"Choosing {best_eco['label']} is the greenest option for this route.",
            "saving_pct": 0,
        })

    return alts[:3]


def build_eco_addons(destination: str) -> dict:
    """
    Generate sustainable travel add-on suggestions for the destination.
    """
    dest = destination.strip().title()
    return {
        "places": [
            {"icon": "🌿", "name": f"Nature Reserve near {dest}", "type": "Eco Park"},
            {"icon": "🏞️", "name": f"{dest} Botanical Garden", "type": "Green Space"},
            {"icon": "♻️", "name": f"Zero-waste Market, {dest}", "type": "Sustainable Shopping"},
        ],
        "hotels": [
            {"icon": "🏨", "name": f"EcoStay {dest}", "rating": "★★★★", "cert": "Green Key Certified"},
            {"icon": "🌱", "name": f"The Green Lodge, {dest}", "rating": "★★★", "cert": "LEED Certified"},
        ],
        "local_transport": [
            {"icon": "🚶", "mode": "Walking", "tip": "Most attractions within 2 km"},
            {"icon": "🚲", "mode": "Cycling", "tip": f"Bike rentals available in {dest} city centre"},
            {"icon": "🚇", "mode": "Metro / Bus", "tip": "Use local transit passes for savings"},
        ],
    }


class TravelPlanner:
    """
    Orchestrates the full trip planning computation.
    """

    def __init__(self, source, destination, travel_date, arrival_time, preference):
        self.source      = source
        self.destination = destination
        self.travel_date = travel_date
        self.arrival_time = arrival_time
        self.preference  = preference

    def compute(self) -> dict:
        """Run full computation and return structured dashboard data."""

        # 1. Distance
        distance = haversine_distance(self.source, self.destination)

        # 2. Parse departure datetime (assume 08:00 departure)
        dep_date = self.travel_date if self.travel_date else datetime.today().strftime("%Y-%m-%d")
        departure_dt = datetime.strptime(f"{dep_date} 08:00", "%Y-%m-%d %H:%M")
        arrival_deadline = parse_arrival_constraint(dep_date, self.arrival_time)

        # 3. Build all transport options
        all_options = []
        for mode in ["flight", "train", "bus", "car"]:
            co2       = calculate_carbon(distance, mode)
            time_hrs  = calculate_travel_time(distance, mode)
            cost      = calculate_cost(distance, mode)
            eco_score = get_eco_score(co2)
            meta      = TRANSPORT_META[mode]

            all_options.append({
                "mode":              mode,
                "label":             meta["label"],
                "icon":              meta["icon"],
                "co2_kg":            co2,
                "travel_time_hours": time_hrs,
                "travel_time_display": hours_to_display(time_hrs),
                "cost_usd":          cost,
                "eco_score":         eco_score,
                "meets_deadline":    True,  # updated below
            })

        # 4. Filter by arrival constraint
        valid_options = filter_by_arrival(all_options, departure_dt, arrival_deadline)

        # Constraint message if nothing valid
        constraint_msg = None
        if arrival_deadline and len(valid_options) == 0:
            constraint_msg = (
                "No transport options meet your required arrival time. "
                "Try adjusting your schedule or choosing a later arrival."
            )
            valid_options = all_options  # show all anyway with warning

        # 5. Rank by preference
        ranked = rank_options(valid_options, self.preference)
        if ranked:
            ranked[0]["recommended"] = True

        # 6. Recommendation + alternatives
        recommendation = build_recommendation(ranked, self.preference, all_options)
        alternatives   = build_alternatives(ranked)
        eco_addons     = build_eco_addons(self.destination)

        # 7. Trip summary
        best = ranked[0] if ranked else all_options[0]
        flight_co2 = next((o["co2_kg"] for o in all_options if o["mode"] == "flight"), best["co2_kg"])
        co2_saved  = round(flight_co2 - best["co2_kg"], 1)

        summary = {
            "total_cost":   best["cost_usd"],
            "total_co2":    best["co2_kg"],
            "co2_saved":    max(0, co2_saved),
            "travel_time":  best["travel_time_display"],
            "eco_message":  f"You saved {max(0, co2_saved)} kg CO₂ 🌳" if co2_saved > 0 else "Every eco choice counts! 🌍",
        }

        # 8. Chart data
        chart_data = {
            "labels": [o["label"] for o in all_options],
            "cost":   [o["cost_usd"] for o in all_options],
            "time":   [round(o["travel_time_hours"], 2) for o in all_options],
            "co2":    [o["co2_kg"] for o in all_options],
        }

        return {
            "source":          self.source,
            "destination":     self.destination,
            "distance_km":     distance,
            "travel_date":     self.travel_date,
            "preference":      self.preference,
            "options":         ranked,
            "all_options":     all_options,
            "recommendation":  recommendation,
            "alternatives":    alternatives,
            "eco_addons":      eco_addons,
            "summary":         summary,
            "chart_data":      chart_data,
            "constraint_msg":  constraint_msg,
        }
