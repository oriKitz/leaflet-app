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
var latestLayer;

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

function hideMarker (e) {
    map.removeLayer(e.relatedTarget)
}

function removePointFromDB(layerId, lon, lat, e) {
    $.ajax({
         type: "POST",
         url: '/remove-point/' + layerId + '/' + lon + '/' + lat,
         success: function(data)
         {
             map.removeLayer(e.relatedTarget)
         }
    });
}

function removeMarker (e) {
//    map.panTo(e.latlng);
    var marker = e.relatedTarget
    var layer = marker._eventParents
    for (var k in layer) {
        layer_val = layer[k]
        for (var layerId in userLayers) {
            if (userLayers[layerId] == layer_val) {
                var lon = marker.feature.geometry.coordinates[0]
                var lat = marker.feature.geometry.coordinates[1]
                removePointFromDB(layerId, lon, lat, e)
            }
        }
    }
}

function addMarkerToLayer(e) {
    var marker = e.relatedTarget
    var lon = marker.feature.geometry.coordinates[0]
    var lat = marker.feature.geometry.coordinates[1]
    latestLon = lon
    latestLat = lat
    toggleMarkerModal()
}

function addLayer(data) {
    icon = getIcon()
    L.geoJSON(data,{onEachFeature:popUp, pointToLayer: function(geoJsonPoint, latlng) {
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
     }}).addTo(map);
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

function toggleLayer(layerId) {
    $(function() {
        var checkbox = $("#checkbox-" + layerId)
        if (checkbox.is(":checked")) {
            getShowLayer(layerId)
        }
        else {
            userLayers[layerId].removeFrom(map)
        }
    })
};

function getShowLayer(layerId) {
    $(function() {
        $.ajax({
             type: "GET",
             url: '/points/' + layerId,
             success: function(data)
             {
                 addUserLayer(data, layerId)
             }
        });
    })
}

function toggleMarkerModal() {
    $(function() {
        $("#add-point").modal('toggle')
    })
}

function toggleLayerModal() {
    $(function() {
        $("#add-layer").modal('toggle')
    })
}

$(function() {
    $('#add-point').on('shown.bs.modal', function () {
        $('#description').focus()
    })
})

$(function() {
    $('form[id="modal-form"]').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        given_description = $("#description").val()
        chosen_layer = $("#layer").val()
        form_serialized = "description=" + given_description + "&layer=" + chosen_layer + "&lon=" + latestLon + "&lat=" + latestLat
        $.ajax({
             type: "POST",
             url: '/point',
             data: form_serialized, // serializes the form's elements.
             success: function(data)
             {
                 console.log(data)
                 userLayers[data['layer_id']].addLayer(latestLayer)
             }
        });
        toggleMarkerModal()
    });
});

$(function() {
    $('form[id="modal-layer-form"]').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        name = $("#name").val()
        share_team = $("#share-team").is(":checked")
        form_serialized = "name=" + name + "&team=" + share_team
        $.ajax({
             type: "POST",
             url: '/layer',
             data: form_serialized, // serializes the form's elements.
             success: function(data)
             {
                 console.log(data)
             }
        });
        location.reload()
    });
});
