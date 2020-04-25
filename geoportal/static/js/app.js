function filterQueries() {
    input = document.getElementById("queries_search");
    filter = input.value.toUpperCase();
    div = document.getElementById("right-sidebar");
    rows = div.getElementsByClassName("row");
    for (i = 0; i < rows.length; i++) {
        txtValue = rows[i].textContent || a[i].innerText;
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
        $('form[name="' + queryId + '"]').html('')
    });
}
function closeFormQuery() {
    $(document).ready(function() {
        $("#params-form").html('')
    });
}

function getParametersFormHTML(data) {
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
    return formHTML
}

$(function() {
    $('button[name="query-selector"]').on("click", function() {
        console.log($(this))
        button = $(this)
        form = button.next()
        queryId = button.parent().parent().attr('id')
        console.log(queryId)
        $.ajax({
            type: "GET",
            url: '/get_query_parameters/' + queryId,
            success: function(data) {
                formHTML = getParametersFormHTML(data)
                formHTML += '<button type="button" class="btn cancel" name="cancel-btn" onclick="closeForm(' + queryId +')">Close</button>'
                console.log(formHTML)
                form.html(formHTML)
            }
        })
    })
})
;

$(function() {
    $('form[id="params-form"]').submit(function(e) {
        e.preventDefault();
        console.log('here')

        var form = $(this);
        var url = form.attr('action');
        console.log(form.serialize())
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
                     console.log(data); // show response from the php script.
                     $("#results-table").html(data)
                     paging()
                 }
            });
        } else {
            $.ajax({
                 type: "POST",
                 url: '/revoke/' + form.attr('name'),
                 data: form.serialize(), // serializes the form's elements.
                 success: function(data)
                 {
                     console.log(data); // show response from the php script.
                     L.geoJSON(data,{onEachFeature:popUp}).addTo(map);
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
                   alert('success')
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
                formHTML = getParametersFormHTML(data)
                formHTML += '<button type="button" class="btn cancel" name="cancel-btn" onclick="closeFormQuery()">Close</button>'
                console.log(formHTML)
                $("#params-form").html(formHTML)
            }
        })
    });
});
