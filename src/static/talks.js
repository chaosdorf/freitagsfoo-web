"use strict";

var talksApp = new Vue({
    el: "#talks",
    data: {
        loading: true,
        errors: [],
        talks: [],
        wiki_link: null
    },
    methods: {
        fetchTable: function() {
            this.loading = true;
            this.errors = [];
            jQuery.ajax("/talks/list").always(this.fetchTableCallback);
        },
        fetchTableCallback: function(data, status) {
            if(status !== "success") {
                this.errors.push("network");
            }
            else if(data["status"] === "ok") {
                this.talks = data["data"]["talks"];
                this.wiki_link = data["data"]["wiki_link"];
            }
            else if(data["status"] === "error") {
                switch(data["last_step"]) {
                    case "fetch-json":
                        this.errors.push("fetch");
                        break;
                }
            }
            this.loading = false;
        }
    }
});

window.onload = talksApp.fetchTable;
