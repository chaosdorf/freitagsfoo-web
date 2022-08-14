"use strict";

var checkApp = new Vue({
    el: "#check-status",
    data: {
        checking: true,
        piId: null,
        piSetupName: null,
        piSetupId: null,
        piExpectedSetupName: null,
        piExpectedSetupId: null,
        piErrors: [],
        piWarnings: [],
        networkErrors: []
    },
    methods: {
        handleNetworkError: function (error) {
            this.networkErrors.push(error);
        },
        doCheck: function() {
            this.reset();
            this.doCheckPi();
        },
        doCheckPi: function() {
            fetch("/host/check/info-beamer")
            .then(this.checkPiCallback, this.handleNetworkError);
        },
        checkPiCallback: function(response) {
            if(!response.ok) {
                this.networkErrors.push(response.status);
            } else {
                response.json().then((data) => {
                    if(data["status"] === "ok") {
                        this.piId = data["data"]["id"];
                        this.piSetupName = data["data"]["setup"]["name"];
                        this.piSetupId = data["data"]["setup"]["id"];
                    } else if(data["status"] === "error") {
                        switch(data["last_step"]) {
                            case "info-beamer.com":
                                this.piErrors.push("infoBeamer");
                                break;
                            case "find-device":
                                this.piErrors.push("deviceMissing");
                                this.piId = data["data"]["id"];
                                break;
                            case "setup":
                                this.piErrors.push("deviceWrongSetup");
                                this.piId = data["data"]["device"]["id"];
                                this.piSetupName = data["data"]["actual"]["name"];
                                this.piSetupId = data["data"]["actual"]["id"];
                                this.piExpectedSetupName = data["data"]["expected"]["name"];
                                this.piExpectedSetupId = data["data"]["expected"]["id"];
                                break;
                            case "check-device-online":
                                this.piWarnings.push("deviceOffline");
                                this.piId = data["data"]["id"];
                                this.piSetupName = data["data"]["setup"]["name"];
                                this.piSetupId = data["data"]["setup"]["id"];
                                break;
                            case "check-device-synced":
                                this.piWarnings.push("deviceNotSynced");
                                this.piId = data["data"]["id"];
                                this.piSetupName = data["data"]["setup"]["name"];
                                this.piSetupId = data["data"]["setup"]["id"];
                                break;
                            case "state":
                                this.piWarnings.push("stateUnknown");
                                this.piId = data["data"]["id"];
                                this.piSetupName = data["data"]["setup"]["name"];
                                this.piSetupId = data["data"]["setup"]["id"];
                                break;
                            case "extron":
                                this.piWarnings.push("extronWrongInput");
                                this.piId = data["data"]["id"];
                                this.piSetupName = data["data"]["setup"]["name"];
                                this.piSetupId = data["data"]["setup"]["id"];
                                break;
                        }
                    }
                });
            }
            this.checking = false;
        },
        piChangeSetup: function() {
            this.reset();
            fetch("/host/check/info-beamer", {method: "POST"})
            .then(this.piChangeSetupCallback, this.handleNetworkError);
        },
        piChangeSetupCallback: function(response){
            if(!response.ok) {
                this.networkErrors.push(response.status);
            } else {
                response.json().then((data) => {
                    if(data["status"] === "ok") {
                        this.doCheckPi();
                    }
                    else if(data["status"] === "error") {
                        switch(data["last_step"]) {
                            case "info-beamer.com":
                                this.piErrors.push("infoBeamer");
                                break;
                            case "assign-setup":
                                this.piErrors.push("assignSetup");
                                this.piId = data["data"]["device"]["id"];
                                this.piSetupName = data["data"]["actual"]["name"];
                                this.piSetupId = data["data"]["actual"]["id"];
                        }
                    }
                });
            }
            this.checking = false;
        },
        piResetState: function() {
            this.reset();
            fetch("/host/check/info-beamer", {method: "PATCH"})
            .then(this.piResetStateCallback, this.handleNetworkError);
        },
        piResetStateCallback: function(response) {
            if(!response.ok) {
                this.networkErrors.push(response.status);
            } else {
                response.json().then((data) => {
                    if(data["status"] === "ok") {
                        this.doCheckPi();
                    }
                    else if(data["status"] === "error") {
                        switch(data["last_step"]) {
                            case "info-beamer.com":
                                this.piErrors.push("infoBeamer");
                                break;
                            case "send-command":
                                this.piErrors.push("resetState");
                        }
                    }
                });
            }
            this.checking = false;
        },
        extronSwitchPort: function() {
            this.reset();
            fetch("/host/check/info-beamer", {method: "PUT"})
            .then(this.extronSwitchPortCallback, this.handleNetworkError);
        },
        extronSwitchPortCallback: function(response) {
            if (!response.ok) {
                this.networkErrors.push(response.status);
            } else {
                response.json().then((data) => {
                    if (data["status"] === "ok") {
                        this.doCheckPi();
                    }
                    else if (data["status"] === "error") {
                        switch (data["last_step"]) {
                            case "extron":
                                this.piErrors.push("extron");
                                break;
                        }
                    }
                });
            }
            this.checking = false;
        },
        reset: function() {
            this.checking = true;
            this.piErrors = [];
            this.piWarnings = [];
            this.networkErrors = [];
        }
    }
});

window.onload = checkApp.doCheck;
