// Object-detail tabs under CoreUI (upstream tracker U2). The theme's tabs-vertical template marks its triggers
// data-coreui-toggle, the only prefix CoreUI's data API reads, so upstream's tabs.js, which selects the Bootstrap
// attribute, finds nothing; it stays loaded and does nothing. This is the same init for the data-coreui triggers:
// owned tablists (data-cv-od-tabs) only, through cv.adapters.tab (coreui-adapters.js points it at window.coreui),
// before the first keypress, without calling show() or taking focus; disposed before modal content is replaced.
//
// Upstream's public initializer, cv.initObjectDetailTabs(root), is the documented hook for content inserted outside
// the modal flow and for a late UI library. The theme wraps it so a call initialises the data-coreui triggers too.
// tabs.js loads after this script (asset registration follows INSTALLED_APPS) and assigns the global
// unconditionally, so until then the global is a one-shot accessor: that first assignment is kept as the upstream
// part and the global becomes a plain property holding the wrapper. Without crud_views_object_detail's script the
// wrapper runs the CoreUI part alone.
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

    // Upstream's contract: a missing adapter map or tab entry is a no-op; a present entry must supply both methods.
    function tabAdapter() {
        const tab = globalThis.cv?.adapters?.tab;
        if (tab == null) return null;
        if (typeof tab.init !== "function" || typeof tab.dispose !== "function") {
            throw new TypeError("cv.adapters.tab must supply init(element) and dispose(element)");
        }
        return tab;
    }

    function withTabAdapter(root, call) {
        const triggers = ownedTriggers(root);
        // Pages without owned tabs must not even look up the adapter.
        if (!triggers.length) {
            return;
        }
        const tab = tabAdapter();
        if (!tab) {
            return;
        }
        triggers.forEach(el => call(tab, el));
    }

    function initCoreuiObjectDetailTabs(root = document) {
        withTabAdapter(root, (tab, el) => tab.init(el));
    }

    const cv = (globalThis.cv = globalThis.cv || {});
    let upstreamInit = null;
    function initObjectDetailTabs(root = document) {
        if (upstreamInit) {
            upstreamInit(root);
        }
        initCoreuiObjectDetailTabs(root);
    }
    // From here on the global is a plain writable property holding the wrapper, so a project can wrap or replace it
    // the usual way (const prev = cv.initObjectDetailTabs; cv.initObjectDetailTabs = r => { prev(r); ... }).
    function publish(fn) {
        upstreamInit = fn;
        Object.defineProperty(cv, "initObjectDetailTabs", {
            configurable: true,
            enumerable: true,
            writable: true,
            value: initObjectDetailTabs,
        });
    }
    if (typeof cv.initObjectDetailTabs === "function") {
        publish(cv.initObjectDetailTabs); // upstream's tabs.js already ran
    } else {
        // tabs.js has not run yet: a one-shot accessor takes its assignment as the upstream part, then turns into
        // the plain property. Re-assigning the wrapper itself before that changes nothing.
        Object.defineProperty(cv, "initObjectDetailTabs", {
            configurable: true,
            enumerable: true,
            get: () => initObjectDetailTabs,
            set: fn => {
                if (fn !== initObjectDetailTabs) {
                    publish(typeof fn === "function" ? fn : null);
                }
            },
        });
    }

    document.addEventListener("DOMContentLoaded", () => initCoreuiObjectDetailTabs(document));
    if (document.readyState !== "loading") {
        initCoreuiObjectDetailTabs(document);
    }
    document.addEventListener("cv:modal:loaded", event => initCoreuiObjectDetailTabs(event.target));
    // Never construct an instance during cleanup: the adapter releases its own handlers.
    document.addEventListener("cv:modal:unload", event => withTabAdapter(event.target, (tab, el) => tab.dispose(el)));
})();
