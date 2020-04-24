var map = L.map('myMap').setView([32.1525104, 34.8601608], 13);
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
const tiles = L.tileLayer(tileUrl, { attribution });
tiles.addTo(map);

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
var drawControl = new L.Control.Draw({
    draw: {
        circle: false
    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

map.on('draw:created', function (e) {
    console.log(1)
    var layers = e.layers;
//    layers.eachLayer(function (layer) {
//         //do whatever you want; most likely save back to db
//    });
    });

// This 2 lines disable somehow my queries shit:
//var toolbar = L.Toolbar();
//toolbar.addToolbar(map);

function popUp(f,l){
    var out = [];
    if (f.properties){
        for(key in f.properties){
//            out.push(key+": "+f.properties[key]);
            out.push(f.properties[key]);
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

function closeForm(queryId) {
    $(document).ready(function() {
        $('form[name="' + queryId + '"]').html('')
    });
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
    });
});

