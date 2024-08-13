"use strict";

var talksApp = Vue.createApp({
    data() {
        return {
            running: new Set(['fetchState']),
            successes: new Set([]),
            errors: new Set([]),
            state: {
                "info-beamer": {
                    is_background: null,
                    announced_talk: null
                },
                talks: {
                    "hosts": ["FIXME"],
                    date: "1970-01-01",
                    talks: [],
                    current: {
                        index: null,
                        started_at: null,
                    },
                    wiki_link: null
                },
                extron: {
                    available_inputs: [],
                    selected_inputs: {},
                    info_beamer_at_port: null
                }
            }, 
            is_host: document.location.pathname.includes("/host/")
        }
    },
    computed: {
        talkRunningForMinutes: {
            get() {
                let current = Date.now() / 1000;
                return (current - this.state.talks.current.started_at) / 60;
            }
        }
    },
    methods: {
        handleNetworkError: function(error) {
            this.errors.add("network");
        },
        fetchState: function() {
            this.running.add('fetchState');
            this.errors.delete("network");
            this.errors.delete("fetch");
            this.$forceUpdate();
            fetch("/state")
            .then(this.fetchStateCallback, this.handleNetworkError);
        },
        fetchStateCallback: function(response) {
            if(!response.ok) {
                this.errors.add("network");
            } else {
                response.json().then(this.handleState);
            }
            this.running.delete("fetchState");
            this.$forceUpdate();
        },
        handleState: function(data) {
            console.log(data);
            if (data["status"] === "ok") {
                this.state = data["data"];
            }
            else if (data["status"] === "error") {
                switch (data["last_step"]) {
                    case "fetch-json":
                        this.errors.add("fetch");
                        break;
                }
            }
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
            fetch("/host/action/begin_talks/info_beamer", {method: "POST"})
            .then(this.doBeginInfoBeamerCallback, this.handleNetworkError);
        },
        doBeginInfoBeamerCallback: function(response) {
            if(!response.ok) {
                this.errors.add("network");
            } else {
                response.json().then((data) => {
                    if(data["status"] === "ok") {
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
                });
            }
            this.running.delete("beginTalks");
            this.fetchState();
            this.$forceUpdate();
        },
        doEnd: function() {
            this.running.add("endTalks");
            this.errors.delete("network");
            this.doEndInfoBeamer();
        },
        doEndInfoBeamer: function() {
            this.successes.delete("endTalksInfoBeamer");
            this.errors.delete("infoBeamer");
            this.errors.delete("endTalksSendCommand");
            this.$forceUpdate();
            fetch("/host/action/end_talks/info_beamer", {method: "POST"})
            .then(this.doEndInfoBeamerCallback, this.handleNetworkError);
        },
        doEndInfoBeamerCallback: function(response) {
            if(!response.ok) {
                this.errors.add("network");
            } else {
                response.json().then((data) => {
                    if(data["status"] === "ok") {
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
                });
            }
            this.running.delete("endTalks");
            this.fetchState();
            this.$forceUpdate();
        },
        doAnnounceTalk: function(index) {
            this.successes.delete("announceTalk");
            this.errors.delete("infoBeamer");
            this.errors.delete("announceTalkSendCommand");
            this.$forceUpdate();
            if(index == this.state['info-beamer'].announced_talk) {
                index = -1;
            }
            let formData = new FormData();
            formData.append("index", index);
            fetch("/host/action/announce_talk/info_beamer", {
                method: "POST",
                body: formData
            })
            .then(this.doAnnounceTalkCallback, this.handleNetworkError);
        },
        doAnnounceTalkCallback: function(response) {
            if(!response.ok) {
                this.errors.add("network");
            } else {
                response.json().then((data) => {
                    if(data["status"] === "error") {
                        switch(data["last_step"]) {
                            case "info-beamer.com":
                                this.errors.add("infoBeamer");
                                break;
                            case "send-command":
                                this.errors.add("announceTalkSendCommand");
                                break;
                        }
                    }
                });
            }
            this.running.delete("announceTalk");
            this.fetchState();
            this.$forceUpdate();
        },
        doBeginTalk: function(index, input) {
            this.running.add("beginTalks")
            this.successes.delete("beginTalk");
            this.errors.delete("network");
            this.$forceUpdate();
            let formData = new FormData();
            formData.append("talk", index);
            formData.append("input", input);
            fetch("/host/action/begin_talk", {
                method: "POST",
                body: formData
            })
            .then(this.doBeginTalkCallback, this.handleNetworkError);
        },
        doBeginTalkCallback: function(response) {
            if (!response.ok) {
                this.errors.add("network");
            } else {
                response.json().then((data) => {
                    if (data["status"] === "error") {
                        // TODO
                    }
                });
            }
            this.running.delete("beginTalk");
            this.fetchState();
            this.$forceUpdate();
        },
        doEndTalk: function (index) {
            this.running.add("endTalk")
            this.successes.delete("endTalk");
            this.errors.delete("network");
            this.$forceUpdate();
            let formData = new FormData();
            formData.append("talk", index);
            fetch("/host/action/end_talk", {
                method: "POST",
                body: formData
            })
            .then(this.doEndTalkCallback, this.handleNetworkError);
        },
        doEndTalkCallback: function (response) {
            if (!response.ok) {
                this.errors.add("network");
            } else {
                response.json().then((data) => {
                    if (data["status"] === "error") {
                        // TODO
                    }
                });
            }
            this.running.delete("endTalk");
            this.fetchState();
            this.$forceUpdate();
        },
    },
    mounted() {
        this.fetchState();
        this.$sse.create({ url: "/stream", format: "json" })
            .on("message", this.handleState)
            .on("error", this.handleNetworkError)
            .connect();
    }
});

window.onload = function() {
    talksApp.use(VueSSE);
    talksApp.use(window["bootstrap-vue-next"].createBootstrap());
    talksApp.mount("#talks");
}
