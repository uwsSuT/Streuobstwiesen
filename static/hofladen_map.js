const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const map = L.map('map', {
	center: [48.43128, 11.35208],
    zoom:10
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

function popUp(feature, layer) {
        var text = "<p><b>" + layer.feature.properties.name + "</b></p>" + 
                   "<p><b>Tel. Nr: " + layer.feature.properties.Telefon + "</b></p>" + 
                   "<p>" + layer.feature.properties.adresse + "<br>" +
                           layer.feature.properties.ort + "</p>" +
	               '<p><a target="_blank" rel="noopener noreferrer" href="' + 
	                layer.feature.properties.www + "\"</a>" + layer.feature.properties.www + "</p>"; 
	    layer.bindPopup(text);
    }
var points = L.geoJSON(markers, {
	onEachFeature: popUp
});
var clusters = L.markerClusterGroup();
clusters.addLayer(points).addTo(map);

map.fitBounds(feature.getBounds(), { padding: [100, 100] });


