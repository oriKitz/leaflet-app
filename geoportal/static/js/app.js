var queryRunningInstances = {}

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
    formHTML += '<button class="btn">Query</button>'
    formHTML += '<a class="btn" href="/query/' + queryId +'" target="_blank">Edit</a>'
    return formHTML
}

$(function() {
    $('button[name="query-selector"]').on("click", function() {
        console.log($(this))
        button = $(this)
        form = button.next()
        queryId = button.attr('id')
        console.log(queryId)
        $.ajax({
            type: "GET",
            url: '/get_query_parameters/' + queryId,
            success: function(data) {
                formHTML = getParametersFormHTML(data, queryId)
                formHTML += '<button type="button" class="btn cancel" name="cancel-btn" onclick="closeForm(' + queryId +')">Close</button>'
                console.log(formHTML)
                form.addClass("mt-2")
                form.html(formHTML)
            }
        })
    })
})
;

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
            console.log(form.serialize())
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
        console.log(form_serialized)
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

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

$(function() {
    $('#query-form').submit(function(e) {
        e.preventDefault();
        console.log('here')
        var form = $(this);
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: form.serialize(), // serializes the form's elements.
            success: function(data)
            {
                console.log('success')
                if (window.location.pathname.endsWith('query')) { // Only when we are in the edit page
                    window.location.href = "/query/" + data['query_id'];
                }
            }
        });
    });
});

$(function() {
    $('#load-results').on("click", function() {
        console.log('here')
        pathname = window.location.pathname
        splittedPathname = pathname.split("/")
        queryId = splittedPathname[splittedPathname.length - 1]
        console.log(queryId)
        $.ajax({
            type: "GET",
            url: '/get_query_parameters/' + queryId,
            success: function(data) {
                formHTML = getParametersFormHTML(data, queryId)
                formHTML += '<button type="button" class="btn cancel" name="cancel-btn" onclick="closeFormQuery()">Close</button>'
                console.log(formHTML)
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
        console.log(formSerialized)
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

function toggleFavOn(queryId) {
    $(function() {
        input = $("#mark-" + queryId)
        input[0].checked = true
    })
}

function makeId(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}


function toggleQueryModal() {
    $(function() {
        $("#run-query").modal('toggle')
    })
}
