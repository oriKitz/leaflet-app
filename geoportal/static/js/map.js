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
var latestLon, latestLat;
var userLayers = {}

map.on('draw:created', function (e) {
    console.log(e)
    var type = e.layerType;
    var layer = e.layer;
    latestLat = layer._latlng.lat
    latestLon = layer._latlng.lng
    drawnItems.addLayer(layer);
    toggleMarkerModal()
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

function addUserLayer(data, layerId) {
    feature = L.geoJSON(data,{onEachFeature:popUp, pointToLayer: function(geoJsonPoint, latlng) {
        return L.marker(latlng, {
            icon: blueIcon
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
        form_serialized = "name=" + name
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
