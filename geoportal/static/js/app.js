var map = L.map('myMap').setView([32.1525104, 34.8601608], 13);
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
const tiles = L.tileLayer(tileUrl, { attribution });
tiles.addTo(map);

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
var drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

function popUp(f,l){
    var out = [];
    if (f.properties){
        for(key in f.properties){
            out.push(key+": "+f.properties[key]);
        }
        l.bindPopup(out.join("<br />"));
    }
}

function getData() {
    var jsonTest = new L.GeoJSON.AJAX("/test",{onEachFeature:popUp});
    jsonTest.addTo(map)
}

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

function openForm(form) {
    $(function() {
        form.style.display = "block";
    })
}

function closeForm() {
    $(document).ready(function() {
        $("#params-form").html('')
    });
}

$(function() {
    $('button[name = "cancel-btn"]').on("click", function() {
        $(this).html('')
    })
})

$(function() {
    $('button[name = "query-selector"]').on("click", function() {
        console.log($(this))
        button = $(this)
        form = button.next()
        queryId = button.parent().parent().attr('id')
        console.log(queryId)
        $.ajax({
            type: "GET",
            url: '/get_query_parameters/' + queryId,
            success: function(data) {
                formHTML = ''
                for (i = 0; i < data.length; i++) {
                    formHTML += '<label class="form-control-label">' + data[i].parameter_name + '</label>'
                    formHTML += '<input class="form-control form-control-lg" type="text" id="' + data[i].parameter_name + '" name="' + data[i].parameter_name + '">'
                }
                formHTML += '<button class="btn">Query</button>'
                formHTML += '<button type="button" class="btn cancel" name="cancel-btn">Close</button>'
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
        $.ajax({
               type: "POST",
               url: '/revoke/' + form.attr('name'),
               data: form.serialize(), // serializes the form's elements.
               success: function(data)
               {
                   console.log(data); // show response from the php script.
                   L.geoJSON(data).bindPopup(function (layer) {
                        return layer.feature.properties.description;
                    }).addTo(map);
               }
        });
    });
});

