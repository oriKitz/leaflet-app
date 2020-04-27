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

$(function() {
    $('form[id="modal-layer-form-query"]').submit(function(e) {
        e.preventDefault();
        layerToken = chosenLayerToken
        chosenLayerToken = ''
        var form = $(this);
        name = $("#layer-name").val()
        share_team = $("#layer-share-team").is(":checked")
        form_serialized = "name=" + name + "&team=" + share_team
        layer = queryLayers[layerToken]
        data = {name: name,
                team: share_team,
                layer: getPointsFromLayer(layer)}
        $.ajax({
             type: "POST",
             url: '/layer-query',
             dataType: 'json',
             contentType: 'application/json',
             data: JSON.stringify(data),
             success: function(data)
             {
                 console.log(data)
             }
        });
        location.reload()
    });
});