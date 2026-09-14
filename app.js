// =========================================
// NIRA RISK ANALYSIS
// =========================================

async function checkRisk() {

    const location =
        document.getElementById("location").value.trim();

    const rainfall =
        document.getElementById("rainfall").value;

    const waterLevel =
        document.getElementById("waterLevel").value;

    const drainage =
        document.getElementById("drainage").value;


    // =========================================
    // INPUT VALIDATION
    // =========================================

    if (
        location === "" ||
        rainfall === "" ||
        waterLevel === ""
    ) {

        alert(
            "Please enter location, rainfall and water level before running NIRA analysis."
        );

        return;
    }


    try {

        const response = await fetch("/api/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                location: location,

                rainfall: rainfall,

                waterLevel: waterLevel,

                drainage: drainage

            })

        });


        if (!response.ok) {

            throw new Error(
                "Backend analysis failed."
            );

        }


        const result =
            await response.json();


        // =========================================
        // RISK SCORE
        // =========================================

        document.getElementById("riskScore").innerText =
            result.score + "%";


        document.getElementById("riskLevel").innerText =
            result.level;


        // =========================================
        // RISK MESSAGE
        // =========================================

        document.getElementById("riskMessage").innerText =

            "NIRA detected a " +
            result.level.toLowerCase() +
            " risk in " +
            result.location +
            " based on the available area data.";


        // =========================================
        // LIVE SIGNALS
        // =========================================

        document.getElementById("rainDisplay").innerText =
            result.rainfall + " mm";


        document.getElementById("waterDisplay").innerText =
            result.waterLevel + "%";


        const drainageDisplay =
            document.getElementById("drainageDisplay");


        if (drainageDisplay) {

            drainageDisplay.innerText =
                result.drainage.toUpperCase();

        }


        // =========================================
        // AI INSIGHT
        // =========================================

        document.getElementById("explanationText").innerText =

            result.prediction +

            " Probability: " +

            result.probability +

            "%. Expected: " +

            result.expectedTime +

            ". " +

            result.reason;


        // =========================================
        // PREVENTION
        // =========================================

        document.getElementById("actionText").innerText =
            result.prevention;


        // =========================================
        // RISK MAP UPDATE
        // =========================================

        updateRiskMap(result);


        // =========================================
        // EARLY WARNING
        // =========================================

        const warningCard =
            document.getElementById("warningCard");


        if (
            result.level === "HIGH" ||
            result.level === "CRITICAL"
        ) {

            if (warningCard) {

                warningCard.style.display = "flex";

            }


            // WARNING TITLE

            const warningTitle =
                document.getElementById(
                    "warningTitle"
                );


            if (warningTitle) {

                warningTitle.innerText =
                    result.level + " RISK DETECTED";

            }


            // WARNING TEXT

            const warningText =
                document.getElementById(
                    "warningText"
                );


            if (warningText) {

                warningText.innerText =

                    result.prediction +

                    " Immediate preventive action is recommended for " +

                    result.location +

                    ".";

            }


            // WARNING PROBABILITY

            const warningProbability =
                document.getElementById(
                    "warningProbability"
                );


            if (warningProbability) {

                warningProbability.innerText =

                    "Probability: " +
                    result.probability +
                    "%";

            }


            // WARNING TIME

            const warningTime =
                document.getElementById(
                    "warningTime"
                );


            if (warningTime) {

                warningTime.innerText =

                    "Expected: " +
                    result.expectedTime;

            }


            // =====================================
            // ALERT POPUP
            // =====================================

            alert(

                "🚨 NIRA EARLY WARNING\n\n" +

                "Location: " +
                result.location +

                "\nRisk Level: " +
                result.level +

                "\nProbability: " +
                result.probability +

                "%" +

                "\nExpected: " +
                result.expectedTime +

                "\n\nNearby people and the respective authority should take preventive action."

            );

        }

        else {

            if (warningCard) {

                warningCard.style.display = "none";

            }

        }


        // =========================================
        // REFRESH HISTORY
        // =========================================

        loadHistory();

    }


    catch (error) {

        console.error(
            "NIRA Error:",
            error
        );


        alert(

            "Unable to connect to NIRA backend.\n\n" +

            "Please make sure Flask is running."

        );

    }

}



// =========================================
// RISK MAP
// =========================================

function updateRiskMap(result) {

    const mapLocation =
        document.getElementById("mapLocation");

    const mapLocationCard =
        document.getElementById("mapLocationCard");

    const mapPredictionCard =
        document.getElementById("mapPredictionCard");

    const mapRiskBadge =
        document.getElementById("mapRiskBadge");

    const mapMarker =
        document.getElementById("mapMarker");


    // =========================================
    // LOCATION
    // =========================================

    if (mapLocation) {

        mapLocation.innerText =
            result.location;

    }


    if (mapLocationCard) {

        mapLocationCard.innerText =
            result.location;

    }


    // =========================================
    // PREDICTION
    // =========================================

    if (mapPredictionCard) {

        mapPredictionCard.innerText =

            result.level +
            " risk • " +
            result.probability +
            "% probability • " +
            result.expectedTime;

    }


    // =========================================
    // RISK BADGE
    // =========================================

    if (mapRiskBadge) {

        mapRiskBadge.innerText =
            result.level;

        // Reset classes

        mapRiskBadge.style.background =
            "rgba(255,255,255,0.06)";

        mapRiskBadge.style.borderColor =
            "rgba(255,255,255,0.08)";

        mapRiskBadge.style.color =
            "#9eb1c7";


        // LOW

        if (result.level === "LOW") {

            mapRiskBadge.style.background =
                "rgba(62,229,139,0.12)";

            mapRiskBadge.style.borderColor =
                "rgba(62,229,139,0.35)";

            mapRiskBadge.style.color =
                "#3ee58b";

        }


        // MODERATE

        else if (result.level === "MODERATE") {

            mapRiskBadge.style.background =
                "rgba(255,209,102,0.12)";

            mapRiskBadge.style.borderColor =
                "rgba(255,209,102,0.35)";

            mapRiskBadge.style.color =
                "#ffd166";

        }


        // HIGH

        else if (result.level === "HIGH") {

            mapRiskBadge.style.background =
                "rgba(255,159,67,0.12)";

            mapRiskBadge.style.borderColor =
                "rgba(255,159,67,0.35)";

            mapRiskBadge.style.color =
                "#ff9f43";

        }


        // CRITICAL

        else if (result.level === "CRITICAL") {

            mapRiskBadge.style.background =
                "rgba(255,82,82,0.14)";

            mapRiskBadge.style.borderColor =
                "rgba(255,82,82,0.4)";

            mapRiskBadge.style.color =
                "#ff5252";

        }

    }


    // =========================================
    // MAP MARKER
    // =========================================

    if (mapMarker) {

        const markerDot =
            mapMarker.querySelector(".marker-dot");

        const markerPulse =
            mapMarker.querySelector(".marker-pulse");


        if (markerDot && markerPulse) {


            // LOW

            if (result.level === "LOW") {

                markerDot.style.background =
                    "#3ee58b";

                markerDot.style.boxShadow =
                    "0 0 20px rgba(62,229,139,0.8), 0 0 50px rgba(62,229,139,0.35)";

                markerPulse.style.background =
                    "rgba(62,229,139,0.12)";

            }


            // MODERATE

            else if (result.level === "MODERATE") {

                markerDot.style.background =
                    "#ffd166";

                markerDot.style.boxShadow =
                    "0 0 20px rgba(255,209,102,0.8), 0 0 50px rgba(255,209,102,0.35)";

                markerPulse.style.background =
                    "rgba(255,209,102,0.12)";

            }


            // HIGH

            else if (result.level === "HIGH") {

                markerDot.style.background =
                    "#ff9f43";

                markerDot.style.boxShadow =
                    "0 0 20px rgba(255,159,67,0.8), 0 0 50px rgba(255,159,67,0.35)";

                markerPulse.style.background =
                    "rgba(255,159,67,0.12)";

            }


            // CRITICAL

            else if (result.level === "CRITICAL") {

                markerDot.style.background =
                    "#ff5252";

                markerDot.style.boxShadow =
                    "0 0 20px rgba(255,82,82,0.8), 0 0 50px rgba(255,82,82,0.4)";

                markerPulse.style.background =
                    "rgba(255,82,82,0.14)";

            }

        }

    }

}



// =========================================
// SCROLL TO ANALYSIS
// =========================================

function scrollToAnalysis() {

    const analysis =
        document.getElementById("analysis");


    if (analysis) {

        analysis.scrollIntoView({

            behavior: "smooth"

        });

    }

}



// =========================================
// LOAD RISK HISTORY
// =========================================

async function loadHistory() {

    try {

        const response =
            await fetch("/api/history");


        if (!response.ok) {

            throw new Error(
                "Unable to load history."
            );

        }


        const history =
            await response.json();


        const historyBody =
            document.getElementById(
                "historyBody"
            );


        if (!historyBody) {

            return;

        }


        historyBody.innerHTML = "";


        // =========================================
        // NO HISTORY
        // =========================================

        if (history.length === 0) {

            historyBody.innerHTML = `

                <tr>

                    <td colspan="7">

                        No risk analysis recorded yet.

                    </td>

                </tr>

            `;

            return;

        }


        // =========================================
        // DISPLAY HISTORY
        // =========================================

        history.forEach(item => {

            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>
                    ${item.id}
                </td>

                <td>
                    ${item.location || "Unknown Area"}
                </td>

                <td>
                    ${item.rainfall} mm
                </td>

                <td>
                    ${item.waterLevel}%
                </td>

                <td>
                    ${item.drainage}
                </td>

                <td>
                    ${item.score}%
                </td>

                <td>
                    ${item.level}
                </td>

            `;


            historyBody.appendChild(row);

        });

    }


    catch (error) {

        console.error(
            "History Error:",
            error
        );

    }

}



// =========================================
// LOAD HISTORY WHEN PAGE OPENS
// =========================================

loadHistory();