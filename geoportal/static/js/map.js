var map = L.map('myMap').setView([32.1525104, 34.8601608], 13);
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
const tiles = L.tileLayer(tileUrl, { attribution });
tiles.addTo(map);

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
var drawControl = new L.Control.Draw({
    draw: {
        circle: false
    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

map.on('draw:created', function (e) {
    console.log(1)
    var layers = e.layers;
//    layers.eachLayer(function (layer) {
//         //do whatever you want; most likely save back to db
//    });
    });

// This 2 lines disable somehow my queries shit:
//var toolbar = L.Toolbar();
//toolbar.addToolbar(map);

function popUp(f, l){
    var out = [];
    if (f.properties) {
        for (key in f.properties) {
//            out.push(key+": "+f.properties[key]);
            out.push(f.properties[key]);
        }
        l.bindPopup(out.join("<br />"));
    }
}

function addLayer(data) {
    icon = getIcon()
    L.geoJSON(data,{onEachFeature:popUp, pointToLayer: function(geoJsonPoint, latlng) {
        return L.marker(latlng, {
            icon: icon
        })
     }}).addTo(map);
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getIcon() {
    if (Array.isArray(unused_icons) && unused_icons.length) {
        icon = unused_icons.shift()
        used_icons.push(icon)
        return icon
    } else {
        return icons[getRandomInt(0, 7)]
    }
}
