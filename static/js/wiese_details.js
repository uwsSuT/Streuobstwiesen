const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

function newIcon (color) {
    return new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-' + color + '.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
        });
}

var ObstIcons = {
    'Apfel'     : newIcon('green'),
    'Birne'     : newIcon('yellow'),
    'Kirsche'   : newIcon('red'),
    'Zwetschge' : newIcon('violet'),
    'Nuss'      : newIcon('orange'),
    'Quitte'    : newIcon('grey'),
    'Mispel'    : newIcon('grey'),
    'unbekannt' : newIcon('blue'),
    'Tod'       : newIcon('black')
};

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

const layer = JSON.parse(document.getElementById('sorten-layer').textContent);
const wiese_polygon = JSON.parse(document.getElementById('wiese-geo-data').textContent);

function popUp_and_ToolTip(feature, layer) {
    var text = "<table> <tr> <th> Baum Nr. </th>" +
                         "<td>" + layer.feature.properties.baum_nr + "</td>" +
                    "</tr>" +
                    "<tr> <th> Art </th>" +
                         "<td>" + layer.feature.properties.obst_type + "</td>" +
                    "</tr>" +
                    "<tr> <th> Sorte </th>" +
                         "<td>" + layer.feature.properties.sorte + "</td>" +
                    "</tr> </table>";
    layer.bindPopup(text);
    // ACHTUGNG: Dem ToolTip muss ein TEXT übergeben werden; Daher das '"" +'
    layer.bindTooltip("" + layer.feature.properties.baum_nr, {permanent: true});
}

// Schleife über die Sorten Layer
var points = {}
for (sorte in layer) {
    points[sorte] = L.geoJSON(layer[sorte], {
        pointToLayer: function(feature, latlng) {
                return L.marker(latlng, {
                       icon: ObstIcons[sorte]
                });
              },
        onEachFeature: popUp_and_ToolTip
    }); 
    points[sorte].addTo(map);
};


var basemaps = {
    "OSM": basemap
};
var overlays = {};
for (sorte in layer) {
    overlays[sorte] = points[sorte];
};

L.control.layers(basemaps, overlays, {
        collapsed: false
    }).addTo(map);

var poly = L.polygon(wiese_polygon).addTo(map)

map.fitBounds(poly.getBounds());


