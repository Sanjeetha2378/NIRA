from flask import Flask, render_template, jsonify, request, send_from_directory
import sqlite3

app = Flask(__name__, template_folder=".")


# =========================================
# STATIC FILES
# =========================================

@app.route("/style.css")
def style():
    return send_from_directory(".", "style.css")


@app.route("/app.js")
def javascript():
    return send_from_directory(".", "app.js")


# =========================================
# SAVE RISK ANALYSIS
# =========================================

def save_analysis(location, rainfall, water_level, drainage, score, level):

    conn = sqlite3.connect("nira.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO risk_analysis
        (location, rainfall, water_level, drainage, risk_score, risk_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        location,
        rainfall,
        water_level,
        drainage,
        score,
        level
    ))

    conn.commit()
    conn.close()


# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================
# SYSTEM STATUS
# =========================================

@app.route("/api/status")
def status():

    return jsonify({
        "system": "NIRA",
        "status": "online"
    })


# =========================================
# RISK ANALYSIS
# =========================================

@app.route("/api/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    location = data.get(
        "location",
        "Unknown Area"
    )

    rainfall = float(
        data.get("rainfall", 0)
    )

    water_level = float(
        data.get("waterLevel", 0)
    )

    drainage = data.get(
        "drainage",
        "good"
    )


    # =====================================
    # RISK SCORE
    # =====================================

    score = 0

    if rainfall > 80:
        score += 40

    elif rainfall > 50:
        score += 25

    else:
        score += 10


    if water_level > 75:
        score += 40

    elif water_level > 50:
        score += 25

    else:
        score += 10


    if drainage == "blocked":
        score += 20

    elif drainage == "poor":
        score += 10


    # =====================================
    # RISK LEVEL
    # =====================================

    if score >= 80:
        level = "CRITICAL"

    elif score >= 60:
        level = "HIGH"

    elif score >= 40:
        level = "MODERATE"

    else:
        level = "LOW"


    score = min(score, 100)


    # =====================================
    # PREDICTION DETAILS
    # =====================================

    if level == "CRITICAL":

        probability = 90

        prediction = (
            "Severe flooding may occur in "
            + location
            + "."
        )

        expected_time = "Within 1-3 hours"

        reason = (
            "High rainfall, rising water level "
            "and poor drainage are combining "
            "to increase the risk."
        )

        prevention = (
            "Alert nearby residents and authorities. "
            "Avoid low-lying roads and prepare "
            "emergency response."
        )


    elif level == "HIGH":

        probability = 75

        prediction = (
            "Flooding or waterlogging may develop "
            "in "
            + location
            + "."
        )

        expected_time = "Within 3-6 hours"

        reason = (
            "Rainfall and surrounding water "
            "conditions indicate an increasing "
            "local risk."
        )

        prevention = (
            "Monitor the area closely and inform "
            "nearby residents and the responsible "
            "authority."
        )


    elif level == "MODERATE":

        probability = 55

        prediction = (
            "Localized waterlogging may develop "
            "in "
            + location
            + " if conditions continue."
        )

        expected_time = "Within 6-12 hours"

        reason = (
            "Current environmental conditions "
            "show a moderate increase in risk."
        )

        prevention = (
            "Continue monitoring rainfall and "
            "water levels and keep drainage "
            "pathways clear."
        )


    else:

        probability = 25

        prediction = (
            "No major immediate risk is predicted "
            "in "
            + location
            + "."
        )

        expected_time = "Next 12 hours"

        reason = (
            "Current area conditions remain "
            "relatively stable."
        )

        prevention = (
            "Continue normal monitoring and "
            "maintain preventive measures."
        )


    # =====================================
    # SAVE RESULT
    # =====================================

    save_analysis(
        location,
        rainfall,
        water_level,
        drainage,
        score,
        level
    )


    # =====================================
    # SEND RESULT
    # =====================================

    return jsonify({

        "location": location,

        "score": score,

        "level": level,

        "rainfall": rainfall,

        "waterLevel": water_level,

        "drainage": drainage,

        "probability": probability,

        "prediction": prediction,

        "expectedTime": expected_time,

        "reason": reason,

        "prevention": prevention

    })


# =========================================
# RISK HISTORY
# =========================================

@app.route("/api/history")
def history():

    conn = sqlite3.connect("nira.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            location,
            rainfall,
            water_level,
            drainage,
            risk_score,
            risk_level
        FROM risk_analysis
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    history_data = []

    for row in rows:

        history_data.append({

            "id": row[0],

            "location": row[1],

            "rainfall": row[2],

            "waterLevel": row[3],

            "drainage": row[4],

            "score": row[5],

            "level": row[6]

        })

    return jsonify(history_data)


# =========================================
# START NIRA SERVER
# =========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
