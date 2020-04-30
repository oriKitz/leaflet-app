$(function() {
    $('form[id="modal-form"]').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        given_description = $("#description").val()
        chosen_layer = $("#layer option:selected")[0].id
        form_serialized = "description=" + given_description + "&layer=" + chosen_layer + "&lon=" + latestLon + "&lat=" + latestLat
        $.ajax({
            type: "POST",
            url: '/point',
            data: form_serialized, // serializes the form's elements.
            success: function(data)
            {
                latestLayer.options.icon = coloredIcons[data['color']]
                userLayers[data['layer_id']].addLayer(latestLayer)
            }
        });
        toggleMarkerModal()
        getAllLayers()
    });
});

function getLayerHtml(data) {
    var layerName = data['layer_name']
    var layerId = data['layer_id']
    var color = data['color']
    var htmlData = '<div class="row ml-2 mt-3 custom-control custom-checkbox justify-content-between" id="layer-' + layerId + '" data-color="' + color + '">'
    htmlData += '<input type="checkbox" id="checkbox-' + layerId  + '" class="custom-control-input" onclick="toggleLayer(' + layerId + ')">'
    htmlData += '<label class="custom-control-label" for="checkbox-' + layerId + '">' + layerName + '</label></div>'
    return htmlData
}

$(function() {
    $('form[id="modal-layer-form"]').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        name = $("#name").val()
        share_team = $("#share-team").is(":checked")
        color = $("#color").val()
        form_serialized = "name=" + name + "&team=" + share_team + "&color=" + color
        $.ajax({
            type: "POST",
            url: '/layer',
            data: form_serialized, // serializes the form's elements.
            success: function(data)
            {
                layerHtml = getLayerHtml(data)
                if (data['private']) {
                    $("#private-layers").append(layerHtml)
                } else {
                    $("#team-layers").append(layerHtml)
                }
                $("#layer").append('<option id="' + data['layer_id'] + '">' + data['layer_name'] + '</option>')
                getAllLayers()
                toggleLayerModal()
            }
        });
    });
});

$(function() {
    $('form[id="modal-layer-form-query"]').submit(function(e) {
        e.preventDefault();
        layerToken = chosenLayerToken
        var form = $(this);
        name = $("#layer-name").val()
        share_team = $("#layer-share-team").is(":checked")
        color = $("#color2").val()
        layer = queryLayers[layerToken]
        chosenLayerToken = ''
        data = {name: name,
                team: share_team,
                layer: getPointsFromLayer(layer),
                color: color}
        debugger
        $.ajax({
            type: "POST",
            url: '/layer-from-query',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(data)
            {
                console.log(data)
                layerHtml = getLayerHtml(data)
                if (data['private']) {
                    $("#private-layers").append(layerHtml)
                } else {
                    $("#team-layers").append(layerHtml)
                }
                $("#layer").append('<option id="' + data['layer_id'] + '">' + data['layer_name'] + '</option>')
                getAllLayers()
                toggleQueryLayerModal()
            }
        });
    });
});

$(function() {
    $('form[id="modal-layer-form-edit"]').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        name = $("#name-edit").val()
        share_team = $("#share-team-edit").is(":checked")
        color = $("#edit-color").val()
        form_serialized = "name=" + name + "&team=" + share_team + "&color=" + color
        $.ajax({
            type: "POST",
            url: '/edit-layer/' + editedLayerId,
            data: form_serialized, // serializes the form's elements.
            success: function(data)
            {
                console.log(data)
            }
        });
        location.reload()
    });
});


function getUserIdByName(username) {
    var u = $("#user")
    for (i = 0; i < u.children().length; i++) {
        var option = u.children()[i]
        if (option.innerText == username) {
            return option.id
        }
    }
    return null
}

$(function() {
    $('form[id="modal-form-team"]').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        user = $("#user").val()
        form_serialized = "user=" + getUserIdByName(user)
        $.ajax({
            type: "POST",
            url: '/add-user-to-team',
            data: form_serialized, // serializes the form's elements.
            success: function(data)
            {
                console.log(data)
            }
        });
        location.reload()
    });
});
