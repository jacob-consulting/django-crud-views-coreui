// The layout switch: colour mode (light, dark, auto) and the sidebar state (default, narrow, unfoldable).
//
// Loaded in <head> without defer, so the choice is applied before the page is painted. Like the free CoreUI admin
// template's color-modes.js, it keeps each choice in localStorage under one key per setting ("django-coreui-theme",
// "django-coreui-sidebar"), sets data-coreui-theme on <html> (dark or light; "auto" follows prefers-color-scheme) and
// dispatches "ColorSchemeChange" on <html> for charts. The sidebar state is CoreUI's own sidebar-narrow /
// sidebar-narrow-unfoldable class on #sidebar, set through coreui.Sidebar once it exists.
//
// A project's default layout (django_coreui/includes/layout_defaults.html) arrives as data-coreui-layout-defaults on
// <html>. A choice is stored only when it differs from that default, so changing the default reaches every user who
// has not picked something else.
(function () {
  const COREUI_DEFAULTS = { theme: "auto", sidebar: "default" };
  const VALUES = { theme: ["light", "dark", "auto"], sidebar: ["default", "narrow", "unfoldable"] };
  const STORAGE_KEYS = { theme: "django-coreui-theme", sidebar: "django-coreui-sidebar" };
  const SIDEBAR_CLASSES = { narrow: "sidebar-narrow", unfoldable: "sidebar-narrow-unfoldable" };
  const root = document.documentElement;
  const darkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  function projectDefaults() {
    try {
      return JSON.parse(document.documentElement.dataset.coreuiLayoutDefaults || "{}");
    } catch {
      return {};
    }
  }

  const DEFAULTS = { ...COREUI_DEFAULTS, ...projectDefaults() };

  function stored(key) {
    try {
      const value = localStorage.getItem(STORAGE_KEYS[key]);
      return VALUES[key].includes(value) ? value : null;
    } catch {
      return null; // Storage can be blocked; the default applies.
    }
  }

  function store(key, value) {
    try {
      if (value === DEFAULTS[key]) localStorage.removeItem(STORAGE_KEYS[key]);
      else localStorage.setItem(STORAGE_KEYS[key], value);
    } catch {
      // Storage can be blocked; the choice then lasts for this page only.
    }
  }

  const state = { theme: stored("theme") ?? DEFAULTS.theme, sidebar: stored("sidebar") ?? DEFAULTS.sidebar };

  function applyTheme() {
    const mode = state.theme === "auto" ? (darkScheme.matches ? "dark" : "light") : state.theme;
    root.setAttribute("data-coreui-theme", mode);
    root.dispatchEvent(new Event("ColorSchemeChange"));
  }

  function applySidebar() {
    if (state.sidebar === COREUI_DEFAULTS.sidebar) root.removeAttribute("data-coreui-sidebar");
    else root.setAttribute("data-coreui-sidebar", state.sidebar);
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;
    const instance = window.coreui?.Sidebar?.getInstance(sidebar);
    if (instance) {
      // Through CoreUI's API, so its own narrow/unfoldable flags stay right (it leaves phones alone).
      instance.reset();
      if (state.sidebar === "narrow") instance.narrow();
      if (state.sidebar === "unfoldable") instance.unfoldable();
    } else {
      // Before CoreUI creates the instance (on window load), which reads the classes back.
      for (const [value, name] of Object.entries(SIDEBAR_CLASSES)) {
        sidebar.classList.toggle(name, state.sidebar === value);
      }
    }
  }

  function sidebarStateOf(sidebar) {
    if (sidebar.classList.contains(SIDEBAR_CLASSES.unfoldable)) return "unfoldable";
    if (sidebar.classList.contains(SIDEBAR_CLASSES.narrow)) return "narrow";
    return "default";
  }

  function settingsOf(button) {
    return JSON.parse(button.dataset.layoutSettings);
  }

  function refresh() {
    for (const button of document.querySelectorAll("[data-layout-settings]")) {
      const active = Object.entries(settingsOf(button)).every(([key, value]) => state[key] === value);
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active);
    }
  }

  function choose(key, value) {
    if (!VALUES[key]?.includes(value)) return;
    state[key] = value;
    store(key, value);
    if (key === "theme") applyTheme();
    else applySidebar();
  }

  applyTheme();
  applySidebar();
  // The sidebar is parsed after this script: set its state as soon as it exists, before the first paint.
  if (!document.getElementById("sidebar")) {
    const observer = new MutationObserver(() => {
      if (document.getElementById("sidebar")) {
        observer.disconnect();
        applySidebar();
      }
    });
    observer.observe(root, { childList: true, subtree: true });
    document.addEventListener("DOMContentLoaded", () => observer.disconnect());
  }

  darkScheme.addEventListener("change", () => {
    if (state.theme === "auto") applyTheme();
  });

  document.addEventListener("click", (event) => {
    // The header's sidebar toggler (data-sidebar-toggle="#sidebar"): shows or hides the sidebar. A delegated handler
    // instead of the free template's inline onclick, so the shell needs no 'unsafe-inline' in a CSP.
    const sidebarToggle = event.target.closest("[data-sidebar-toggle]");
    if (sidebarToggle) {
      const target = document.querySelector(sidebarToggle.dataset.sidebarToggle);
      if (target && window.coreui) coreui.Sidebar.getOrCreateInstance(target).toggle();
      return;
    }
    const button = event.target.closest("[data-layout-settings]");
    if (button) {
      for (const [key, value] of Object.entries(settingsOf(button))) choose(key, value);
      refresh();
      // Charts size themselves from the window; the content area may just have changed width.
      window.dispatchEvent(new Event("resize"));
      return;
    }
    // The sidebar footer's own toggler: CoreUI has already toggled the class (its handler sits on #sidebar).
    const toggler = event.target.closest('#sidebar [data-coreui-toggle="unfoldable"], #sidebar [data-coreui-toggle="narrow"]');
    if (toggler) {
      choose("sidebar", sidebarStateOf(toggler.closest("#sidebar")));
      refresh();
      window.dispatchEvent(new Event("resize"));
    }
  });

  document.addEventListener("DOMContentLoaded", refresh);
})();
