var map = L.map('myMap', {
    contextmenu: true,
    contextmenuWidth: 140,
    contextmenuItems: [{
        text: 'Center map here',
        callback: centerMap
    }]
}).setView([33.247876, 37.485509], 6);
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

function initMap(lon, lat, zoom) {
    map.setView([lat, lon], zoom);
}

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
    var type = e.layerType;
    var layer = e.layer;
    if (type == 'marker') {
        latestLat = layer._latlng.lat
        latestLon = layer._latlng.lng
        latestLayer = layer
        toggleMarkerModal()
    }
    if (type == 'rectangle') {
        southWest = layer._bounds._southWest
        northEast = layer._bounds._northEast
        fromLat = southWest.lat
        toLat = northEast.lat
        fromLon = southWest.lng
        toLon = northEast.lng
        $("#from-lon").val(fromLon)
        $("#from-lat").val(fromLat)
        $("#to-lon").val(toLon)
        $("#to-lat").val(toLat)
    }
});

map.on("popupopen", function(e) {
    var lat = e.popup._latlng.lat.toFixed(6)
    var lon = e.popup._latlng.lng.toFixed(6)
    $(function() {
        $("#current-point").val(lon + ", " + lat)
    })
})

map.on("click", function(e) {
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
            if (key == 'description') {
                out.push(f.properties[key]);
            } else {
                out.push(key + ": " + f.properties[key]);
            }
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
    queryLayers[token] = feature
    feature.addTo(map);
    var token = makeId(10)
    var layerHtml = '<div class="row custom-control custom-checkbox justify-content-between ml-2 mt-3">'
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
    icon = getLayerIcon(layerId)
    feature = L.geoJSON(data,{onEachFeature:popUp, pointToLayer: function(geoJsonPoint, latlng) {
        return L.marker(latlng, {
            icon: icon,
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
