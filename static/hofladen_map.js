const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const map = L.map('map', {
	center: [48.43128, 11.35208],
    zoom: 10
})

// add Hilgertshausen Rathaus als eigenen Layer
var rathaus = L.circleMarker([48.43128, 11.35208], {
	color : 'red',
	radius : 5,
	weight : 3
})
rathaus.addTo(map)

var basemap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', 
		{ attribution: attribution }
	).addTo(map);

const markers = JSON.parse(document.getElementById('markers-data').textContent);

var points = L.geoJSON(markers);

var markerCluster = L.markerClusterGroup();

points.addTo(markerCluster);
markerCluster.addTo(map);

map.fitBounds(feature.getBounds(), { padding: [100, 100] });


