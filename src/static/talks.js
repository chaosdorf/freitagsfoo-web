"use strict";

function fetchTable() {
    jQuery("#talks-table").fadeOut();
    jQuery(".talks-status").fadeOut();
    jQuery("#refresh-button").prop("disabled", true);
    jQuery.ajax("/talks/list").always(function(data, status) {
        if(status !== "success") {
            handleNetworkError(status);
        }
        else if(data["status"] === "ok") {
            renderTable(data["data"]);
        }
        else if(data["status"] === "error") {
            switch(data["last_step"]) {
                case "fetch-json":
                    jQuery("#error-fetch").fadeIn();
                    break;
            }
        }
        jQuery("#refresh-button").prop("disabled", false);
    });
}

function renderTable(data) {
    let rendered = Handlebars.templates.talks(data);
    jQuery("#talks-container").html(rendered);
    jQuery("#talks-table").fadeIn();
}

function handleNetworkError(status) {
    jQuery("#network-error").fadeIn();
}

window.onload = fetchTable;
