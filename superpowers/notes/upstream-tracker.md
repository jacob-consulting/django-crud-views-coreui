# Upstream tracker: what a non-Bootstrap-JS theme needs from django-crud-views

Living list of upstream changes that would make theming django-crud-views cheaper, collected while building the
CoreUI theme (`crud_views_coreui`, `django_coreui`). Its sister file in the Tabler project is
`../tabler-test/dev/crud_views_upstream_findings_roastery.md`; entries already filed there are not repeated, only
referenced.

CoreUI 5 is a Bootstrap 5 fork with the same class names, but its JavaScript namespace is `coreui` (not
`bootstrap`), it only reacts to `data-coreui-*` attributes (never `data-bs-*`) and its CSS custom properties are
`--cui-*` (not `--bs-*`). Any theme built on a Bootstrap fork that renamed those (CoreUI today; others later) hits the
same spots. That is what this file is about.

Rule: every theme template override, theme CSS rule or demo workaround that exists because of an upstream gap gets an
entry here in the same change that adds it.

References are against the sibling checkouts: `../django-crud-views` `main` @ `fa2f0a7b` (2026-11-19, includes
ViewSet Navigation #383 and its navbar class keys #386; re-checked, U1-U6 unchanged from `8cc4c05a`). Paths without a
repo prefix are in django-crud-views.

Status: **anticipated** (found by reading the code, not yet hit while building), **confirmed** (the theme needed a
workaround), **filed** (issue number), **done** (fixed upstream and adopted here).

Severity: **blocker**, **annoyance**, **cosmetic** (same meaning as in the Tabler findings file).

## U1. Hard-coded `data-bs-*` attributes in templates

- Status: anticipated · Severity: annoyance
- Where:
  - `crud_views/templates/crud_views/tags/actions_menu_toggle.html:4-5`: `data-bs-toggle="dropdown"`,
    `data-bs-popper-config` (the `⋯` menu on every list row and toolbar)
  - `crud_views/templates/crud_views/snippets/language_selector.html:6`: `data-bs-toggle="dropdown"`
  - `crud_views_object_detail/templates/crud_views_object_detail/layouts/tabs-vertical/object_detail.html:11-12`:
    `data-bs-toggle="pill"`, `data-bs-target`
  - `crud_views_object_detail/templates/crud_views_object_detail/layouts/accordion/group.html:7,18`:
    `data-bs-toggle="collapse"`, `data-bs-target`, `data-bs-parent`
- Effect under CoreUI: dropdowns, pills and accordion groups do nothing; the theme has to override each template
  just to rename attributes, and the copies drift from upstream.
- Possible fix: one setting or template variable for the data-attribute prefix (e.g. `CRUD_VIEWS_DATA_PREFIX`,
  default `bs`, exposed to templates as `cv_data_prefix`), so the templates write `data-{{ cv_data_prefix }}-toggle`.
  Alternative: let these components initialise through `cv.adapters` (see U3) and drop the data API dependency.

## U2. Hard-coded `data-bs-toggle` selector in JavaScript

- Status: anticipated · Severity: annoyance
- Where: `crud_views_object_detail/static/crud_views_object_detail/js/tabs.js:12`:
  `'[data-bs-toggle="tab"], [data-bs-toggle="pill"], [data-bs-toggle="list"]'`
- Effect: if the theme renames the attributes (U1), tabs.js no longer finds the triggers; if it keeps them, CoreUI's
  data API ignores them. Either way the theme must replace the script or add its own init.
- Possible fix: read the prefix from `cv_config` (the same value as U1), or mark triggers with a crud_views-owned
  attribute (`data-cv-tab`) the way tooltips use `data-cv-tooltip`.

## U3. No `dropdown` adapter

- Status: anticipated · Severity: annoyance
- Where: `crud_views/static/crud_views/js/adapters.js:67-127`: `cv.bootstrapAdapters(ns)` builds `modal`,
  `tooltip`, `tab`, `collapse`, `alert`, but no `dropdown`; dropdowns rely on Bootstrap's data API alone.
- Effect: a theme whose library is not `window.bootstrap` cannot initialise crud_views' dropdowns through the adapter
  layer, which otherwise works well for CoreUI (`cv.bootstrapAdapters(() => window.coreui)`).
- Possible fix: add `dropdown.init(el)` and initialise `actions_menu_toggle` triggers through it, like
  `data-cv-tooltip`.

## U4. Default adapter namespace is fixed to `globalThis.bootstrap`

- Status: confirmed · Severity: cosmetic
- Where: `crud_views/static/crud_views/js/adapters.js:129`
- Effect: works (a theme script runs `cv.adapters = cv.bootstrapAdapters(() => window.coreui)`), but every
  Bootstrap-fork theme writes the same few lines and has to load after `adapters.js` and before first use.
- Theme workaround: `src/crud_views_coreui/static/crud_views_coreui/coreui-adapters.js` (registered as a
  `crud_views_coreui` asset bundle in `CrudViewsCoreuiConfig.ready()`) runs
  `Object.assign(cv.adapters, cv.bootstrapAdapters(() => globalThis.coreui))`, the same line as
  `tabler-adapters.js` with another namespace. Its tooltip placement wrapper also has to name the library's data
  attribute (`data-coreui-placement` here, `data-bs-placement` in Tabler), so a `cv_config` namespace alone would not
  remove the theme script; a placement option on `tooltip.init` would.
- Possible fix: a `cv_config` value (`js_namespace: "coreui"`) that `adapters.js` reads before falling back to
  `bootstrap`.

## U5. Upstream CSS reads `--bs-*` custom properties

- Status: confirmed · Severity: cosmetic
- Where: `crud_views/static/crud_views/css/manage.css`, `crud_views/static/crud_views/css/formset.css`
  (13 `--bs-` references in total: 6 properties read with `var()`, `--bs-secondary-color`,
  `--bs-secondary-text-emphasis`, `--bs-body-bg`, `--bs-border-color`, `--bs-border-radius`, `--bs-tertiary-bg`; and
  2 Bootstrap component variables upstream *sets*, `--bs-btn-color` on the manage help button and `--bs-gutter-x` on
  the compact formset rows, which CoreUI's `.btn`/`.row` never read because they read `--cui-btn-color` and
  `--cui-gutter-x`)
- Effect: under CoreUI the variables are undefined (CoreUI defines `--cui-*`), so the manage page and formsets fall
  back to hard defaults and do not follow dark mode. The Tabler theme already re-maps two of them from `--tblr-*`
  (see the Tabler findings, manage page section); a CoreUI theme re-maps them from `--cui-*`.
- Theme workaround: `src/crud_views_coreui/static/crud_views_coreui/crud_views_coreui.css`: one block on
  `[data-cv-manage]` and the formset row/child elements defines the six read properties from `--cui-*`
  (element-scoped, so a `[data-coreui-theme]` subtree is followed), plus two rules handing the set values on
  (`--cui-btn-color: var(--bs-btn-color)` on the help button, `--cui-gutter-x: var(--bs-gutter-x)` on the compact
  rows). `tests/crud_views_coreui/test_registration.py::test_css_maps_every_bs_variable_upstream_reads` parses the
  upstream files, so a new `--bs-*` reference fails the suite.
- Possible fix: crud_views defines its own tokens (`--cv-secondary-color: var(--bs-secondary-color, #6c757d)`) in
  one place and uses only those; a theme sets the `--cv-*` tokens once. The component variables it sets
  (`--bs-btn-color`, `--bs-gutter-x`) would better be a class key or a `--cv-*` token the theme maps.

## U6. Third party: crispy-bootstrap5 hard-codes `data-bs-*`

- Status: anticipated · Severity: annoyance · Upstream: crispy-bootstrap5, not django-crud-views
- Where: crispy-bootstrap5 templates for accordion, tabs and collapse (`accordion-group.html`, `layout/tab-link.html`, …)
- Effect: the CoreUI crispy pack vendors crispy-bootstrap5 (as the Tabler pack does) and rewrites `data-bs-` to
  `data-coreui-` in the vendoring script. Nothing to file for django-crud-views; noted so the rewrite rule has a
  reason on record.

## U7. App code names icons by library (`tabler:<name>`)

- Status: anticipated · Severity: annoyance · Partly a demo issue, not only upstream
- Where: the Acme Roasters example (47 `tabler:` strings in `example/**/*.py` in the Tabler project)
- Effect: moving the same app to another theme means editing every icon string. The app is meant to be
  theme-agnostic ("the app code never imports the theme"), but its icon names are not.
- Checked 2026-11-20: upstream already supports it. `crud_views/lib/icons.py:138-147` merges `DEFAULT_ICONS`,
  theme `register_icons()` and `CRUD_VIEWS_ICONS` with any key, so an app can use semantic names (`"customer"`) and
  the project maps them to `library:name`. Nothing to file for crud_views; the demo should use semantic names.
- Remaining gap (theme-side, not upstream): template-level icons rendered by the shell tag (`{% icon "…" %}` from
  `django_tabler` / `django_coreui`) cannot use that registry, because the shell package must not depend on
  crud_views. Either the shell tag gets its own alias map, or app templates keep library-native names.

## U8. Theme registration boilerplate

- Status: anticipated · Severity: cosmetic
- Where: `../tabler-test/src/crud_views_tabler/apps.py` (`ready()` registers button classes, label-mode defaults,
  icon library, icons, assets)
- Effect: a second theme repeats the same `ready()` shape. To confirm once `crud_views_coreui/apps.py` exists: if
  the two are near-identical, a small upstream "theme" helper (one call taking classes, icons, assets) would make the
  pattern explicit.
- 2026-11-20: `src/crud_views_coreui/apps.py` exists and its `ready()` is the Tabler one with names replaced (icon
  library, icons, label-mode defaults, button classes filtered on `crud_views_workflow`, one asset bundle); `checks.py`
  (W001) is likewise a rename of `check_tabler_icons`. Status left anticipated: it is boilerplate, not a workaround.
