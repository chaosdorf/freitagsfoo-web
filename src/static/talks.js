"use strict";

function fetchTable() {
    jQuery("#talks-table").fadeOut();
    jQuery.ajax("/talks/list").always(function(data, status) {
        if(status !== "success") {
            // TODO
            // handleNetworkError(status);
        }
        else if(data["status"] === "ok") {
            renderTable(data["data"]);
        }
        else if(data["status"] === "error") {
            switch(data["last_step"]) {
                case "fetch-json":
                    // TODO
                    break;
            }
        }
    });
}

function renderTable(talks) {
    let rendered = Handlebars.templates.talks({
        "talks": talks
    });
    jQuery("#talks-container").html(rendered);
    jQuery("#talks-table").fadeIn();
}

window.onload = fetchTable;
