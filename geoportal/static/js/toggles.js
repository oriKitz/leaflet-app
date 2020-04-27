// Map:

function hideMarker (e) {
    map.removeLayer(e.relatedTarget)
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

function toggleQueryLayer(token) {
    $(function() {
        var checkbox = $("#checkbox-" + token)
        if (checkbox.is(":checked")) {
            queryLayers[token].addTo(map)
        }
        else {
            queryLayers[token].removeFrom(map)
        }
    })
};

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

function toggleQueryLayerModal() {
    $(function() {
        $("#add-layer-query").modal('toggle')
    })
}


// Modals:

function toggleQueryModal() {
    $(function() {
        $("#run-query").modal('toggle')
    })
}


// Checkboxes:

function toggleFavOn(queryId) {
    $(function() {
        input = $("#mark-" + queryId)
        input[0].checked = true
    })
}


// Forms:

function openForm(form) {
    $(function() {
        form.style.display = "block";
    })
}

function closeForm(queryId) {
    $(document).ready(function() {
        form = $('form[name="' + queryId + '"]')
        form.html('')
        form.removeClass("mt-2")
    });
}
function closeFormQuery() {
    $(document).ready(function() {
        $("#params-form").html('')
    });
}


