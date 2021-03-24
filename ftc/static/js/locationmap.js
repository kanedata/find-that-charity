const GEOJSON_URL = 'https://findthatpostcode.uk/areas/{}.geojson';
const GEOPOINT_URL = 'https://findthatpostcode.uk/postcodes/{}.json';
const TILES = 'https://stamen-tiles-{s}.a.ssl.fastly.net/{style}/{z}/{x}/{y}.png';
var bounds = L.latLngBounds(
    L.latLng(49.8647440573549, -8.649995833304311),
    L.latLng(60.86078239016185, 1.763705609663519),
);
if (GEOCODES || ORG_LAT_LONGS) {
    var map = L.map('locationmap').setView([51.505, -0.09], 13);
    map.scrollWheelZoom.disable();
    L.tileLayer(TILES, { style: 'toner' }).addTo(map);
    map.fitBounds(bounds);

    if (GEOCODES) {
        geojsonbounds = L.latLngBounds();
        GEOCODES.forEach(function (geocode) {
            fetch(GEOJSON_URL.replace('{}', geocode))
                .then(response => response.json())
                .then(data => {
                    var layer = L.geoJSON(data, {
                        onEachFeature: function (feature, layer) {
                            if (feature.properties && feature.properties.name) {
                                layer.bindPopup(feature.properties.name);
                            }
                        }
                    }).addTo(map);
                    geojsonbounds.extend(layer.getBounds());
                    map.fitBounds(geojsonbounds);
                });
        });
    }

    if (ORG_LAT_LONGS) {
        ORG_LAT_LONGS.forEach((latlng) => {
            var point = L.latLng([
                latlng[0],
                latlng[1],
            ]);
            var marker = L.marker(point).addTo(map);
            marker.bindPopup(`<strong>${latlng[2]}</strong>: ${latlng[3]}`);
            bounds.extend(point);
            map.fitBounds(bounds);
        });
    }
}