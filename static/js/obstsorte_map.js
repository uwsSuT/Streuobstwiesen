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

function popUp(feature, layer) {
    var text = "<p><b>" + layer.feature.properties.baum_nr + "</b></p>" +
               "<p>" + layer.feature.properties.sorte + "</p>";
                    
    layer.bindPopup(text);
}

var points = L.geoJSON(markers, {
	onEachFeature: BaumPopUp
});

// Wenn wir keine Gruppierung wollen kann man die Bäume auch direkt als Points setzen
points.addTo(map);

//map.fitBounds(feature.getBounds(), { padding: [100, 100] });


