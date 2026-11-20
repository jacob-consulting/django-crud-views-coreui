// CoreUI's bundle exposes its Bootstrap-derived components on window.coreui, not window.bootstrap.
// crud_views calls Bootstrap only through cv.adapters (adapters.js); point them at CoreUI (upstream tracker U4).
// The namespace is resolved on every adapter call, so coreui.bundle.min.js may load deferred.
Object.assign(cv.adapters, cv.bootstrapAdapters(() => globalThis.coreui));
// Toolbar tooltips open below the buttons, so they do not cover the page header; the rest keep CoreUI's default.
// Wrap crud_views' init instead of replacing it, so its tooltip-transition guard stays in place; CoreUI reads
// the placement from the data-coreui-placement attribute. An explicit placement on the button wins.
{
    const init = cv.adapters.tooltip.init;
    cv.adapters.tooltip.init = (el, options = {}) => {
        if (options.location === "context" && !el.hasAttribute("data-coreui-placement")) {
            el.setAttribute("data-coreui-placement", "bottom");
        }
        init(el, options);
    };
}
