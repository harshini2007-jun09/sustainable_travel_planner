"""
Sustainable Travel Planner - Flask Backend
Main application entry point
"""

from flask import Flask, render_template, request, jsonify, session
from travel_logic import TravelPlanner
from database import init_db, save_trip, get_recent_trips
import json

app = Flask(__name__)
app.secret_key = "eco_travel_secret_2024"

# Initialize database on startup
init_db()


@app.route("/")
def index():
    """Homepage with travel input form"""
    return render_template("index.html")


@app.route("/plan", methods=["POST"])
def plan_trip():
    """
    Main endpoint: receives travel inputs, calculates options,
    returns dashboard data as JSON
    """
    data = request.get_json()

    source = data.get("source", "")
    destination = data.get("destination", "")
    travel_date = data.get("travel_date", "")
    arrival_time = data.get("arrival_time", "")
    preference = data.get("preference", "eco")  # fastest | cheapest | eco

    if not source or not destination:
        return jsonify({"error": "Source and destination are required"}), 400

    # Use TravelPlanner to compute all options
    planner = TravelPlanner(source, destination, travel_date, arrival_time, preference)
    result = planner.compute()

    # Save trip to database
    save_trip(source, destination, travel_date, preference, result)

    return jsonify(result)


@app.route("/dashboard")
def dashboard():
    """Dashboard page - receives data via session or query param"""
    return render_template("dashboard.html")


@app.route("/recent-trips")
def recent_trips():
    """Fetch recent trips from database"""
    trips = get_recent_trips(limit=5)
    return jsonify(trips)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
