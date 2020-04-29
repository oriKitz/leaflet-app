var map = L.map('myMap', {
    contextmenu: true,
    contextmenuWidth: 140,
    contextmenuItems: [{
        text: 'Center map here',
        callback: centerMap
    }]
}).setView([32.1525104, 34.8601608], 13);
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

var latestLon, latestLat;
var userLayers = {}
var allLayers = {}
var queryLayers = {}
var latestLayer;
var chosenLayerToken;

function centerMap (e) {
    map.panTo(e.latlng);
}

map.on('draw:created', function (e) {
    console.log(e)
    var type = e.layerType;
    var layer = e.layer;
    latestLat = layer._latlng.lat
    latestLon = layer._latlng.lng
    latestLayer = layer
    toggleMarkerModal()
});

map.on("popupopen", function(e) {
    var lat = e.popup._latlng.lat.toFixed(6)
    var lon = e.popup._latlng.lng.toFixed(6)
    $(function() {
        $("#current-point").val(lon + ", " + lat)
    })
})

map.on("click", function(e) {
    console.log(e)
    var lat = e.latlng.lat.toFixed(6)
    var lon = e.latlng.lng.toFixed(6)
    $(function() {
        $("#current-point").val(lon + ", " + lat)
    })
})

$(function() {
    $("#queried-layers").on('click', 'button[name="add-custom-layer"]', function(e) {
        chosenLayerToken = e.target.parentElement.dataset.token
    })
})

$(function() {
    $('#add-point').on('shown.bs.modal', function () {
        $('#description').focus()
    })
})

function popUp(f, l){
    var out = [];
    if (f.properties) {
        for (key in f.properties) {
            out.push(key + ": " + f.properties[key]);
//            out.push(f.properties[key]);
        }
        l.bindPopup(out.join("<br />"));
    }
}

function addLayer(data, queryName) {
    icon = getIcon()
    feature = L.geoJSON(data,{onEachFeature:popUp, pointToLayer: function(geoJsonPoint, latlng) {
        return L.marker(latlng, {
            icon: icon,
            contextmenu: true,
            contextmenuItems: [{
                text: 'Hide marker',
                callback: hideMarker,
                index: 0
            }, {
                text: 'Add to a Layer',
                callback: addMarkerToLayer,
                index: 1
            }, {
                separator: true,
                index: 2
            }]
        })
    }})
    feature.addTo(map);
    var token = makeId(10)
    queryLayers[token] = feature
    var layerHtml = '<div class="row custom-control custom-checkbox justify-content-between">'
    layerHtml += '<button type="button" name="add-custom-layer" data-token="' + token + '" class="btn btn-xs p-0 pb-3 mr-2 pr-3" data-toggle="modal" data-target="#add-layer-query"><span class="fa fa-plus mr-2"></span></button>'
    layerHtml += '<input type="checkbox" id="checkbox-' + token + '" class="custom-control-input" onclick="toggleQueryLayer(' + "'" + token + "'" +')">'
    layerHtml += '<label class="custom-control-label normal" style="font-size: 17px" for="checkbox-' + token + '">' + queryName + '</label></div>'
    $(function () {
        $("#queried-layers-header").css('display', '')
        $("#queried-layers").append(layerHtml)
        $("#checkbox-" + token)[0].checked = true
    })
}


function addUserLayer(data, layerId) {
    feature = L.geoJSON(data,{onEachFeature:popUp, pointToLayer: function(geoJsonPoint, latlng) {
        return L.marker(latlng, {
            icon: blueIcon,
            contextmenu: true,
            contextmenuItems: [{
                text: 'Remove marker',
                callback: removeMarker,
                index: 0
            },
            {
                text: 'Hide marker',
                callback: hideMarker,
                index: 1
            }, {
                separator: true,
                index: 2
            }]
        })
    }})
    feature.addTo(map);
    userLayers[layerId] = feature
}
