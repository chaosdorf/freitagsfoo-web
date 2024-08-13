let mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
function mediaQueryUpdated(mq) {
    let theme = mq.matches ? "dark" : "light";
    document.getElementsByTagName("body")[0].setAttribute("data-bs-theme", theme);
}
mediaQuery.addListener(mediaQueryUpdated);
mediaQueryUpdated(mediaQuery);

[...document.querySelectorAll('[data-bs-toggle="tooltip"]')]
    .forEach(el => new bootstrap.Tooltip(el));
[...document.querySelectorAll('[data-bs-toggle="popover"]')]
    .forEach(el => new bootstrap.Popover(el));
