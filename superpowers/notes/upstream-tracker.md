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

- Status: confirmed · Severity: annoyance
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

- Status: confirmed · Severity: annoyance
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

- Status: confirmed · Severity: annoyance
- Where: `crud_views/static/crud_views/js/adapters.js:67-127`: `cv.bootstrapAdapters(ns)` builds `modal`,
  `tooltip`, `tab`, `collapse`, `alert`, but no `dropdown`; dropdowns rely on Bootstrap's data API alone.
- Effect: a theme whose library is not `window.bootstrap` cannot initialise crud_views' dropdowns through the adapter
  layer, which otherwise works well for CoreUI (`cv.bootstrapAdapters(() => window.coreui)`).
- Possible fix: add `dropdown.init(el)` and initialise `actions_menu_toggle` triggers through it, like
  `data-cv-tooltip`.
- Theme workaround (2026-11-20): none in JavaScript; the two dropdown templates (`tags/actions_menu_toggle.html`,
  incl. its `data-bs-popper-config`, and `snippets/language_selector.html`) are among the U1 overrides, so CoreUI's
  data API picks them up. With a dropdown adapter and a crud_views-owned trigger attribute both overrides could go.

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
- 2026-11-20, after Task 7: compared again with `../tabler-test/src/crud_views_tabler/apps.py` (names normalised):
  the only differences are docstring wording, import order, comments and one more JS file in the asset bundle
  (`coreui-tabs.js`, U2). Two themes, the same five registrations and the same workflow filter. Verdict: the
  duplication is real but costs a dozen lines per theme and hides nothing; status stays **anticipated**, cosmetic.
  Worth filing only together with a theme-facing change (e.g. U1's prefix setting), as a `register_theme()` helper
  that takes classes, icons, label-mode defaults and assets and does the `crud_views_workflow` filtering itself.

## U9. The breadcrumb has no class key

- Status: confirmed · Severity: cosmetic
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

- Status: confirmed · Severity: annoyance (accessibility)
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

- Status: confirmed · Severity: annoyance
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
- Possible fix: with U1's data-attribute prefix (or adapter-driven init), the theme would not need the overrides, and
  the order would stop mattering for them.

## U12. django-crud-views-extensions' typeahead skins read `--bs-*` custom properties

- Status: confirmed · Severity: annoyance · Upstream: django-crud-views-extensions, not django-crud-views
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

## Theme layout overrides (not upstream gaps)

For the record, so they are not mistaken for missing hooks. Started from the Tabler theme's seven layout overrides;
kept only where stock Bootstrap 5 markup is wrong under CoreUI's layout, which sets the page on `--cui-tertiary-bg`
and its content on cards:

- `crud_views/snippets/form_frame.html`: the form in a card outside a modal. Extends upstream's frame of the same name.
- `crud_views/table/bootstrap5.html`: the table on a card, in `.table-responsive`, pagination in the card footer.
  Extends upstream's table of the same name and overrides three blocks with `{{ block.super }}`, so rows, sorting and
  pagination stay upstream's; two CSS rules drop the inner bottom margins. Its fourth block, `table.thead`, is the
  upstream copy with `aria-sort` (an upstream gap: U10).
- Dropped (stock is correct CoreUI markup): `modal/shell.html`, `tags/alert.html`, `tags/card.html`,
  `tags/list_filter.html`, `tags/list_filter.inner.html`, `view_card.content.html`. `card:root` is `card mb-4`
  (upstream's spacing), since the stock card grid has no vertical gutter.
