const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const map = L.map('map', {
	center: [48.43128, 11.35208],
	zoom: 14,
    maxZoom: 21,
    minZoom: 10
})

// add Hilgertshausen Rathaus als eigenen Layer
var rathaus = L.circleMarker([48.43128, 11.35208], {
	color : 'red',
	radius : 5,
	weight : 3
})
rathaus.addTo(map)

var basemap =  L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
	maxZoom: 20,
	attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}
	).addTo(map);

const markers = JSON.parse(document.getElementById('markers-data').textContent);
const wiesen = JSON.parse(document.getElementById('wiesen-data').textContent);

function popUp(feature, layer) {
    var text = "<p><b>" + layer.feature.properties.baum_nr + "</b></p>" +
               "<p>" + layer.feature.properties.sorte + "</p>";
                    
    layer.bindPopup(text);
}

var points = L.geoJSON(markers, {
	onEachFeature: popUp
});

function toolTip(feature, layer) {
    layer.bindTooltip(layer.feature.properties.Ort, {permanent: true});
}

var wiesen_poly = L.geoJSON(wiesen, {
    onEachFeature: toolTip
});
wiesen_poly.addTo(map)

var clusters = L.markerClusterGroup();

// Wenn wir keine Gruppierung wollen kann man die Bäume auch direkt als Points setzen
//points.addTo(map);

var clusters = L.markerClusterGroup();
clusters.addLayer(points).addTo(map);

var basemaps = {
    "OSM": basemap
};
var overlays = {
    "Streuobstwiesen": wiesen_poly,
    "Obstbäume": clusters,
};
L.control.layers(basemaps, overlays, {
        collapsed: false
    }).addTo(map);

map.fitBounds(feature.getBounds(), { padding: [100, 100] });


