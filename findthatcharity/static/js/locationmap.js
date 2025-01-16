const GEOJSON_URL = 'https://findthatpostcode.uk/areas/{}.geojson';
const GEOPOINT_URL = 'https://findthatpostcode.uk/postcodes/{}.json';
const DEFAULT_BOUNDS = L.latLngBounds(
    L.latLng(49.8647440573549, -8.649995833304311),
    L.latLng(60.86078239016185, 1.763705609663519),
);
const MAX_ZOOM_BOUNDS = 8;

if (MARKER_ICON_OPTIONS) {
    Object.entries(MARKER_ICON_OPTIONS).forEach(([key, value]) => {
        L.Icon.Default.prototype.options[key] = value
    });
    L.Icon.Default.imagePath = '';
}

if (GEOCODES || ORG_LAT_LONGS) {
    var map = L.map('locationmap');
    map.scrollWheelZoom.disable();
    var layer = L.maplibreGL({
        style: 'https://tiles.openfreemap.org/styles/positron',
        attribution: `
    <a href="https://openfreemap.org" target="_blank">OpenFreeMap</a> 
    <a href="https://www.openmaptiles.org/" target="_blank">&copy; OpenMapTiles</a> 
    Data from <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>`,
    }).addTo(map);
    map.fitBounds(DEFAULT_BOUNDS);
    var bounds = L.latLngBounds();

    function updateBounds(layer) {
        bounds.extend(layer);
        map.fitBounds(bounds, {
            maxZoom: MAX_ZOOM_BOUNDS
        });
    }

    var layer_groups = {};
    if (GEOCODES) {
        geojsonbounds = L.latLngBounds();
        GEOCODES.forEach(function ([geocode_type, geocode]) {
            if (!layer_groups[geocode_type]) {
                layer_groups[geocode_type] = L.layerGroup().addTo(map);
            }
            fetch(GEOJSON_URL.replace('{}', geocode))
                .then(response => response.json())
                .then(data => {
                    var layer = L.geoJSON(data, {
                        onEachFeature: function (feature, layer) {
                            if (feature.properties && feature.properties.name) {
                                layer.bindPopup(`<strong>${geocode_type}</strong>: ${feature.properties.name}`);
                            }
                        }
                    })
                    layer_groups[geocode_type].addLayer(layer);
                    updateBounds(layer.getBounds());
                });
        });
    }

    if (ORG_LAT_LONGS) {
        ORG_LAT_LONGS.forEach((latlng) => {
            var point = L.latLng([
                latlng[0],
                latlng[1],
            ]);
            var group_label = latlng[2];
            if (latlng[2] == "Registered Office") {
                // group_label = `<img src="" /> ${latlng[2]}`;
                var marker = L.marker(point).bindPopup(`<strong>${latlng[2]}</strong>: ${latlng[3]}`);
            } else {
                var marker = L.circleMarker(point, {
                    radius: 4,
                    color: 'red',
                    weight: 4,
                    fill: true,
                    fillOpacity: 0,
                }).bindPopup(`<strong>${latlng[2]}</strong>: ${latlng[3]}`);
            }
            if (!layer_groups[group_label]) {
                layer_groups[group_label] = L.layerGroup().addTo(map);
            }
            layer_groups[group_label].addLayer(marker);
            updateBounds(point);
        });
    }
    L.control.layers(null, layer_groups, {
        collapsed: false,
    }).addTo(map);
    map.fitBounds(bounds);
}