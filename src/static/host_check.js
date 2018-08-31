"use strict";

function doCheck() {
    reset();
    doCheckPi();
}

function reset() {
    jQuery("#recheck-button").prop("disabled", true);
    jQuery(".status").fadeOut();
}

function renderStatus(enabled_alerts, data) {
    let rendered = Handlebars.templates.host_check(data);
    jQuery("#check-status-container").html(rendered);
    for(alert of enabled_alerts) {
        jQuery("#"+alert).fadeIn();
    }
}

function doCheckPi() {
    jQuery.ajax("/host/check/info-beamer").always(function(data, status) {
        if(status !== "success") {
            handleNetworkError(status);
        }
        else if(data["status"] === "ok") {
            renderStatus(["pi-success"], {
                "pi-id": data["data"]["id"],
                "pi-setup-name": data["data"]["setup"]["name"],
                "pi-setup-id": data["data"]["setup"]["id"],
            });
        }
        else if(data["status"] === "error") {
            switch(data["last_step"]) {
                case "info-beamer.com":
                    renderStatus(["pi-error-info-beamer"], {});
                    break;
                case "find-device":
                    renderStatus(["pi-error-device-missing"], {
                        "pi-id": data["data"]["id"],
                    });
                    break;
                case "check-device-online":
                    renderStatus(["pi-error-device-offline"], {
                        "pi-id": data["data"]["id"],
                    });
                    break;
                case "check-device-synced":
                    renderStatus(["pi-error-device-not-synced"], {
                        "pi-id": data["data"]["id"],
                    });
                    break;
                case "setup":
                    renderStatus(["pi-error-device-wrong-setup"], {
                        "pi-id": data["data"]["device"]["id"],
                        "pi-setup-name": data["data"]["actual"]["name"],
                        "pi-setup-id": data["data"]["actual"]["name"],
                        "pi-expected-setup-name": data["data"]["expected"]["name"],
                        "pi-expected-setup-id": data["data"]["expected"]["id"],
                    });
                    break;
            }
        }
        jQuery("#recheck-button").prop("disabled", false);
    })
}

function piChangeSetup() {
    jQuery("#pi-error-device-wrong-setup").fadeOut();
    jQuery.ajax("/host/check/info-beamer", {method: "POST"}).always(function(data, status){
        if(status !== "success") {
            handleNetworkError(status);
        }
        else if(data["status"] === "ok") {
            doCheckPi();
        }
        else if(data["status"] === "error") {
            switch(data["last_step"]) {
                case "info-beamer.com":
                    renderStatus(["pi-error-info-beamer"], {});
                    break;
                case "assign-setup":
                    renderStatus(["pi-error-assign-setup"], {
                      "pi-id": data["data"]["device"]["id"],
                      "pi-setup-name": data["data"]["actual"]["name"],
                      "pi-setup-id": data["data"]["actual"]["name"],
                    });
            }
        }
    });
}

function handleNetworkError(status) {
    renderStatus(["network-error"], {
        "network-error-reason": status
    });
}

window.onload = doCheck;
