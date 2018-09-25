"use strict";
function render(categories, available, reserved, pending) {

    Highcharts.chart('container', {
        "yAxis": {
            "max": 100,
            "title": {
                "text": "Pool Usage"
            },
            "endOnTick": "true",
            "allowDecimals": "false",
            "min": 0
        },
        "series": [
            { "color": "red",    "data": reserved,  "name": "Used" },
            { "color": "yellow", "data": pending,   "name": "Pending" },
            { "color": "green",  "data": available, "name": "Available" },
        ],
        "title": {
            "text": "Available Resources by Pool"
        },
        "chart": {
            "animation": "false",
            "type": "bar"
        },
        "plotOptions": {
            "series": {
                "animation": { "duration": 0 },
                "stacking": "normal"
            }
        },
        "xAxis": {
            "categories": categories
        },
        "legend": {
            "reversed": "true"
        }
    });
}

function ajax_success(json_data) {
    var categories = json_data.map(item => item.name);
    var available = json_data.map(item => item.rsrc_ready);
    var pending = json_data.map(item => item.rsrc_pending);
    var reserved = json_data.map(item => item.rsrc_reserved);
    var resource_max = json_data.map(item => item.resource_max);
    render(categories, available, reserved, pending);
}

function dashboard_view() {
  $.ajax({
      url: 'testpool/api/v1/pool/list',
      type: "GET",
      dataType: 'json',
      success: ajax_success
    });
    setTimeout(dashboard_view, 5000);
}
