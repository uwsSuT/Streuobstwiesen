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

mymap = L.map('map', {
	center: [48.43128, 11.35208],
	zoom: 14,
    maxZoom: 21,
    minZoom: 10
})

function find_me () {
    mymap.on('locationfound', function(e) {

      console.log('Location found!');

      var lat = e.latlng.lat;
      var lon = e.latlng.lng;
      var locationAccuracy = e.accuracy;
      var altitude = e.altitude;
      var altitudeAccuracy = e.altitudeAccuracy;
      var heading = e.heading;
      var speed = e.speed;
      var time = e.timestamp;

        var standort = L.circleMarker([lat, lon], {
            color : 'blue',
            radius : 5,
            weight : 3 
        });

    standort.addTo(mymap);
    mymap.setView([lat,lon]);

    });
}

function getLocation() {
    mymap.locate();
    find_me();
}

// add Hilgertshausen Rathaus als eigenen Layer
var rathaus = L.circleMarker([48.43128, 11.35208], {
	color : 'red',
	radius : 5,
	weight : 3
})
rathaus.addTo(mymap)

var basemap =  L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
	maxZoom: 20,
	attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}
	).addTo(mymap);

so_layer = JSON.parse(document.getElementById('sorten-layer').textContent);
wiese_polygon = JSON.parse(document.getElementById('wiese-geo-data').textContent);

// Schleife über die Sorten Layer
var points = {}
for (sorte in so_layer) {
    points[sorte] = L.geoJSON(so_layer[sorte], {
        pointToLayer: function(feature, latlng) {
                return L.marker(latlng, {
                       icon: ObstIcons[sorte]
                });
              },
        onEachFeature: BaumPopUp
    }); 
    points[sorte].addTo(mymap);
};


var basemaps = {
    "OSM": basemap
};
var overlays = {};
for (sorte in so_layer) {
    overlays[sorte] = points[sorte];
};

L.control.layers(basemaps, overlays, {
        collapsed: false
    }).addTo(mymap);

var poly = L.polygon(wiese_polygon).addTo(mymap)

mymap.fitBounds(poly.getBounds());


