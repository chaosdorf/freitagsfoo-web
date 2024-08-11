let mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
function mediaQueryUpdated(mq) {
    let theme = mq.matches ? "dark" : "light";
    document.getElementsByTagName("body")[0].setAttribute("data-bs-theme", theme);
}
mediaQuery.addListener(mediaQueryUpdated);
mediaQueryUpdated(mediaQuery);
