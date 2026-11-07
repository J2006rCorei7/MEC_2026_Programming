
const map = L.map('map').setView([43.6532, -79.3832], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let highlightedRoads = [];

async function highlightRoads(path) {

    // Clear previous route
    highlightedRoads.forEach(road => map.removeLayer(road));
    highlightedRoads = [];

    if (!path || path.length < 2) {
        console.error("Not enough nodes to calculate a route.");
        return;
    }

    // Get starting and ending coordinates
    const start = path[0];
    const end = path[path.length - 1];

    // OSRM expects longitude,latitude
    const coordinates =
        `${start.longitude},${start.latitude};` +
        `${end.longitude},${end.latitude}`;

    const url =
        `https://router.project-osrm.org/route/v1/driving/${coordinates}?overview=full&geometries=geojson`;

    try {

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("OSRM request failed");
        }

        const data = await response.json();

        if (data.code !== "Ok" || !data.routes.length) {
            throw new Error("No route found");
        }

        // Extract road-following geometry
        const routeCoordinates = data.routes[0].geometry.coordinates;

        // Convert [longitude, latitude] to [latitude, longitude]
        const latLngs = routeCoordinates.map(point => [
            point[1],
            point[0]
        ]);

        // Draw route
        const route = L.polyline(latLngs, {
            color: '#0066ff',
            weight: 6,
            opacity: 0.85
        }).addTo(map);

        highlightedRoads.push(route);

        // Zoom to route
        map.fitBounds(route.getBounds());

        // Display distance
        const distanceKm = data.routes[0].distance / 1000;

        console.log("Route distance:", distanceKm.toFixed(2), "km");

        return distanceKm;

    } catch (error) {
        console.error("Routing error:", error);
    }
}
