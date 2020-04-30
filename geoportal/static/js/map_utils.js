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

function getIcon() {
    if (Array.isArray(unused_icons) && unused_icons.length) {
        icon = unused_icons.shift()
        used_icons.push(icon)
        return icon
    } else {
        return icons[getRandomInt(0, 7)]
    }
}

function getLayerIcon(layerId) {
    layerDiv = window.document.getElementById("layer-" + layerId)
    color = layerDiv.dataset.color
    icon = coloredIcons[color]
    return icon
}

function getAllLayers() {
    $(function() {
        $.ajax({
            type: "GET",
            url: '/get-all-layers',
            success: function(data)
            {
                allLayers = data
            }
        });
    })
}

function showLayer(layerId) {
    addUserLayer(allLayers[layerId], layerId)
}

function getPointsFromLayer(layer) {
    var points = []
    for (key in layer._layers) {
        point = layer._layers[key]
        var lon = point._latlng.lng
        var lat = point._latlng.lat
        var description = point._popup._content
        points.push([lon, lat, description])
    }
    return points
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