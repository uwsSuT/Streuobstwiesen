const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const map = L.map('map')

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: attribution }).addTo(map);

const markers = JSON.parse(document.getElementById('markers-data').textContent);

let feature = L.geoJSON(markers).bindPopup(function (layer) { 
	return "<p><b>" + layer.feature.properties.name + "</b></p>" + layer.feature.properties.www; 
}).addTo(map);

map.fitBounds(feature.getBounds(), { padding: [100, 100] });


