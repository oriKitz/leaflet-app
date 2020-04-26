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
            $.ajax({
                 type: "POST",
                 url: '/revoke/' + form.attr('name'),
                 data: form.serialize(), // serializes the form's elements.
                 success: function(data)
                 {
                     addLayer(data)
                 }
            });
        }
    });
});

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
