# Theme internals

How `crud_views_coreui` themes django-crud-views: what it overrides, which upstream hooks it uses, and where it stops.
It is exercised by the Acme Roasters demo (`example/`), which puts nested ViewSets, formsets, conditional groups,
workflow, polymorphic models, object detail packs, Guardian, resources, card views and the django-crud-views-extensions
widgets through it, and by its own test app under `tests/crud_views_coreui/`. Everything the theme needed beyond
upstream hooks is an entry in the
[upstream tracker](https://github.com/jacob-consulting/django-crud-views-coreui/blob/main/superpowers/notes/upstream-tracker.md)
(U1-U11), referenced below.

## CoreUI in one paragraph

CoreUI 5 is a Bootstrap 5 fork with the same class names, but three things are renamed. Its JavaScript components live
on `window.coreui` (not `window.bootstrap`); its data API reacts only to `data-coreui-*` attributes (`data-coreui-toggle`,
`data-coreui-target`, ... and never `data-bs-*`); and its CSS custom properties are `--cui-*` (not `--bs-*`). Any code
that is written against Bootstrap's names (django-crud-views' templates, script selectors and stylesheets) hits those
three spots, and they are all this theme has to bridge.

## Approach

django-crud-views has no theme setting. The route its own hints describe is the one the theme follows:

- a theme **app** ships templates under the `crud_views/` namespace,
- it is listed **before** `crud_views` (and `crud_views_object_detail`) in `INSTALLED_APPS`, so Django's app template
  loader finds its files first (check `crud_views_coreui.E002` enforces the order, tracker U11),
- anything it does not override falls through to the stock Bootstrap 5 templates, whose markup is CoreUI markup.

So the theme is a few template overrides, a little Python (the icon library, the button class table, system checks) and
three static files (a stylesheet and two scripts). No crud_views code is patched or subclassed.

```python
INSTALLED_APPS = [
    ...,
    "crispy_forms",
    "django_tables2",
    "django_filters",
    "django_coreui",  # also provides the crispy_coreui template pack
    "crud_views_coreui",  # before crud_views and crud_views_object_detail
    "crud_views.apps.CrudViewsConfig",
    "crud_views_object_detail",
]
CRISPY_TEMPLATE_PACK = "crispy_coreui"
CRISPY_ALLOWED_TEMPLATE_PACKS = ("crispy_coreui",)
CRUD_VIEWS_EXTENDS = "crud_views_coreui/page.html"
DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"
COREUI = {"edition": "free"}
```

`CrudViewsCoreuiConfig.ready()` registers five things through upstream's hooks: the `coreui` icon library, the icon table
(`register_icons`), label-mode defaults (`{"form": "both"}`), the button class table (`register_button_classes`; the
`workflow:*` keys only when `crud_views_workflow` is installed) and the asset bundle (`register_assets`:
`coreui-adapters.js`, `coreui-tabs.js`, `crud_views_coreui.css`).

## The page: CRUD_VIEWS_EXTENDS

`crud_views_coreui/page.html` extends `django_coreui/layouts/app.html` and maps the crud_views pieces onto CoreUI's page:

| crud_views | CoreUI page |
|---|---|
| `{% cv_breadcrumb %}` | the header's second row (block `breadcrumb`), on every page |
| `cv_navbar.icon` + `cv_navbar.label`, `{% cv_navbar_items %}` (block `cv_navbar`) | the owner header at the top of the page header (block `page_header_top`): avatar, `h1`, tabs |
| `{% cv_header_icon %}` + `{% cv_header %}` (via `{% cv_heading %}`) | the page title (block `page_heading` / `page_title`) |
| `{% cv_paragraph %}` | the subtitle |
| `{% cv_context_actions object %}` | the page header's action area (block `actions`) |
| `{% cv_messages %}` | block `messages` |
| `cv_filter`, `cv_content`, `{% cv_config %}` | block `content` |
| `{% cv_css %}` / `{% cv_js %}` | blocks `extra_head` / `extra_js` |

The page title is rendered through `{% cv_heading %}`, so `CRUD_VIEWS_HEADER_LEVEL` applies while the title keeps
CoreUI's `h3` size.

With ViewSet Navigation (upstream PR #383), the owner header shows an avatar with the owner ViewSet's icon, the owner's
name as `h1` and the section links as underline tabs (`nav nav-underline-border`, set through the `navbar:*` class keys,
#384). The view's own title row follows the tabs. A view heading whose text equals the active tab's label is left out
(template tag `cv_coreui_heading_repeats_tab`); the subline and buttons stay. The breadcrumb stays in the header row on
bar pages too, so it appears once. The `cv_navbar` block holds only the tabs: emptying it drops the tabs and keeps the
owner row.

## Header and actions: no button template overrides

The theme overrides no button template. Every action button, the row and toolbar containers, the `⋯` menu toggle, the
filter toggle and the card-order bar render through crud_views' stock templates. The CoreUI look comes from the class
table: `crud_views_coreui/buttons.py` holds `COREUI_BUTTON_CLASSES`, registered with `register_button_classes()`, so
projects need no button settings. A project overrides single keys with `CRUD_VIEWS_BUTTON_CLASSES` (project settings
win).

How Tabler classes translate to CoreUI (the key set is the same):

| Tabler | CoreUI |
|---|---|
| plain `btn` (a bordered button) | `btn btn-outline-secondary` (CoreUI's plain `.btn` is transparent) |
| `btn-ghost-*` | `btn-ghost-*` (the same classes exist) |
| `btn-icon` | the theme's `cv-coreui-icon-btn`, on every `:icon` key, the menu toggles and the formset and card-order controls |
| `bg-<colour>-lt` badges | `bg-<colour>-subtle text-<colour>-emphasis` |
| `btn-list` | `d-flex flex-wrap gap-2` |
| `nav-bordered` | `nav nav-underline-border` |
| `table-vcenter` | `align-middle` |
| `azure`, `green`, `red`, `yellow` | `info`, `success`, `danger`, `warning` |
| `blue`, `pink` (manage page legend) | `cv-coreui-badge-blue`, `cv-coreui-badge-pink`: subtle badges built in the theme CSS from `--cui-blue` and `--cui-pink`, which CoreUI defines but gives no utility classes |

The label mode decides the square shape: each action key exists as `location:variant` (labelled) and
`location:variant:icon` (icon-only, with `cv-coreui-icon-btn`). The manage page's badges never use `primary`, because
its legend names colours and a project's primary may be any colour.

## Overridden templates

The page and six templates:

```
crud_views_coreui/
  page.html                                          CRUD_VIEWS_EXTENDS target (above)
crud_views/
  snippets/form_frame.html        layout: the form in a card (bare in a modal); extends upstream's frame
  table/bootstrap5.html           layout: the table on a card, in .table-responsive, pagination in the card footer;
                                  extends upstream's table, three blocks with {{ block.super }}; plus table.thead (below)
  tags/actions_menu_toggle.html   data-bs- renamed to data-coreui- (U1)
  snippets/language_selector.html data-bs- renamed to data-coreui- (U1)
crud_views_object_detail/layouts/
  tabs-vertical/object_detail.html  data-bs- renamed to data-coreui- (U1)
  accordion/group.html              data-bs- renamed to data-coreui- (U1)
```

CoreUI's layout puts the page on `--cui-tertiary-bg` (gray) and its content on cards. Stock Bootstrap 5 markup is
CoreUI markup, so a layout override is kept only where stock content would sit bare on the gray page: the form frame and
the table. The Tabler theme's other layout overrides (modal shell, alert, card, filter, card view) were dropped, because
the stock markup is right. `card:root` is `card mb-4`, since the stock card grid has no vertical gutter.

### The four `data-bs` overrides (U1, U11)

django-crud-views hard-codes `data-bs-toggle`, `data-bs-target`, `data-bs-parent` and `data-bs-popper-config` in four
templates: the `⋯` actions menu, the language selector, the vertical-tabs object detail and the accordion group.
CoreUI's data API ignores `data-bs-*`, so under CoreUI dropdowns, pills and accordion groups would do nothing. The theme
overrides exactly those four files. Each is the upstream file at `fa2f0a7b` with only `data-bs-` replaced by
`data-coreui-`, plus a first-line comment naming the upstream path and commit. Because they are copies, a test compares
each with the installed upstream file (with the rename applied): any upstream edit fails the suite. Another test renders
every test app page, full and as a modal partial, and finds no `data-bs-` anywhere.

Because these are overrides of `crud_views` and `crud_views_object_detail` templates, the theme's position in
`INSTALLED_APPS` is load-bearing; a project that lists either app first silently gets upstream's `data-bs-*` markup. The
system check `crud_views_coreui.E002` reports exactly that.

### The table header override (U10)

The stock table header marks the sorted column with an icon but has no `aria-sort`, so assistive technology does not
learn which column is sorted. A block cannot add an attribute to upstream's `<th>`, so the theme's table template
overrides `{% block table.thead %}` with a copy of upstream's block plus one attribute on orderable columns:
`aria-sort="ascending|descending|none"`, taken from `column.is_ordered` and `column.order_by_alias.is_descending` (which
also works for tables with a `prefix`). A test requires the block to equal the installed upstream one with only that
attribute added, so an upstream change fails the suite.

## JavaScript

### The adapter (U4)

Core scripts of django-crud-views call Bootstrap components only through `cv.adapters` (`modal`, `tooltip`, `tab`,
`collapse`, `alert`). CoreUI's bundle exposes the same components on `window.coreui`, so the theme registers one asset,
`crud_views_coreui/coreui-adapters.js`:

```js
Object.assign(cv.adapters, cv.bootstrapAdapters(() => globalThis.coreui));
```

A second statement places toolbar tooltips below the buttons, so they do not cover the page header. It **wraps**
crud_views' `cv.adapters.tooltip.init` instead of replacing it: that `init` guards tooltip transitions that outlive
`dispose()`, and the tooltip object also carries the optional `hide` and `dispose`. The placement travels as
`data-coreui-placement`; a button that already has one keeps it. Do not reassign `cv.adapters.tooltip` as a whole.

The namespace is resolved on every call, so CoreUI's bundle may load deferred.

### Object-detail tabs (U2)

django-crud-views' `crud_views_object_detail/js/tabs.js` selects `[data-bs-toggle="tab"]`, `"pill"` and `"list"`. With the
four overrides above the triggers say `data-coreui-toggle`, so upstream's script finds nothing. `coreui-tabs.js`
(registered after `coreui-adapters.js`) is upstream's initialisation with the selector
`[data-coreui-toggle="tab"|"pill"|"list"]`: it handles owned tablists (`data-cv-od-tabs`) only, initialises them through
`cv.adapters.tab.init` on load and on `cv:modal:loaded`, and disposes them on `cv:modal:unload`. Upstream's `tabs.js`
stays loaded and finds nothing. It also keeps upstream's public `cv.initObjectDetailTabs(root)` working: that global
becomes a writable property holding the theme's wrapper (upstream part, then the CoreUI init), so projects can wrap it
the usual way. A test fails once upstream's selector changes, the signal to drop the theme script.

### Dropdowns (U3)

There is no dropdown adapter upstream; dropdowns rely on the data API alone. The theme needs no JavaScript for that: the
two dropdown templates are among the four overrides, so CoreUI's own data API handles them.

### The shell

`django_coreui` ships `layout-switch.js` (colour mode and sidebar state, see [Layouts](layouts.md)); it never touches
`cv`. CoreUI's bundle (`window.coreui`) loads synchronously at the end of `<body>`, as in CoreUI's own admin template.

## CSS tokens (U5)

django-crud-views' `manage.css` and `formset.css` read Bootstrap's `--bs-*` custom properties, which CoreUI does not
define, so the manage page and formsets would use hard fallbacks and ignore dark mode. `crud_views_coreui.css` defines
the six properties upstream reads (`--bs-secondary-color`, `--bs-secondary-text-emphasis`, `--bs-body-bg`,
`--bs-border-color`, `--bs-border-radius`, `--bs-tertiary-bg`) from the matching `--cui-*` ones, on the elements those
rules style (so a `[data-coreui-theme]` subtree is followed). Two properties upstream *sets* for Bootstrap components
(`--bs-btn-color` on the manage help button, `--bs-gutter-x` on compact formset rows) are handed to CoreUI's names
(`--cui-btn-color`, `--cui-gutter-x`). A test parses upstream's CSS and fails on any new `--bs-*` reference.

The other rules: the square `cv-coreui-icon-btn`, `cv-coreui-section-legend` (registered for the conditional and formset
legends), the two subtle badge colours, `--cui-breadcrumb-margin-bottom: 0` for the header's breadcrumb row (U9, upstream
has no `breadcrumb:*` class key), a smaller view title below the owner tabs, and two rules that drop the inner bottom
margins of the card table and its pagination.

## Forms

Forms render through [`crispy_coreui`](crispy_coreui.md); the theme needs no crispy overrides. Form buttons come from the class table like all others (`form:*` keys). `view_create/update/delete.content.html` are not overridden: the card
comes from the form frame, which checks `request.headers.x_cv_modal` to stay bare inside a modal.

## Icons

django-crud-views refers to icons by semantic name and resolves names through a layered table (package defaults, theme
registrations, `CRUD_VIEWS_ICONS`) to `library:name` values. The theme plugs into that:

- `django_coreui/icons.py` holds CoreUI Icons Free as inline SVG (`ICONS`); `crud_views_coreui/icons.py` holds the
  registry renderer `render` and `COREUI_ICONS`, a `coreui:cil-*` icon for every semantic name the package defines (37
  names);
- `render` calls `django_coreui.icons.svg()` and does not apply `COREUI_ICON_ALIASES` (that setting is for templates);
- the system check `crud_views_coreui.W001` warns about a `coreui:` value without an SVG. See [Icons](icons.md) for the
  substitutions where the free set has no equivalent.

## Edition seam

`settings.COREUI = {"edition": "free"}` selects the CoreUI edition. `django_coreui.conf.EDITIONS` lists the editions the
package serves, today `("free",)`, and the system check `django_coreui.E001` rejects any other value. The only template
that reads the edition is `django_coreui/includes/assets.html`, which takes CoreUI's CSS and JavaScript from
`django_coreui/assets.py`: jsDelivr URLs pinned to `COREUI_VERSION` (5.9.1) with SRI hashes (`sha384`, computed with
`curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A`; recompute both when the version changes). Nothing
else in either package, or in the demo, branches on the edition.

A PRO edition is planned behind this setting as a separate design. CoreUI PRO assets are commercial and are never shipped
with this package. Anyone who wants PRO needs their own CoreUI licence.

## Not covered yet

- A PRO edition (above), and PRO widgets (date range picker, multi select).
- A simplebar scroll container in the sidebar (CoreUI's sidebar scrolls without it).
- A public hosted demo.
