"use strict";

function doBegin() {
    jQuery(".action-status").fadeOut();
    jQuery("#begin-talks-button").prop("disabled", true);
    jQuery.ajax("/host/action/begin_talks", {method: "POST"}).always(function(data, status){
        if(status !== "success") {
            handleNetworkError(status);
        }
        else if(data["status"] === "ok") {
            jQuery("#begin-talks-success").fadeIn();
        }
        else if(data["status"] === "error") {
            switch(data["last_step"]) {
                case "info-beamer.com":
                    jQuery("#error-info-beamer").fadeIn();
                    break;
                case "send-command":
                    jQuery("#begin-talks-error-send-command").fadeIn();
                    break;
            }
        }
        jQuery("#begin-talks-button").prop("disabled", false);
    });
}

function doEnd() {
    jQuery(".action-status").fadeOut();
    jQuery("#end-talks-button").prop("disabled", true);
    jQuery.ajax("/host/action/end_talks", {method: "POST"}).always(function(data, status){
        if(status !== "success") {
            handleNetworkError(status);
        }
        else if(data["status"] === "ok") {
            jQuery("#end-talks-success").fadeIn();
        }
        else if(data["status"] === "error") {
            switch(data["last_step"]) {
                case "info-beamer.com":
                    jQuery("#error-info-beamer").fadeIn();
                    break;
                case "send-command":
                    jQuery("#end-talks-error-send-command").fadeIn();
                    break;
            }
        }
        jQuery("#end-talks-button").prop("disabled", false);
    });
}

function handleNetworkError(status) {
    jQuery("#network-error").fadeIn();
}
