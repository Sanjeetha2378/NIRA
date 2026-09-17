from flask import Flask, render_template, jsonify, request
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
DATABASE = "nira.db"

DISTRICTS = {
    "Ariyalur": (11.1401, 79.0786),
    "Chengalpattu": (12.6819, 79.9677),
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Cuddalore": (11.7480, 79.7714),
    "Dharmapuri": (12.1211, 78.1582),
    "Dindigul": (10.3673, 77.9803),
    "Erode": (11.3410, 77.7172),
    "Kallakurichi": (11.7404, 78.9590),
    "Kancheepuram": (12.8342, 79.7036),
    "Karur": (10.9601, 78.0766),
    "Krishnagiri": (12.5186, 78.2137),
    "Madurai": (9.9252, 78.1198),
    "Mayiladuthurai": (11.1035, 79.6520),
    "Nagapattinam": (10.7672, 79.8449),
    "Namakkal": (11.2194, 78.1677),
    "Perambalur": (11.2320, 78.8801),
    "Pudukkottai": (10.3797, 78.8208),
    "Ramanathapuram": (9.3639, 78.8395),
    "Ranipet": (12.9249, 79.3333),
    "Salem": (11.6643, 78.1460),
    "Sivaganga": (9.8433, 78.4809),
    "Tenkasi": (8.9590, 77.3152),
    "Thanjavur": (10.7870, 79.1378),
    "The Nilgiris": (11.4102, 76.6950),
    "Theni": (10.0104, 77.4768),
    "Thoothukudi": (8.7642, 78.1348),
    "Tiruchirappalli": (10.7905, 78.7047),
    "Tirunelveli": (8.7139, 77.7567),
    "Tirupathur": (12.4960, 78.5600),
    "Tiruppur": (11.1085, 77.3411),
    "Tiruvallur": (13.1439, 79.9080),
    "Tiruvannamalai": (12.2253, 79.0747),
    "Tiruvarur": (10.7726, 79.6368),
    "Vellore": (12.9165, 79.1325),
    "Viluppuram": (11.9401, 79.4861),
    "Virudhunagar": (9.5851, 77.9535),
    "Kanyakumari": (8.0883, 77.5385)
}


def init_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            rainfall REAL,
            water_level REAL DEFAULT 0,
            drainage TEXT DEFAULT 'AUTOMATIC',
            risk_score REAL,
            risk_level TEXT,
            temperature REAL DEFAULT 0,
            wind REAL DEFAULT 0,
            weather TEXT DEFAULT '',
            created_at TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(risk_analysis)")
    columns = [row[1] for row in cursor.fetchall()]

    if "temperature" not in columns:
        cursor.execute("""
            ALTER TABLE risk_analysis
            ADD COLUMN temperature REAL DEFAULT 0
        """)

    if "wind" not in columns:
        cursor.execute("""
            ALTER TABLE risk_analysis
            ADD COLUMN wind REAL DEFAULT 0
        """)

    if "weather" not in columns:
        cursor.execute("""
            ALTER TABLE risk_analysis
            ADD COLUMN weather TEXT DEFAULT ''
        """)

    if "created_at" not in columns:
        cursor.execute("""
            ALTER TABLE risk_analysis
            ADD COLUMN created_at TEXT
        """)

    conn.commit()
    conn.close()


def save_analysis(
    location,
    rainfall,
    temperature,
    wind,
    weather,
    score,
    level
):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO risk_analysis
        (
            location,
            rainfall,
            water_level,
            drainage,
            risk_score,
            risk_level,
            temperature,
            wind,
            weather,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        location,
        rainfall,
        0,
        "AUTOMATIC",
        score,
        level,
        temperature,
        wind,
        weather,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify({
        "system": "NIRA",
        "status": "online"
    })


@app.route("/api/location")
def location_search():

    location = request.args.get("name", "").strip()

    if not location:
        return jsonify({
            "success": False,
            "error": "District is required"
        }), 400

    if location not in DISTRICTS:
        return jsonify({
            "success": False,
            "error": "Tamil Nadu district not found"
        }), 404

    latitude, longitude = DISTRICTS[location]

    print("")
    print("===================================")
    print("NIRA DISTRICT SELECTED")
    print("District :", location)
    print("Latitude :", latitude)
    print("Longitude:", longitude)
    print("===================================")
    print("")

    return jsonify({
        "success": True,
        "name": location,
        "latitude": latitude,
        "longitude": longitude,
        "country": "India",
        "admin1": "Tamil Nadu",
        "timezone": "Asia/Kolkata"
    })


@app.route("/api/weather")
def weather():

    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:
        return jsonify({
            "success": False,
            "error": "Coordinates required"
        }), 400

    try:

        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "precipitation,"
                    "rain,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            },
            headers={
                "User-Agent": "NIRA-College-Project/1.0"
            },
            timeout=8
        )

        if response.status_code == 429:

            print("")
            print("OPEN-METEO RATE LIMIT")
            print("Using safe demo fallback")
            print("")

            return jsonify({
                "success": True,
                "temperature": 30.0,
                "rainfall": 0.0,
                "wind": 10.0,
                "weather": "Weather service temporarily limited",
                "fallback": True
            })

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})

        temperature = float(
            current.get("temperature_2m", 0)
        )

        precipitation = float(
            current.get("precipitation", 0)
        )

        rain = float(
            current.get("rain", precipitation)
        )

        wind = float(
            current.get("wind_speed_10m", 0)
        )

        weather_code = current.get(
            "weather_code",
            0
        )

        weather_name = get_weather_description(
            weather_code
        )

        print("")
        print("LIVE WEATHER")
        print("Temperature:", temperature)
        print("Rain:", rain)
        print("Wind:", wind)
        print("Weather:", weather_name)
        print("")

        return jsonify({
            "success": True,
            "temperature": round(temperature, 1),
            "rainfall": round(rain, 1),
            "wind": round(wind, 1),
            "weather": weather_name
        })

    except requests.exceptions.RequestException as e:

        print("WEATHER NETWORK ERROR:", e)
        print("Using safe fallback")

        return jsonify({
            "success": True,
            "temperature": 30.0,
            "rainfall": 0.0,
            "wind": 10.0,
            "weather": "Weather service temporarily limited",
            "fallback": True
        })

    except Exception as e:

        print("WEATHER ERROR:", e)
        print("Using safe fallback")

        return jsonify({
            "success": True,
            "temperature": 30.0,
            "rainfall": 0.0,
            "wind": 10.0,
            "weather": "Weather service temporarily limited",
            "fallback": True
        })


def get_weather_description(code):

    descriptions = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Light Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        85: "Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Severe Thunderstorm with Hail"
    }

    return descriptions.get(
        code,
        "Unknown Weather"
    )


@app.route("/api/auto-analyze", methods=["POST"])
def auto_analyze():

    data = request.get_json(
        silent=True
    ) or {}

    location = str(
        data.get(
            "location",
            "Unknown Area"
        )
    )

    rainfall = float(
        data.get(
            "rainfall",
            0
        )
    )

    temperature = float(
        data.get(
            "temperature",
            0
        )
    )

    wind = float(
        data.get(
            "wind",
            0
        )
    )

    weather = str(
        data.get(
            "weather",
            "Unknown"
        )
    )

    score = 0

    # Rainfall risk
    if rainfall >= 30:
        score += 50
    elif rainfall >= 15:
        score += 35
    elif rainfall >= 5:
        score += 20
    elif rainfall > 0:
        score += 10

    # Weather risk
    weather_lower = weather.lower()

    if (
        "thunder" in weather_lower
        or "violent" in weather_lower
    ):
        score += 25

    elif (
        "heavy rain" in weather_lower
        or "heavy" in weather_lower
    ):
        score += 20

    elif (
        "moderate rain" in weather_lower
        or "rain showers" in weather_lower
    ):
        score += 10

    # Wind risk
    if wind >= 60:
        score += 20
    elif wind >= 40:
        score += 15
    elif wind >= 25:
        score += 8

    # Temperature risk
    if temperature >= 40:
        score += 10

    score = min(
        max(score, 0),
        100
    )

    if score >= 75:

        level = "CRITICAL"

        prediction = (
            "NIRA detects a critical environmental "
            "risk that may develop rapidly."
        )

        prevention = (
            "Move people away from vulnerable areas, "
            "notify the responsible authority, and "
            "follow emergency safety procedures."
        )

        expected_time = "Within 1–3 hours"

        reason = (
            "High-risk weather indicators are "
            "currently present."
        )

    elif score >= 50:

        level = "HIGH"

        prediction = (
            "NIRA predicts a high possibility of "
            "an emerging local risk."
        )

        prevention = (
            "Monitor the area closely, clear possible "
            "drainage blockages, and alert the "
            "respective in-charge."
        )

        expected_time = "Within 3–6 hours"

        reason = (
            "The combination of current weather "
            "conditions has increased the risk score."
        )

    elif score >= 25:

        level = "MODERATE"

        prediction = (
            "NIRA identifies a developing environmental "
            "risk that requires monitoring."
        )

        prevention = (
            "Continue monitoring the area and take "
            "preventive measures if conditions worsen."
        )

        expected_time = "Within 6–12 hours"

        reason = (
            "Moderate environmental signals "
            "were detected."
        )

    else:

        level = "LOW"

        prediction = (
            "NIRA currently detects a low "
            "environmental risk."
        )

        prevention = (
            "No immediate action is required. "
            "Continue normal monitoring of the area."
        )

        expected_time = "No immediate threat"

        reason = (
            "Current weather indicators "
            "remain relatively stable."
        )

    probability = score

    save_analysis(
        location,
        rainfall,
        temperature,
        wind,
        weather,
        score,
        level
    )

    return jsonify({
        "success": True,
        "location": location,
        "rainfall": round(rainfall, 1),
        "temperature": round(temperature, 1),
        "wind": round(wind, 1),
        "weather": weather,
        "score": score,
        "probability": probability,
        "level": level,
        "prediction": prediction,
        "expectedTime": expected_time,
        "reason": reason,
        "prevention": prevention
    })


@app.route("/api/history")
def history():

    try:

        conn = sqlite3.connect(
            DATABASE
        )

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                location,
                rainfall,
                water_level,
                drainage,
                risk_score,
                risk_level,
                temperature,
                wind,
                weather,
                created_at
            FROM risk_analysis
            ORDER BY id DESC
            LIMIT 20
        """)

        rows = cursor.fetchall()

        conn.close()

        history_data = []

        for row in rows:

            history_data.append({
                "id": row["id"],
                "location": row["location"],
                "rainfall": row["rainfall"],
                "waterLevel": row["water_level"],
                "drainage": row["drainage"],
                "score": row["risk_score"],
                "level": row["risk_level"],
                "temperature": row["temperature"],
                "wind": row["wind"],
                "weather": row["weather"],
                "createdAt": row["created_at"]
            })

        return jsonify(
            history_data
        )

    except Exception as e:

        print(
            "HISTORY ERROR:",
            e
        )

        return jsonify([])


init_database()


if __name__ == "__main__":

    print("")
    print("===================================")
    print("        NIRA SYSTEM STARTED")
    print("===================================")
    print(
        "NIRA: Networked Intelligent Risk Analyzer"
    )
    print(
        "Location: Tamil Nadu - 38 Districts"
    )
    print(
        "Live Weather: Enabled"
    )
    print(
        "Risk Analysis: Enabled"
    )
    print(
        "Database: SQLite"
    )
    print("===================================")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )