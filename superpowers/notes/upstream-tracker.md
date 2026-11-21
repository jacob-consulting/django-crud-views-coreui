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
repo prefix are in django-crud-views. Since 2026-11-21 the theme builds on `49d5173a` (#391, #393, #394 adopted) and
django-crud-views-extensions `fd06c91` (0.4.0); the line references in the entries below are historical.

Status: **anticipated** (found by reading the code, not yet hit while building), **confirmed** (the theme needed a
workaround), **filed** (issue number), **fixed** (merged upstream, PR number; the theme workaround is still in place),
**done** (fixed upstream and adopted here).

Severity: **blocker**, **annoyance**, **cosmetic** (same meaning as in the Tabler findings file).

## Close-out (2026-11-20, after the browser pass)

Every entry was re-checked against `../django-crud-views` @ `fa2f0a7b` and `../django-crud-views-extensions` @
`667f27a9` and in the browser (alex, sam, kim; light, dark and auto; 375px). Nothing is filed or done upstream yet.

2026-11-21: U1 and U2 filed together as django-crud-views #391 (theme-registered data-attribute prefix,
`register_data_prefix()` / `{% cv_data_prefix %}`, prefix read by `tabs.js` from `#cv-config`). U8 was considered for
that issue and deliberately left out; revisit when a third theme exists or a registration bug appears.
2026-11-21: U9 and U10 filed together as django-crud-views #393 (keys `breadcrumb:list` / `:item` / `:item-active`;
`aria-sort` and the sort icon from `column.is_ordered`, which also fixes the icon on prefixed tables).
2026-11-21: U5 filed as django-crud-views #394 (six `--cv-*` tokens read as `var(--cv-x, var(--bs-x, fallback))`, never
declared upstream; gutter via `gx-3`; help-button rule stays). U12 follows with the same token names.
2026-11-21: U12 filed as django-crud-views-extensions #6 (same chains, plus `--cv-border-color-translucent` and
`--cv-highlight-bg`; hard fallbacks everywhere); #394 got a comment asking its docs to state the naming rule.

2026-11-21, later the same day: all four issues fixed and closed upstream.

| Issue | Entries | Fixed by | Merge commit | What landed |
|---|---|---|---|---|
| django-crud-views #391 | U1, U2 | PR #395 | `95d40ddf` | `register_data_prefix()`, `{% cv_data_prefix %}`; prefix on actions-menu toggle, language selector, vertical tabs, accordion group; `data-data-prefix` in both config tags, read by `tabs.js` on every init/dispose scan. Default output byte-identical apart from `data-data-prefix="bs"`. |
| django-crud-views #393 | U9, U10 (and C8) | PR #396 | `4ec93cb9` | keys `breadcrumb:list`, `breadcrumb:item`, `breadcrumb:item-active`; header `aria-sort` and sort icon from the bound column's ordering, so default-ordered and prefixed tables show their real sort state. |
| django-crud-views #394 | U5 | PR #397 | `49d5173a` | six `--cv-*` tokens read with Bootstrap and literal fallbacks (twelve uses); compact formset rows use `gx-3`; the help-button `--bs-btn-color` bridge stays. |
| extensions #6 | U12 | PR #7 | `c23739cb` | both typeahead skins read five `--cv-*` tokens as `var(--cv-x, var(--bs-x, <hard>))`; released in 0.4.0 (`fd06c91`). |

Adopted (2026-11-21, PR #3, merged to `main` as `c895d3f`; design
`superpowers/specs/2026-11-21-adopt-upstream-fixes-design.md`): `../django-crud-views` pulled to `49d5173a`.

- U1, U2: `register_data_prefix("coreui")` in `CrudViewsCoreuiConfig.ready()`; the four `data-coreui-` template copies
  and `coreui-tabs.js` are deleted. Guards: every test app page (full and modal partial) renders without `data-bs-`,
  `#cv-config` carries `data-data-prefix="coreui"`, and a scan of upstream's templates and scripts finds no hard-coded
  `data-bs-`.
- U11: E002 checks only `crud_views` (the form frame and table overrides remain); `crud_views_object_detail` may come
  anywhere.
- U9: `breadcrumb:list` = `breadcrumb my-0`; the CSS rule is gone.
- U10, C8: the theme's `table.thead` copy is gone; upstream's header sets `aria-sort` and the icon from the table's
  ordering, prefixed tables included (`test_bulk_prefixed_sort_shows_the_icon` is an ordinary test now).
- U5, U12: the theme sets the `--cv-*` tokens from `--cui-*` (element-scoped); the `--bs-*` re-mapping and the gutter
  rule are gone (upstream uses `gx-3`); the help-button `--cui-btn-color: var(--bs-btn-color)` bridge stays. The
  example requires django-crud-views-extensions >= 0.4.0.
- U3: the overrides it relied on are gone; dropdowns now work through the prefix and CoreUI's data API. Still deferred.
- U4: unchanged; upstream's `adapters.js` did not change, `coreui-adapters.js` stays. Its tooltip placement wrapper could
  derive `data-coreui-placement` from the prefix now in `#cv-config`; worth filing together with a namespace value.

Browser pass after adoption (Acme Roasters, alex, Chrome via Claude in Chrome, 1548px window, 2026-11-21):

| Check | Page | Mode | Result |
| --- | --- | --- | --- |
| `#cv-config` prefix `coreui`, no `data-bs-` in the page; second pill switches tab and pane | `/product/<id>/detail/` (tabs-vertical) | light | pass |
| accordion: second group opens, first closes; no `data-bs-` | `/lot/<id>/detail/` (accordion) | light | pass |
| `⋯` actions menu opens (`aria-expanded="true"`, `.show`) | `/lot/<id>/detail/` | light | pass |
| header breadcrumb `breadcrumb my-0`, computed bottom margin 0 | `/lot/<id>/detail/` | light | pass |
| sorted column: `aria-sort="ascending"` + icon; unsorted columns `none` | `/orders/?sort=number` | light | pass |
| tokens resolve to CoreUI dark values; table headers and `?` buttons `rgba(255,255,255,.87)` | `/orders/manage/` | dark | pass (see note) |
| same, light values (`rgba(37,43,54,.95)`, `--cv-body-bg` `#fff`) | `/orders/manage/` | light | pass |
| typeahead select popup opaque, options readable | `/orders/create/` | dark | pass |
| compact formset: `row gx-3` headings and fields, gutter 1rem, columns aligned to 1px, row card dark | `/customer/<id>/order/create/` | dark | pass |

Note: the first manage-page check showed `#495057` headers on the dark page, because the browser still had the
pre-pull `manage.css` (reading `--bs-*`) cached next to the new theme CSS (setting only `--cv-*`). After a cache reload
it passed. The theme's and upstream's stylesheets must be upgraded together; hashed static file names
(`ManifestStaticFilesStorage`) do that in production. Not checked in the browser: tabs inside a modal (no demo view
opens an object detail in a modal; covered by `test_cv_config_publishes_the_coreui_prefix`), the language selector (the
demo has no i18n; covered by `test_no_data_bs_on_any_testapp_page`), the prefixed bulk list (covered by
`test_bulk_prefixed_sort_*`), 375px.

| Entry | Final status | Handled by (theme side) |
|---|---|---|
| U1 | done (#391, PR #395; adopted 2026-11-21) | `register_data_prefix("coreui")` in `ready()`; no template copies |
| U2 | done (#391, PR #395; adopted 2026-11-21) | nothing; upstream's `tabs.js` reads the prefix (`coreui-tabs.js` deleted) |
| U3 | deferred (superseded by #391, adopted) | nothing; upstream's dropdown templates write `data-coreui-*` through the prefix and CoreUI's data API opens them (row menus keep the fixed popper strategy) |
| U4 | deferred (#391 adopted; adapters.js unchanged, script stays) | `src/crud_views_coreui/static/crud_views_coreui/coreui-adapters.js` |
| U5 | done (#394, PR #397; adopted 2026-11-21) | `src/crud_views_coreui/static/crud_views_coreui/crud_views_coreui.css`, `--cv-*` block (`--cv-secondary-text-emphasis` from `--cui-body-color`) |
| U6 | confirmed | `scripts/vendor_templates.py` / `django_coreui.crispy.vendored.rewrite` (`data-bs-` -> `data-coreui-` in the crispy pack) |
| U7 | confirmed (demo) | semantic icon names: `example/config/icons.py` `ACME_ICONS` -> `CRUD_VIEWS_ICONS` and `COREUI_ICON_ALIASES` (`django_coreui/icons.py`) |
| U8 | anticipated, not hit | nothing to work around; `src/crud_views_coreui/apps.py` is the duplicated `ready()` |
| U9 | done (#393, PR #396; adopted 2026-11-21) | class key `breadcrumb:list` = `breadcrumb my-0` |
| U10 | done (#393, PR #396; adopted 2026-11-21) | nothing; upstream's header |
| U11 | reduced (2026-11-21) | system check `crud_views_coreui.E002`, now `crud_views` only (two layout overrides remain) |
| U12 | done (extensions #6, PR #7, 0.4.0; adopted 2026-11-21) | `crud_views_coreui.css`, `--cv-*` tokens on `.cv-typeahead, .cv-typeahead-select` |

U8 verdict: not worth an issue of its own. Two themes repeat a dozen lines of registration and the duplication hides no
bug. #391 shipped `register_data_prefix()` without a `register_theme()` helper, so the theme's `ready()` now makes six
registrations; revisit when a third theme exists or a registration bug appears.

## Still open (2026-11-21, after PR #3)

Waiting upstream: #398 (U4). Left, none of them blocking:

- **U4**: filed as django-crud-views #398 (2026-11-21): `register_js_namespace()` and
  `register_tooltip_placements()`, both in `#cv-config`; once released `coreui-adapters.js` goes.
- **U3**: deferred until a theme exists whose library is neither Bootstrap nor a data-API fork.
- **U8**: see the verdict above.
- **U11**: E002 stays for the two layout overrides (`snippets/form_frame.html`, `table/bootstrap5.html`); they are
  theme layout, not upstream gaps.
- **C10** (bulk toolbar shows every action to every viewer): filed as django-crud-views #399 (2026-11-21), amending
  #387 D-03: the toolbar offers an action only when its destination passes `cv_has_access` and `cv_action_enabled`
  for the viewer (default, no flag, no per-row check); a source with no action left renders no toolbar and no
  checkboxes. Once released, Kim no longer sees "Cancel orders"; nothing to remove here.
- **C11** (no danger variant for bulk buttons): filed as django-crud-views #400 (2026-11-21), amending 06.41
  D-19 / D-29: a dedicated bulk leaf (`crud_views/tags/button/bulk.html`) with four class keys `bulk:primary` to
  `bulk:danger`, selected by the destination's `cv_action_variant` (stock values unchanged). Once released, add the
  four keys (and `:icon` variants) to `COREUI_BUTTON_CLASSES` and set `cv_action_variant = "danger"` on the demo's
  "Cancel orders".
- Theme-side follow-ups from the PR #3 review (not upstream): the token tests check token names but not that the
  selector list still covers the three formset classes; a `[data-coreui-theme]` element nested inside the manage page
  or a formset card keeps the outer token values; no test pins the icon on a default-ordered list without `?sort=`.

## U1. Hard-coded `data-bs-*` attributes in templates

- Status: fixed (#391 filed and fixed 2026-11-21 by PR #395 @ `95d40ddf`, together with U2; adopted 2026-11-21, overrides deleted) · Severity: annoyance
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
- Theme workaround (2026-11-20): four overrides under `src/crud_views_coreui/templates/`, each the upstream file at
  `fa2f0a7b` with only `data-bs-` replaced by `data-coreui-` and a first-line comment naming the upstream path and
  commit: `crud_views/tags/actions_menu_toggle.html`, `crud_views/snippets/language_selector.html`,
  `crud_views_object_detail/layouts/tabs-vertical/object_detail.html`,
  `crud_views_object_detail/layouts/accordion/group.html`. The drift guard is
  `tests/crud_views_coreui/test_theme.py::DataCoreuiTests::test_data_bs_overrides_track_upstream`: each override must
  equal header + the installed upstream file with the rename, so any upstream edit (or upstream dropping
  `data-bs-`) fails the suite. `test_no_data_bs_on_any_testapp_page` renders every test app URL (both object-detail
  packs included), full page and modal partial, and finds no `data-bs-`.

## U2. Hard-coded `data-bs-toggle` selector in JavaScript

- Status: fixed (#391 filed and fixed 2026-11-21 by PR #395 @ `95d40ddf`, together with U1; adopted 2026-11-21, `coreui-tabs.js` deleted) · Severity: annoyance
- Where: `crud_views_object_detail/static/crud_views_object_detail/js/tabs.js:12`:
  `'[data-bs-toggle="tab"], [data-bs-toggle="pill"], [data-bs-toggle="list"]'`
- Effect: if the theme renames the attributes (U1), tabs.js no longer finds the triggers; if it keeps them, CoreUI's
  data API ignores them. Either way the theme must replace the script or add its own init.
- Possible fix: read the prefix from `cv_config` (the same value as U1), or mark triggers with a crud_views-owned
  attribute (`data-cv-tab`) the way tooltips use `data-cv-tooltip`.
- Theme workaround (2026-11-20): `src/crud_views_coreui/static/crud_views_coreui/coreui-tabs.js`, registered in
  `CrudViewsCoreuiConfig.ready()` after `coreui-adapters.js`, is upstream's init with the selector
  `[data-coreui-toggle="tab"|"pill"|"list"]`: owned tablists (`data-cv-od-tabs`) only, `cv.adapters.tab.init` on load
  and on `cv:modal:loaded`, `dispose` on `cv:modal:unload`. Upstream's `tabs.js` stays loaded and finds nothing.
  `test_upstream_tabs_script_still_selects_data_bs` fails once upstream's selector changes, the signal to drop the
  theme script.
- Public initializer: upstream documents `cv.initObjectDetailTabs(root)` (`docs/reference/javascript.md`,
  "Object-detail tabs"; `docs/reference/assets.md`) as the call for content inserted outside the modal flow and for
  a UI library that loads late. Upstream's function selects `data-bs-toggle`, so under the theme it alone would find
  nothing. `tabs.js` loads after `coreui-tabs.js` (asset order follows `INSTALLED_APPS`: the theme comes before
  crud_views and the object-detail app) and assigns the global unconditionally. So until then `coreui-tabs.js`
  makes `cv.initObjectDetailTabs` a one-shot accessor: `tabs.js`'s assignment is kept as the upstream part, and the
  global becomes a plain writable property holding the theme's wrapper (upstream part, then the `data-coreui` init).
  If `tabs.js` ran first, the plain property is defined directly. From then on it behaves like any global, so a
  project can wrap it the usual way (`const prev = cv.initObjectDetailTabs; cv.initObjectDetailTabs = r => {...}`)
  without recursion. Without `crud_views_object_detail`'s script the wrapper runs the CoreUI part alone. The theme
  keeps upstream's adapter contract (a missing `cv.adapters.tab` is a no-op; an entry without callable
  `init`/`dispose` throws `TypeError`). Pinned by
  `test_coreui_tabs_script_wraps_the_public_initializer` and `test_coreui_tabs_script_keeps_the_adapter_contract`
  (source-level; behaviour is for the browser pass, the project has no JS test suite). Same possible fix: with a
  prefix in `cv_config` or a `data-cv-tab` marker, upstream's initializer would cover the theme and the wrapper goes.

## U3. No `dropdown` adapter

- Status: deferred (confirmed; superseded in practice by #391, adopted 2026-11-21) · Severity: annoyance
- Where: `crud_views/static/crud_views/js/adapters.js:67-127`: `cv.bootstrapAdapters(ns)` builds `modal`,
  `tooltip`, `tab`, `collapse`, `alert`, but no `dropdown`; dropdowns rely on Bootstrap's data API alone.
- Effect: a theme whose library is not `window.bootstrap` cannot initialise crud_views' dropdowns through the adapter
  layer, which otherwise works well for CoreUI (`cv.bootstrapAdapters(() => window.coreui)`).
- Possible fix: add `dropdown.init(el)` and initialise `actions_menu_toggle` triggers through it, like
  `data-cv-tooltip`.
- Theme workaround (2026-11-20): none in JavaScript; the two dropdown templates (`tags/actions_menu_toggle.html`,
  incl. its `data-bs-popper-config`, and `snippets/language_selector.html`) are among the U1 overrides, so CoreUI's
  data API picks them up. With a dropdown adapter and a crud_views-owned trigger attribute both overrides could go.
- Dependency (2026-11-21): superseded in practice by django-crud-views #391 (U1 + U2). With the prefix registered,
  the dropdown templates write `data-coreui-toggle` and CoreUI's own data API opens them, so the U1 overrides that
  served as this workaround go. A dropdown adapter would then only help a library that is neither Bootstrap nor a
  data-API fork; no such theme exists. Deferred until one does.
- Adopted (2026-11-21, PR #3): the U1 overrides are deleted; the `⋯` menu opens through CoreUI's data API (browser
  pass), the language selector is covered by the no-`data-bs-` page test.

## U4. Default adapter namespace is fixed to `globalThis.bootstrap`

- Status: filed (#398, 2026-11-21) · Severity: cosmetic
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
- Dependency (2026-11-21): builds on django-crud-views #391 (U1 + U2), which puts the data-attribute prefix into
  `#cv-config`. With it, `adapters.js` could derive the tooltip placement attribute from the prefix, and a namespace
  value next to it would remove `coreui-adapters.js` entirely. The namespace stays a second value: prefix and
  namespace differ for Bootstrap (`bs` / `bootstrap`) and only coincide for CoreUI. Decide after #391 lands, by how
  much of the theme script is left. Deferred.
- After adoption (2026-11-21, PR #3): `adapters.js` is unchanged at `49d5173a`; all of `coreui-adapters.js` is left
  (the namespace line and the tooltip placement wrapper). Filing would need both values, the namespace and the
  placement attribute from the prefix; not filed yet (see "Still open").
- Filed (2026-11-21): django-crud-views #398, design approved by the maintainer. Two theme registrations carried in
  `#cv-config` and read by `adapters.js` at call time: `register_js_namespace(name)` (default `bootstrap`) and
  `register_tooltip_placements({location: placement})` (default `{}`, so stock Bootstrap is unchanged; an explicit
  `data-{prefix}-placement` on the trigger wins). Chosen over a global "context → bottom" default (would move stock
  tooltips) and namespace-only (the script would stay). Once released the theme calls
  `register_js_namespace("coreui")` and `register_tooltip_placements({"context": "bottom"})` and deletes
  `coreui-adapters.js` with its asset bundle.

## U5. Upstream CSS reads `--bs-*` custom properties

- Status: fixed (#394 filed and fixed 2026-11-21 by PR #397 @ `49d5173a`; adopted 2026-11-21, theme sets `--cv-*`) · Severity: cosmetic
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
- 2026-11-20, browser pass: `--bs-secondary-text-emphasis` is now fed from `--cui-body-color`, not from
  `--cui-secondary-text-emphasis`: CoreUI 5.9.1 keeps that token dark (`#212233`) in dark mode, where Bootstrap's
  turns light, so the manage page's table headers and `?` help buttons were dark on dark. The same browser pass found
  the same gap in django-crud-views-extensions (U12).
- Possible fix: crud_views defines its own tokens (`--cv-secondary-color: var(--bs-secondary-color, #6c757d)`) in
  one place and uses only those; a theme sets the `--cv-*` tokens once. The component variables it sets
  (`--bs-btn-color`, `--bs-gutter-x`) would better be a class key or a `--cv-*` token the theme maps.

## U6. Third party: crispy-bootstrap5 hard-codes `data-bs-*`

- Status: confirmed (2026-11-20: the pack's accordion, tab, modal and alert templates carry the rewritten attributes) ·
  Severity: annoyance · Upstream: crispy-bootstrap5, not django-crud-views
- Where: crispy-bootstrap5 templates for accordion, tabs and collapse (`accordion-group.html`, `layout/tab-link.html`, …)
- Effect: the CoreUI crispy pack vendors crispy-bootstrap5 (as the Tabler pack does) and rewrites `data-bs-` to
  `data-coreui-` in the vendoring script. Nothing to file for django-crud-views; noted so the rewrite rule has a
  reason on record.

## U7. App code names icons by library (`tabler:<name>`)

- Status: confirmed (demo; 2026-11-20: semantic names throughout, see the last bullet) · Severity: annoyance · Partly a
  demo issue, not only upstream
- Where: the Acme Roasters example (47 `tabler:` strings in `example/**/*.py` in the Tabler project)
- Effect: moving the same app to another theme means editing every icon string. The app is meant to be
  theme-agnostic ("the app code never imports the theme"), but its icon names are not.
- Checked 2026-11-20: upstream already supports it. `crud_views/lib/icons.py:138-147` merges `DEFAULT_ICONS`,
  theme `register_icons()` and `CRUD_VIEWS_ICONS` with any key, so an app can use semantic names (`"customer"`) and
  the project maps them to `library:name`. Nothing to file for crud_views; the demo should use semantic names.
- Remaining gap (theme-side, not upstream): template-level icons rendered by the shell tag (`{% icon "…" %}` from
  `django_tabler` / `django_coreui`) cannot use that registry, because the shell package must not depend on
  crud_views. Either the shell tag gets its own alias map, or app templates keep library-native names.
- Resolved here (2026-11-20): the shell tag got its own alias map, `settings.COREUI_ICON_ALIASES`
  (`django_coreui/icons.py`); the demo sets both it and `CRUD_VIEWS_ICONS` from one dict, `ACME_ICONS`
  (`example/config/icons.py`), so app code and templates use semantic names only.

## U8. Theme registration boilerplate

- Status: anticipated, not hit (final verdict 2026-11-20, see below) · Severity: cosmetic
- Where: `../tabler-test/src/crud_views_tabler/apps.py` (`ready()` registers button classes, label-mode defaults,
  icon library, icons, assets)
- Effect: a second theme repeats the same `ready()` shape. To confirm once `crud_views_coreui/apps.py` exists: if
  the two are near-identical, a small upstream "theme" helper (one call taking classes, icons, assets) would make the
  pattern explicit.
- 2026-11-20: `src/crud_views_coreui/apps.py` exists and its `ready()` is the Tabler one with names replaced (icon
  library, icons, label-mode defaults, button classes filtered on `crud_views_workflow`, one asset bundle); `checks.py`
  (W001) is likewise a rename of `check_tabler_icons`. Status left anticipated: it is boilerplate, not a workaround.
- 2026-11-20, after Task 7: compared again with `../tabler-test/src/crud_views_tabler/apps.py` (names normalised):
  the only differences are docstring wording, import order, comments and one more JS file in the asset bundle
  (`coreui-tabs.js`, U2). Two themes, the same five registrations and the same workflow filter. Verdict: the
  duplication is real but costs a dozen lines per theme and hides nothing; status stays **anticipated**, cosmetic.
  Worth filing only together with a theme-facing change (e.g. U1's prefix setting), as a `register_theme()` helper
  that takes classes, icons, label-mode defaults and assets and does the `crud_views_workflow` filtering itself.
- Final verdict (close-out, 2026-11-20): anticipated, not hit. The browser pass found no defect that a registration
  helper would have prevented; every registration took effect (button classes, icons, assets in order, label modes).
  Do not file alone; bundle with U1.
- 2026-11-21: #391 shipped without a registration helper; the theme adds one more registration
  (`register_data_prefix`). Verdict unchanged.

## U9. The breadcrumb has no class key

- Status: fixed (#393 filed and fixed 2026-11-21 by PR #396 @ `4ec93cb9`, together with U10; adopted 2026-11-21, `breadcrumb:list` key) · Severity: cosmetic
- Where: `crud_views/templates/crud_views/tags/breadcrumb.html`: `<ol class="breadcrumb">` is fixed; there is no
  `breadcrumb:*` key in `crud_views/lib/button_classes.py`.
- Effect under CoreUI: the theme puts the breadcrumb where CoreUI's layout has it, the header's second row
  (`django_coreui/layouts/app.html`, block `breadcrumb`; on bar pages too, see `crud_views_coreui/page.html`). There
  the free admin template writes `ol.breadcrumb.my-0`; `.breadcrumb` otherwise keeps a 1rem bottom margin, which
  pushes the row's content up. A `breadcrumb:list` key would let the theme set `breadcrumb my-0` instead.
- Theme workaround: `crud_views_coreui.css`, `.header-breadcrumb .breadcrumb { --cui-breadcrumb-margin-bottom: 0; }`
  (CoreUI's own variable, scoped to the header row). Pinned by
  `test_theme.py::ThemeRenderingTests::test_header_breadcrumb_has_no_bottom_margin`.
- Possible fix: `breadcrumb:nav`, `breadcrumb:list`, `breadcrumb:item` keys (defaults `""`, `breadcrumb`,
  `breadcrumb-item`), as the navbar got with #384.

## U10. The stock table header has no `aria-sort`

- Status: fixed (#393 filed and fixed 2026-11-21 by PR #396 @ `4ec93cb9`, together with U9; adopted 2026-11-21, `table.thead` copy deleted) · Severity: annoyance (accessibility)
- Where: `crud_views/templates/crud_views/table/bootstrap5.html`, block `table.thead`: an orderable `<th>` shows the
  `table-sort-asc`/`-desc` icon (from `request.GET.sort`), but carries no `aria-sort`, so assistive technology does not
  learn which column is sorted or in which direction. The Tabler theme's table override sets it.
- Theme workaround: the theme's `crud_views/table/bootstrap5.html` (which extends upstream's) overrides
  `{% block table.thead %}` with upstream's block at `fa2f0a7b` plus one attribute on the `<th>`:
  `aria-sort="ascending|descending|none"` from `column.is_ordered` / `column.order_by_alias.is_descending`, on
  orderable columns only. A block cannot add an attribute to upstream's `<th>`, so the block is a copy;
  `test_theme.py::ThemeRenderingTests::test_table_head_is_upstream_plus_aria_sort` requires it to equal the installed
  upstream block with only that attribute added (and upstream to have no `aria-sort`), so an upstream change to the
  header fails the suite. `test_sorted_column_is_marked`, `test_every_orderable_header_has_aria_sort` check the output.
- Possible fix: add `aria-sort` to the stock header (and take the sort state from `column.is_ordered` instead of
  `request.GET.sort`, which ignores a table `prefix`); then the theme's `table.thead` block goes.

## U11. Template overrides make the theme's place in `INSTALLED_APPS` load-bearing

- Status: reduced (2026-11-21: with #391 adopted the theme overrides no `crud_views_object_detail` template; E002 checks
  `crud_views` only, for the two layout overrides) · Severity: annoyance
- Where: consequence of U1/U2. The `data-bs` renames are template overrides of `crud_views` and
  `crud_views_object_detail` templates, and Django's app-directories loader takes the first app that has a template.
- Effect: a project that lists `crud_views_object_detail` (or `crud_views`) before `crud_views_coreui` silently gets
  upstream's templates: `data-bs-toggle="pill"` tabs and `data-bs-toggle="collapse"` accordions that CoreUI ignores.
  Nothing fails, the tabs just do not switch. The example had exactly this order (copied from the Tabler demo, whose
  theme did not override object-detail templates); the Task 9 page sweep found it.
- Theme workaround (2026-11-20): system check `crud_views_coreui.E002` (`crud_views_coreui/checks.py`,
  `check_app_order`): an Error when `crud_views_coreui` comes after `crud_views` or after `crud_views_object_detail`
  (when installed), with a hint naming the order. Tests:
  `tests/crud_views_coreui/test_registration.py::AppOrderCheckTests`.
- 2026-11-21 (PR #3): with the prefix adopted the object-detail overrides are gone; E002 checks only `crud_views`, for
  the two layout overrides, and its hint says "before crud_views". The possible fix below happened for the data-bs
  half; the layout half is theme design, so E002 stays.
- Possible fix: with U1's data-attribute prefix (or adapter-driven init), the theme would not need the overrides, and
  the order would stop mattering for them.

## U12. django-crud-views-extensions' typeahead skins read `--bs-*` custom properties

- Status: fixed (django-crud-views-extensions #6 filed and fixed 2026-11-21 by PR #7 @ `c23739cb`, released in 0.4.0; adopted 2026-11-21, theme sets `--cv-*`) · Severity: annoyance · Upstream: django-crud-views-extensions, not django-crud-views
- Where (`../django-crud-views-extensions` @ `667f27a9`):
  `src/crud_views_widget_typeahead/static/crud_views_widget_typeahead/typeahead-select.css` (`--bs-body-bg`,
  `--bs-border-color-translucent`, `--bs-border-radius` on the select popup, `--bs-secondary-color`,
  `--bs-highlight-bg`) and `typeahead.css` (`--bs-highlight-bg`, `--bs-secondary-color`).
- Effect under CoreUI (found in the browser pass, 2026-11-20): the variables are undefined, so the select popup had no
  background and the options lay transparent over the form below it (both colour modes); in dark mode the match
  highlight kept its light `#fff3cd` fallback under light text.
- Theme workaround: `crud_views_coreui.css`, one block on `.cv-typeahead, .cv-typeahead-select` defining the five
  properties from `--cui-*` (as U5 does for crud_views). Pinned by
  `tests/crud_views_coreui/test_registration.py::AssetTests::test_css_maps_every_bs_variable_the_typeahead_reads`,
  which parses the installed skins (skipped without the extensions).
- Possible fix: the same as U5, own `--cv-*` tokens with Bootstrap fallbacks, set once by a theme.

## Bulk selection (2026-11-21, upstream 75a42851)

Bulk selection (django-crud-views #392) needed no new CoreUI entry, no `bulk:*` key and no CSS: the theme uses
upstream's seven defaults (`form-check-input`, `d-flex ... gap-*`, ...), which are CoreUI classes too. Checked by
`tests/crud_views_coreui/test_bulk.py` (toolbar, row and card checkboxes bound to the toolbar form, the select column
inside `.card.cv-coreui-table > .table-container > .table-responsive`, the review page, messages, empty list).
The gaps found in the AdminLTE tracker apply here as they are:

- **C9** (the bare `div.table-container`, no `.table-responsive`): already solved by the theme's table override, which
  puts `.table-responsive` around the table inside the card (`{% block table %}`), so a wide list with the select column
  scrolls inside the card. No CSS rule; `test_bulk_table_inside_coreui_card` pins the structure.
- **C10** (the toolbar shows every action to every viewer) and **C11** (no danger variant for bulk buttons): upstream
  gaps, not worked around; no CoreUI-specific effect.
- **C8** (a sorted column of a prefixed table, e.g. `?c-sort=name` on the bulk list, has no `aria-sort` and no sort icon):
  the `aria-sort` half is U10 here (the table.thead copy reads the ordering from the table, so the prefix works;
  `test_bulk_prefixed_sort_sets_aria_sort`). The icon half is not solved: the copy still tests `request.GET.sort`,
  which a prefixed table never sets, so the prefixed header shows no sort icon until upstream #393 lands
  (`test_bulk_prefixed_sort_shows_the_icon`, a strict xfail). Done 2026-11-21: #393 (PR #396) adopted, the copy is
  gone and the test passes without the xfail.
- **Demo test deviation:** `example/sales/tests/test_bulk.py` is AdminLTE's file with one change, the message selector
  `.adminlte-messages .alert` is `.alert`, since this shell has no host message wrapper.
- Demo and browser pass (Acme Roasters, `/orders/` and `/orders/card/`, Chromium via chrome-devtools, 2026-11-21).
  Indeterminate select-all already takes the brand colour (CoreUI's `.form-check-input:indeterminate` reads
  `--cui-primary`), so no `acme.css` rule, unlike the AdminLTE demo. Results (pass unless noted; "clientWidth" because
  the classic 15px scrollbar makes `scrollWidth` equal `clientWidth`, 360 at a 375px viewport, and no sideways scroll):

  | Check | View | User | Width | Result |
  | --- | --- | --- | --- | --- |
  | checkboxes + select-all visible; none white/grey, some indeterminate sienna `rgb(160, 82, 45)`, all sienna | table 20 rows | alex | 1280 | pass |
  | same, card checkboxes (12) in each card's top-left corner, not over the title, all `form=` the toolbar | cards | alex | 1280 | pass |
  | same states, select column 16px; table scrolls inside `.table-responsive` (505 in 311) | table | alex, kim | 375 | pass |
  | same states | cards | alex, kim | 375 | pass |
  | page scroll: `scrollWidth` 360 = `clientWidth` 360 (innerWidth 375) | table, cards | alex, kim | 375 | pass |
  | page scroll: 1265 = 1265 | table, cards | alex, kim | 1280 | pass |
  | "Mark roasted" on 2 confirmed orders: straight through, "2 orders marked roasted.", both Roasted | table | alex | 1280 | pass |
  | "Cancel orders": review with reason textarea, confirm, "1 order cancelled.", order Cancelled | table | alex | 1280 | pass |
  | "Cancel orders" POST and GET | `/orders/bulk-cancel/` | kim | 1280 | 403 (C10: the button is still shown) |
  | "Mark roasted" review | `/orders/bulk-roast/` | kim | 375 | 200 |

  The card's total sits in `card_actions`, which the stock card wraps in a shaded block inside the body (the
  product card's `card-footer` looked the same), so the order card keeps AdminLTE's rule-and-bold-total markup.
  Card-view submits ("Mark roasted", "Cancel orders" from `/orders/card/`) were not run in the browser pass; the
  checkbox-to-form binding there is covered by `test_bulk_checkboxes_point_at_the_toolbar_form`.

## Theme layout overrides (not upstream gaps)

For the record, so they are not mistaken for missing hooks. Started from the Tabler theme's seven layout overrides;
kept only where stock Bootstrap 5 markup is wrong under CoreUI's layout, which sets the page on `--cui-tertiary-bg`
and its content on cards:

- `crud_views/snippets/form_frame.html`: the form in a card outside a modal. Extends upstream's frame of the same name.
- `crud_views/table/bootstrap5.html`: the table on a card, in `.table-responsive`, pagination in the card footer.
  Extends upstream's table of the same name and overrides three blocks with `{{ block.super }}`, so rows, sorting and
  pagination stay upstream's; two CSS rules drop the inner bottom margins. (Until 2026-11-21 a fourth block,
  `table.thead`, copied upstream's header to add `aria-sort`: U10, now upstream.)
- Dropped (stock is correct CoreUI markup): `modal/shell.html`, `tags/alert.html`, `tags/card.html`,
  `tags/list_filter.html`, `tags/list_filter.inner.html`, `view_card.content.html`. `card:root` is `card mb-4`
  (upstream's spacing), since the stock card grid has no vertical gutter.
