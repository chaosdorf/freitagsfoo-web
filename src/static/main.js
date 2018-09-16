"use strict";

// initialize pop-overs
jQuery(function () {
    jQuery('[data-toggle="popover"]').popover({
        trigger: "focus",
        html: true
    });
})
