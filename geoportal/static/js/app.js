var queryRunningInstances = {}
var queriesParams = {}
var queriesPolygonParams = {}

function filterQueries() {
    input = document.getElementById("queries_search");
    filter = input.value.toUpperCase();
    div = document.getElementById("right-sidebar");
    rows = div.getElementsByClassName("list-group")[0].children;
    for (i = 0; i < rows.length; i++) {
        txtValue = rows[i].textContent;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

function paging() {
    $(function () {
      $('#full-results').DataTable();
      $('.dataTables_length').addClass('bs-select');
    });
}

$(function() {
    $('form[id="geofile-upload"]').submit(function(e) {
        e.preventDefault();
        file = $("#geofile")[0].files[0]
        var formData = new FormData()
        formData.append('file', file)
        $.ajax({
            type: "POST",
            url: '/upload-file',
            data: formData,
            processData: false,  // tell jQuery not to process the data
            contentType: false,  // tell jQuery not to set contentType
            success: function(data) {
                addLayer(data['geojson'], data['filename'])
            }
        })
    })
});

function getParametersFormHTML(data, queryId) {
    formHTML = ''
    for (i = 0; i < data.length; i++) {
        formHTML += '<label class="form-control-label">' + data[i].parameter_name + '</label>'
        if (data[i].parameter_type == 'datetime') {
            formHTML += '<input class="form-control form-control-lg" type="date" id="' + data[i].parameter_name + '" name="' + data[i].parameter_name + '">'
        } else {
            formHTML += '<input class="form-control form-control-lg" type="text" id="' + data[i].parameter_name + '" name="' + data[i].parameter_name + '">'
        }
    }
    if (queryId in queriesPolygonParams) {
        formHTML += '<p class="mb-0"><b>Draw a rectangle to fill these fields</b></p>'
        formHTML += '<label class="form-control-label">From lon:</label>'
        formHTML += '<input class="form-control form-control-lg" type="text" id="from-lon" name="from-lon">'
        formHTML += '<label class="form-control-label">To lon:</label>'
        formHTML += '<input class="form-control form-control-lg" type="text" id="to-lon" name="to-lon">'
        formHTML += '<label class="form-control-label">From lat:</label>'
        formHTML += '<input class="form-control form-control-lg" type="text" id="from-lat" name="from-lat">'
        formHTML += '<label class="form-control-label">To lat:</label>'
        formHTML += '<input class="form-control form-control-lg" type="text" id="to-lat" name="to-lat">'
    }
    formHTML += '<button class="btn">Query</button>'
    formHTML += '<a class="btn" href="/query/' + queryId +'" target="_blank">Edit</a>'
    return formHTML
}

$(function() {
    $('button[name="query-selector"]').on("click", function() {
        button = $(this)
        form = button.next()
        queryId = button.attr('id')
        formHTML = getParametersFormHTML(queriesParams[queryId], queryId)
        formHTML += '<button type="button" class="btn cancel" name="cancel-btn" onclick="closeForm(' + queryId +')">Close</button>'
        form.addClass("mt-2")
        form.html(formHTML)
    })
})
;

function getAllQueriesParams() {
    $(function() {
        $.ajax({
            type: "GET",
            url: '/get-all-queries-params',
            success: function(data) {
                queriesParams = data
            }
        })
    })
};

function getAllQueriesPolygonParams() {
    $(function() {
        $.ajax({
            type: "GET",
            url: '/get-all-queries-polygon-params',
            success: function(data) {
                queriesPolygonParams = data
                console.log(data)
            }
        })
    })
};

$(function() {
    $('form[id="params-form"]').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        if (window.location.pathname.startsWith('/query')) {
            pathname = window.location.pathname
            splittedPathname = pathname.split("/")
            queryId = splittedPathname[splittedPathname.length - 1]
            $.ajax({
                 type: "POST",
                 url: '/table_results/' + queryId,
                 data: form.serialize(), // serializes the form's elements.
                 success: function(data)
                 {
                     $("#results-table").html(data)
                     paging()
                 }
            });
        } else {
            queryId = form.attr('name')
            var tempId = makeId(10)
            var htmlData = '<div class="row" id="' + tempId + '">'
            htmlData += '<div class="loadingio-spinner-spinner-kly0lqmixgq"><div class="ldio-np83wdslazg"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div></div>'
            htmlData += '<p class="mt-2 pt-1">Running query ID: ' + form.attr('name') + '</p></div>'
            $("#queries-running").append(htmlData)
            $.ajax({
                type: "POST",
                url: '/invoke/' + queryId + '/' + tempId,
                data: form.serialize(), // serializes the form's elements.
                success: function(data)
                {
                    addLayer(data['geojson'], data['query_name'])
                    var points = data['results_amount']
                    var query_name = data['query_name']
                    var infoHtml = '<span class="close close2 mt-2 pt-1 mr-2">x</span><p>Query: "' + query_name + '" returned ' + points + ' points.</p>'
                    $("#" + data['token']).html(infoHtml)
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    var error_params = xhr.responseJSON
                    var error_message = error_params['error_message']
                    var error_type = error_params['error_type']
                    var query_name = error_params['query_name']
                    var params = error_params['params']
                    var token = error_params['token']
                    var errorHtml = '<span class="close close2 mt-2 pt-1 mr-2">x</span><p><b>Query: "' + query_name + '" Failed with error:</b> ' + escapeHtml(error_type) + ': ' + error_message + '</p>'
                    $("#" + token).html(errorHtml)
                }
            });
        }
    });
});

$(function() {
    $('form[id="modal-query-form"]').submit(function(e) {
        e.preventDefault();
        query = $("#query-big")[0].innerText
        selectIndex = query.toLowerCase().indexOf('select')
        query = query.substring(selectIndex)
        var form_serialized = "query=" + query
        var tempId = makeId(10)
        var htmlData = '<div class="row" id="' + tempId + '">'
        htmlData += '<div class="loadingio-spinner-spinner-kly0lqmixgq"><div class="ldio-np83wdslazg"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div></div>'
        htmlData += '<p class="mt-2 pt-1">Running custom query</p></div>'
        $("#queries-running").append(htmlData)
        $.ajax({
            type: "POST",
            url: '/run_query/' + tempId,
            data: form_serialized, // serializes the form's elements.
            success: function(data)
            {
                addLayer(data['geojson'], 'Custom Query')
                var points = data['results_amount']
                var infoHtml = '<span class="close close2 mt-2 pt-1 mr-2">x</span><p>Custom query returned ' + points + ' points.</p>'
                $("#" + data['token']).html(infoHtml)
            },
            error: function (xhr, ajaxOptions, thrownError) {
                var error_params = xhr.responseJSON
                var error_message = error_params['error_message']
                var error_type = error_params['error_type']
                var token = error_params['token']
                var errorHtml = '<span class="close close2 mt-2 pt-1 mr-2">x</span><p><b>Custom query failed with error:</b> ' + escapeHtml(error_type) + ': ' + error_message + '</p>'
                $("#" + token).html(errorHtml)
            }
        });
        toggleQueryModal()
    });
});

$(function() {
    $('#queries-running').on("click", '.close2', function(e) {
        row = $(this).parent()
        row.css('display', 'none')
    })
});



$(function() {
    $('#query-form').submit(function(e) {
        e.preventDefault();
        var form = $(this);
        query = $("#query")[0].innerText
        selectIndex = query.toLowerCase().indexOf('select')
        query = query.substring(selectIndex)
        var serialized = form.serialize()
        if (serialized.indexOf('query=&') != -1) {
            serialized = serialized.slice(0, serialized.indexOf('query=&')) + '&query=' + query + serialized.substring(serialized.indexOf('query=&') + 6)
        }
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: serialized, // serializes the form's elements.
            success: function(data)
            {
                if (window.location.pathname.endsWith('query')) { // Only when we are in the edit page
                    window.location.href = "/query/" + data['query_id'];
                }
            }
        });
    });
});

$(function() {
    $('#load-results').on("click", function() {
        pathname = window.location.pathname
        splittedPathname = pathname.split("/")
        queryId = splittedPathname[splittedPathname.length - 1]
        $.ajax({
            type: "GET",
            url: '/get_query_parameters/' + queryId,
            success: function(data) {
                formHTML = getParametersFormHTML(data, queryId)
                formHTML += '<button type="button" class="btn cancel" name="cancel-btn" onclick="closeFormQuery()">Close</button>'
                $("#params-form").html(formHTML)
            }
        })
    });
});

$(function() {
    $('input[name="fav-checkbox"]').on("click", function(e) {
        input = $(this)
        checked = input.is(':checked')
        id = input.attr('id')
        queryId = id.split("-")[1]
        formSerialized = "query_id=" + queryId + "&checkbox=" + checked
        $.ajax({
            type: "POST",
            url: '/favorite',
            data: formSerialized, // serializes the form's elements.
            success: function(data)
            {
                console.log('success')
            }
        });
    })
})

$(function() {
    $('input[name="fav-layer-checkbox"]').on("click", function(e) {
        input = $(this)
        checked = input.is(':checked')
        id = input.attr('id')
        layerId = id.split("-")[1]
        formSerialized = "layer_id=" + layerId + "&checkbox=" + checked
        $.ajax({
            type: "POST",
            url: '/favorite-layer',
            data: formSerialized, // serializes the form's elements.
            success: function(data)
            {
                console.log('success')
            }
        });
    })
})
