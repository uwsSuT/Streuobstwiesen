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

const bluehwiesen = JSON.parse(document.getElementById('bluehwiesen-data').textContent);

function bluehToolTip(feature, layer) {
    // layer.bindTooltip('layer.feature.properties.Name', {permanent: true});
    var thref = layer.feature.properties.id;
    var pic = layer.feature.properties.wpic;

    // console.log('bluehToolTip' + pic)
    var htext = '<p>' +
            'Name: ' + layer.feature.properties.Name + 
            '<a href="' + thref + '">' + '<img src=' + pic + ' style="width:200px;"> </a>' + 
        '</p>';
    layer.bindPopup(htext);
}

function showInfo(e) {
    var maht = e.target.feature.properties.letzteMaht;
    var pic = '/static/images/bluehwiesen/Kunstpfad_Ost_Kunstobjekte/x.jpg'
    document.getElementById('WiesenInfo').innerHTML = maht + '<img src=' + pic +' style="width:100%;">';
    // console.log('showInfo' + pic)
}

var bluehwiesen_poly = L.geoJSON(bluehwiesen, {
    onEachFeature: bluehToolTip,
    style: {
        color: 'red'
    }
});
bluehwiesen_poly.addTo(map)

var basemaps = {
    "OSM": basemap
};
var overlays = {
    "Blühwiesen": bluehwiesen_poly,
};
L.control.layers(basemaps, overlays, {
        collapsed: false
    }).addTo(map);

map.fitBounds(bluehwiesen_poly.getBounds(), { padding: [100, 100] });


