"use strict";

var talksApp = new Vue({
    el: "#talks",
    data: {
        running: new Set(['fetchTalks', 'fetchState']),
        successes: new Set([]),
        state: null,
        errors: new Set([]),
        talks: [],
        wiki_link: null
    },
    methods: {
        fetch: function() {
            this.running.add('fetchTalks');
            this.running.add('fetchState');
            this.errors.delete("network");
            this.errors.delete("fetch");
            this.$forceUpdate();
            jQuery.ajax("/talks/list").always(this.fetchTableCallback);
            jQuery.ajax("/host/action/info_beamer/state").always(this.fetchStateCallback);
        },
        fetchTableCallback: function(data, status) {
            if(status !== "success") {
                this.errors.add("network");
            }
            else if(data["status"] === "ok") {
                this.talks = data["data"]["talks"];
                this.wiki_link = data["data"]["wiki_link"];
            }
            else if(data["status"] === "error") {
                switch(data["last_step"]) {
                    case "fetch-json":
                        this.errors.add("fetch");
                        break;
                }
            }
            this.running.delete("fetchTalks");
            this.$forceUpdate();
        },
        fetchStateCallback: function(data, status) {
            if(status !== "success") {
                this.errors.add("network");
            }
            else if(data["status"] === "ok") {
                this.state = data["data"];
            }
            else if(data["status"] === "error") {
                switch(data["last_step"]) {
                    case "fetch-json":
                        this.errors.add("fetch");
                        break;
                }
            }
            this.running.delete("fetchState");
            this.$forceUpdate();
        },
        doBegin: function() {
            this.running.add("beginTalks")
            this.errors.delete("network");
            this.doBeginInfoBeamer();
        },
        doBeginInfoBeamer: function() {
            this.successes.delete("beginTalksInfoBeamer");
            this.errors.delete("infoBeamer");
            this.errors.delete("beginTalksSendCommand");
            this.$forceUpdate();
            jQuery.ajax("/host/action/begin_talks/info_beamer", {method: "POST"})
            .always(this.doBeginInfoBeamerCallback);
        },
        doBeginInfoBeamerCallback: function(data, status){
            if(status !== "success") {
                this.errors.add("network");
            }
            else if(data["status"] === "ok") {
                this.successes.add("beginTalksInfoBeamer");
            }
            else if(data["status"] === "error") {
                switch(data["last_step"]) {
                    case "info-beamer.com":
                        this.errors.add("infoBeamer");
                        break;
                    case "send-command":
                        this.errors.add("beginTalksSendCommand");
                        break;
                }
            }
            this.running.delete("beginTalks");
            this.$forceUpdate();
        },
        doEnd: function() {
            this.running.add("endTalks")
            this.errors.delete("network");
            this.doEndInfoBeamer();
        },
        doEndInfoBeamer: function() {
            this.successes.delete("endTalksInfoBeamer");
            this.errors.delete("infoBeamer");
            this.errors.delete("endTalksSendCommand");
            this.$forceUpdate();
            jQuery.ajax("/host/action/end_talks/info_beamer", {method: "POST"})
            .always(this.doEndInfoBeamerCallback);
        },
        doEndInfoBeamerCallback: function(data, status){
            if(status !== "success") {
                this.errors.add("network");
            }
            else if(data["status"] === "ok") {
                this.successes.add("endTalksInfoBeamer");
            }
            else if(data["status"] === "error") {
                switch(data["last_step"]) {
                    case "info-beamer.com":
                        this.errors.add("infoBeamer");
                        break;
                    case "send-command":
                        this.errors.add("endTalksSendCommand");
                        break;
                }
            }
            this.running.delete("endTalks");
            this.$forceUpdate();
        }
    }
});

window.onload = talksApp.fetch;
