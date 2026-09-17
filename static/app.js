let selectedLocation = "";
let selectedLatitude = null;
let selectedLongitude = null;


// =====================================
// LOCATION SEARCH
// =====================================

async function searchLocation() {

    const locationInput = document.getElementById("location");

    if (!locationInput) {
        alert("Location selector not found.");
        return;
    }

    const locationName = locationInput.value.trim();

    if (locationName === "") {
        alert("Please select a Tamil Nadu district.");
        return;
    }

    try {

        const response = await fetch(
            "/api/location?name=" + encodeURIComponent(locationName)
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert("Unable to find " + locationName + ".");
            return;
        }

        selectedLocation = data.name || locationName;
        selectedLatitude = data.latitude;
        selectedLongitude = data.longitude;

        await getAutomaticWeather();

    } catch (error) {

        console.error("Location Error:", error);

        alert(
            "Unable to find the selected district. Please try again."
        );
    }
}


// =====================================
// GET LIVE WEATHER
// =====================================

async function getAutomaticWeather() {

    if (
        selectedLatitude === null ||
        selectedLongitude === null
    ) {
        alert("Location coordinates are missing.");
        return;
    }

    try {

        const response = await fetch(
            "/api/weather?latitude=" +
            encodeURIComponent(selectedLatitude) +
            "&longitude=" +
            encodeURIComponent(selectedLongitude)
        );

        const weather = await response.json();

        if (!response.ok || !weather.success) {

            alert(
                weather.error ||
                "Unable to retrieve weather."
            );

            return;
        }


        // =====================================
        // UPDATE LIVE SIGNALS
        // =====================================

        const rainDisplay =
            document.getElementById("rainDisplay");

        const temperatureDisplay =
            document.getElementById("temperatureDisplay");

        const windDisplay =
            document.getElementById("windDisplay");

        const weatherDisplay =
            document.getElementById("weatherDisplay");


        if (rainDisplay) {
            rainDisplay.textContent =
                weather.rainfall + " mm";
        }

        if (temperatureDisplay) {
            temperatureDisplay.textContent =
                weather.temperature + "°C";
        }

        if (windDisplay) {
            windDisplay.textContent =
                weather.wind + " km/h";
        }

        if (weatherDisplay) {
            weatherDisplay.textContent =
                weather.weather;
        }


        // =====================================
        // RUN NIRA ANALYSIS
        // =====================================

        await runAutomaticAnalysis(weather);

    } catch (error) {

        console.error("Weather Error:", error);

        alert(
            "Unable to retrieve weather. Please try again."
        );
    }
}


// =====================================
// NIRA RISK ANALYSIS
// =====================================

async function runAutomaticAnalysis(weather) {

    try {

        const response = await fetch(
            "/api/auto-analyze",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    location: selectedLocation,

                    rainfall: weather.rainfall,

                    temperature: weather.temperature,

                    wind: weather.wind,

                    weather: weather.weather

                })
            }
        );


        const result = await response.json();


        if (!response.ok || !result.success) {

            alert(
                result.error ||
                "NIRA analysis failed."
            );

            return;
        }


        // =====================================
        // RISK SCORE
        // =====================================

        const riskScore =
            document.getElementById("riskScore");

        const riskLevel =
            document.getElementById("riskLevel");

        const riskMessage =
            document.getElementById("riskMessage");


        if (riskScore) {
            riskScore.textContent =
                result.score + "%";
        }


        if (riskLevel) {
            riskLevel.textContent =
                result.level;
        }


        if (riskMessage) {
            riskMessage.textContent =
                result.prediction;
        }


        // =====================================
        // AI INSIGHT
        // =====================================

        const explanationText =
            document.getElementById("explanationText");


        if (explanationText) {

            explanationText.textContent =
                result.reason ||
                "NIRA analyzed the available environmental signals.";
        }


        // =====================================
        // PREVENTION
        // =====================================

        const actionText =
            document.getElementById("actionText");


        if (actionText) {

            actionText.textContent =
                result.prevention ||
                "Continue monitoring the area and follow recommended safety measures.";
        }


        // =====================================
        // EARLY WARNING
        // =====================================

        updateEarlyWarning(result);


        // =====================================
        // RISK MAP
        // =====================================

        updateRiskMap(result);


        // =====================================
        // REFRESH HISTORY
        // =====================================

        loadHistory();

    } catch (error) {

        console.error(
            "Analysis Error:",
            error
        );

        alert(
            "NIRA analysis could not be completed."
        );
    }
}


// =====================================
// EARLY WARNING
// =====================================

function updateEarlyWarning(result) {

    const warningCard =
        document.getElementById("warningCard");

    const warningTitle =
        document.getElementById("warningTitle");

    const warningText =
        document.getElementById("warningText");

    const warningProbability =
        document.getElementById(
            "warningProbability"
        );

    const warningTime =
        document.getElementById(
            "warningTime"
        );


    if (warningTitle) {
        warningTitle.textContent =
            result.level + " RISK";
    }


    if (warningText) {
        warningText.textContent =
            result.prediction;
    }


    if (warningProbability) {
        warningProbability.textContent =
            "Probability: " +
            result.probability +
            "%";
    }


    if (warningTime) {
        warningTime.textContent =
            "Expected: " +
            result.expectedTime;
    }


    if (warningCard) {
        warningCard.style.display = "flex";
    }
}


// =====================================
// RISK MAP
// =====================================

function updateRiskMap(result) {

    const mapLocation =
        document.getElementById(
            "mapLocation"
        );

    const mapLocationCard =
        document.getElementById(
            "mapLocationCard"
        );

    const mapPredictionCard =
        document.getElementById(
            "mapPredictionCard"
        );

    const mapRiskBadge =
        document.getElementById(
            "mapRiskBadge"
        );


    if (mapLocation) {
        mapLocation.textContent =
            result.location;
    }


    if (mapLocationCard) {
        mapLocationCard.textContent =
            result.location;
    }


    if (mapPredictionCard) {
        mapPredictionCard.textContent =
            result.prediction;
    }


    if (mapRiskBadge) {
        mapRiskBadge.textContent =
            result.level;
    }
}


// =====================================
// MAIN BUTTON
// =====================================

function checkRisk() {

    searchLocation();

}


// =====================================
// SCROLL TO ANALYSIS
// =====================================

function scrollToAnalysis() {

    const analysis =
        document.getElementById(
            "analysis"
        );

    if (analysis) {

        analysis.scrollIntoView({
            behavior: "smooth"
        });

    }

}


// =====================================
// RISK HISTORY
// =====================================

async function loadHistory() {

    const historyBody =
        document.getElementById(
            "historyBody"
        );


    if (!historyBody) {
        return;
    }


    try {

        const response =
            await fetch("/api/history");

        const history =
            await response.json();


        if (
            !Array.isArray(history) ||
            history.length === 0
        ) {

            historyBody.innerHTML = `
                <tr>
                    <td colspan="7">
                        No risk analysis history available.
                    </td>
                </tr>
            `;

            return;
        }


        historyBody.innerHTML =
            history.map(item => `

                <tr>

                    <td>${item.id}</td>

                    <td>${item.location}</td>

                    <td>${item.rainfall ?? 0} mm</td>

                    <td>${item.waterLevel ?? 0}</td>

                    <td>${item.drainage ?? "AUTOMATIC"}</td>

                    <td>${item.score}%</td>

                    <td>${item.level}</td>

                </tr>

            `).join("");


    } catch (error) {

        console.error(
            "History Error:",
            error
        );

        historyBody.innerHTML = `
            <tr>
                <td colspan="7">
                    Unable to load risk history.
                </td>
            </tr>
        `;
    }
}


// =====================================
// LOAD HISTORY WHEN PAGE OPENS
// =====================================

loadHistory();