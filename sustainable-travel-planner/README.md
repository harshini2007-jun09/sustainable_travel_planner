# 🌍 Sustainable Travel Planner

A full-stack web application that helps users choose travel options based on
**cost**, **time**, and **carbon footprint** — powered by Flask, SQLite, and
a rich JavaScript dashboard.

---

## 📂 Folder Structure

```
sustainable-travel-planner/
├── app.py              # Flask app entry point & routes
├── travel_logic.py     # Core logic: carbon calc, ranking, filtering
├── database.py         # SQLite persistence layer
├── requirements.txt    # Python dependencies
├── database/
│   └── trips.db        # Auto-created SQLite database
├── templates/
│   ├── index.html      # Homepage (input form)
│   └── dashboard.html  # Results dashboard
└── static/
    ├── css/
    │   └── main.css    # Full design system (green eco theme)
    └── js/
        ├── home.js     # Homepage interactions
        └── dashboard.js # Dashboard rendering + charts
```

---

## ⚙️ Setup & Run Locally

### Prerequisites
- Python 3.8 or higher
- pip

### Steps

```bash
# 1. Clone or download the project
cd sustainable-travel-planner

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask server
python app.py
```

Open your browser at **http://localhost:5000**

---

## 🌿 Features

### Homepage
- Source & destination input with city autocomplete
- Travel date and optional arrival deadline
- Preference selector: **Eco-Friendly** | **Fastest** | **Cheapest**

### Dashboard
| Section | Description |
|---|---|
| 🚦 Travel Options | Cards for Flight, Train, Bus, Car with cost/time/CO₂/eco score |
| 📊 Comparison Charts | Bar charts for cost, time, emissions side-by-side |
| 🌱 Smart Recommendation | Best option explanation with CO₂ savings |
| 🔄 Alternatives | Greener route suggestions with % savings |
| ⚠️ Constraint Handling | Filters options that miss arrival deadline |
| 🧾 Trip Summary | Total cost, CO₂, savings, eco message |
| 🌍 Eco Add-ons | Green places, hotels, local transport at destination |

### Carbon Calculation
```
CO₂ (kg) = Distance (km) × Emission Factor

Factors:
  ✈️ Flight : 0.15 kg CO₂/km
  🚆 Train  : 0.04 kg CO₂/km
  🚌 Bus    : 0.06 kg CO₂/km
  🚗 Car    : 0.12 kg CO₂/km
```

---

## 🛠 Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite (via sqlite3 stdlib) |
| Frontend | HTML5, CSS3 (custom variables), Vanilla JS |
| Charts | Chart.js 4 (CDN) |
| Fonts | Google Fonts (Playfair Display + DM Sans) |

---

## 🔌 API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/` | Homepage |
| POST | `/plan` | Compute trip options (JSON body) |
| GET | `/dashboard` | Dashboard page |
| GET | `/recent-trips` | Recent trip history (JSON) |

### POST `/plan` body
```json
{
  "source": "Mumbai",
  "destination": "Delhi",
  "travel_date": "2025-06-15",
  "arrival_time": "20:00",
  "preference": "eco"
}
```

---

## 🌍 Supported Cities (distance calculation)

Mumbai, Delhi, Bangalore, Chennai, Hyderabad, Kolkata, Pune, Ahmedabad,
Jaipur, Goa, London, Paris, New York, Tokyo, Dubai, Singapore, Sydney,
Berlin, Rome, Barcelona, Amsterdam, Bangkok, Toronto, Los Angeles,
Chicago, San Francisco, Kuala Lumpur, Hong Kong, Istanbul, Moscow,
Beijing, Shanghai, Cairo, Cape Town, Nairobi, São Paulo, Buenos Aires,
Mexico City.

For any city not in the list, a consistent pseudo-random distance is used
(seeded by city names for reproducibility).
