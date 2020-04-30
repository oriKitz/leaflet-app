var editedLayerId;

function deleteLayer(layerId) {
    $(function() {
        if (confirm("Are you sure you want do delete this layer?")) {
            $.ajax({
                 type: "POST",
                 url: '/delete-layer/' + layerId,
                 success: function(data)
                 {
                     $("#" + layerId).css('display', 'none')
                 }
            });
        }
    })
}

function editLayer(layerId) {
    $(function() {
        editedLayerId = layerId
        toggleEditLayerModal()
        row = $("#" + layerId)
        permission = row.children("td")[2].children[0].dataset.name
        if (permission == "share-team") {
            $("#share-team-edit")[0].checked = true
        }
        layer_name = row.children("td")[1].innerText
        $("#name-edit")[0].value = layer_name
    })
}

function deleteQuery(queryId) {
    $(function() {
        if (confirm("Are you sure you want do delete this layer?")) {
            $.ajax({
                 type: "POST",
                 url: '/delete-query/' + queryId,
                 success: function(data)
                 {
                     $("#" + queryId).css('display', 'none')
                 }
            });
        }
    })
}