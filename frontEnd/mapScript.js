
const mapConfigElement = document.getElementById('map-config');
const mapConfig = JSON.parse(mapConfigElement.textContent);
const map = L.map('map').setView(mapConfig.center, mapConfig.zoom);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let highlightedRoads = [];

// Create this once, outside the function
let routeLayer = L.layerGroup().addTo(map);

async function highlightRoads(path) {

    // Clear the previous route and stopping points
    routeLayer.clearLayers();

    const coordinates = path.map(point => [
        point.latitude,
        point.longitude
    ]);

    // Draw the new route
    const route = L.polyline(coordinates, {
        color: "#007bff",
        weight: 6,
        opacity: 0.85
    }).addTo(routeLayer);

    // Highlight every stopping point in red
    path.forEach((point, index) => {

        L.circleMarker(
            [point.latitude, point.longitude],
            {
                radius: 7,
                color: "#990000",
                fillColor: "#ff0000",
                fillOpacity: 1,
                weight: 2
            }
        )
        .bindPopup(`Stopping Point ${index + 1}`)
        .addTo(routeLayer);

    });

    // Zoom and center the map to fit the entire route
    map.fitBounds(route.getBounds(), {
        padding: [50, 50],
        maxZoom: 16
    });

    return route;
}


async function loadRequestByID(requestID) {
    try {
        const response = await fetch(`/requests/${requestID}`);

        if (!response.ok) {
            throw new Error("Failed to retrieve request");
        }

        const data = await response.json();

        highlightRoads(data.path)

    } catch (error) {
        console.error("Error retrieving request:", error);
    }
}





