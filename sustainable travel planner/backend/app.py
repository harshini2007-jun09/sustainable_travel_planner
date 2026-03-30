
from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

def get_db():
    return sqlite3.connect('../database/data.db')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plan', methods=['POST'])
def plan():
    data = request.json

    # Dummy transport data
    options = [
        {"type": "Train", "cost": 500, "time": 5, "co2": 20},
        {"type": "Bus", "cost": 300, "time": 6, "co2": 30},
        {"type": "Flight", "cost": 2000, "time": 1, "co2": 100}
    ]

    best = min(options, key=lambda x: x["co2"])

    return jsonify({
        "options": options,
        "best": best,
        "message": f"You saved {100 - best['co2']} kg CO2 🌱"
    })

if __name__ == "__main__":
    app.run(debug=True)
