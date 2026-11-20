// Object-detail tabs under CoreUI (upstream tracker U2). The theme's tabs-vertical template marks its triggers
// data-coreui-toggle, the only prefix CoreUI's data API reads, so upstream's tabs.js, which selects the Bootstrap
// attribute, finds nothing; it stays loaded and does nothing. This is the same init for the data-coreui triggers:
// owned tablists (data-cv-od-tabs) only, through cv.adapters.tab (coreui-adapters.js points it at window.coreui),
// before the first keypress, without calling show() or taking focus; disposed before modal content is replaced.
(function () {
    if (globalThis.__cvCoreuiObjectDetailTabsInit) {
        return;
    }
    globalThis.__cvCoreuiObjectDetailTabsInit = true;

    const ownedList = "[data-cv-od-tabs]";
    const tablist = '[data-cv-od-tabs], [role="tablist"], .nav, .list-group';
    const trigger = '[data-coreui-toggle="tab"], [data-coreui-toggle="pill"], [data-coreui-toggle="list"]';

    function ownedTriggers(root) {
        const lists = [...root.querySelectorAll(ownedList)];
        if (root.matches?.(ownedList)) {
            lists.unshift(root);
        }
        return lists.flatMap(list => [...list.querySelectorAll(trigger)].filter(el => el.closest(tablist) === list));
    }

    function withTabAdapter(root, call) {
        const triggers = ownedTriggers(root);
        // Pages without owned tabs must not even look up the adapter.
        if (!triggers.length) {
            return;
        }
        const tab = globalThis.cv?.adapters?.tab;
        if (tab == null) {
            return;
        }
        triggers.forEach(el => call(tab, el));
    }

    document.addEventListener("DOMContentLoaded", () => withTabAdapter(document, (tab, el) => tab.init(el)));
    if (document.readyState !== "loading") {
        withTabAdapter(document, (tab, el) => tab.init(el));
    }
    document.addEventListener("cv:modal:loaded", event => withTabAdapter(event.target, (tab, el) => tab.init(el)));
    // Never construct an instance during cleanup: the adapter releases its own handlers.
    document.addEventListener("cv:modal:unload", event => withTabAdapter(event.target, (tab, el) => tab.dispose(el)));
})();
