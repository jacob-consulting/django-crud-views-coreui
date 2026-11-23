# Theme internals

How `crud_views_coreui` themes django-crud-views: what it overrides, which upstream hooks it uses, and where it stops.
It is exercised by the Acme Roasters demo (`example/`), which puts nested ViewSets, formsets, conditional groups,
workflow, polymorphic models, object detail packs, Guardian, resources, card views and the django-crud-views-extensions
widgets through it, and by its own test app under `tests/crud_views_coreui/`. Everything the theme needed beyond
upstream hooks is an entry in the
upstream tracker (`superpowers/notes/upstream-tracker.md` in the GitHub repository jacob-consulting/django-crud-views-coreui; maintainer notes, not on this site)
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
- it is listed **before** `crud_views` in `INSTALLED_APPS`, so Django's app template loader finds its files first (check
  `crud_views_coreui.E002` enforces the order, tracker U11),
- anything it does not override falls through to the stock Bootstrap 5 templates, whose markup is CoreUI markup.

So the theme is a few template overrides, a little Python (the icon library, the button class table, system checks) and
two static files (a stylesheet and a script). No crud_views code is patched or subclassed.

```python
INSTALLED_APPS = [
    ...,
    "crispy_forms",
    "django_tables2",
    "django_filters",
    "django_coreui",  # also provides the crispy_coreui template pack
    "crud_views_coreui",  # before crud_views
    "crud_views.apps.CrudViewsConfig",
    "crud_views_object_detail",
]
CRISPY_TEMPLATE_PACK = "crispy_coreui"
CRISPY_ALLOWED_TEMPLATE_PACKS = ("crispy_coreui",)
CRUD_VIEWS_EXTENDS = "crud_views_coreui/page.html"
DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"
COREUI = {"edition": "free"}
```

`CrudViewsCoreuiConfig.ready()` registers eight things through upstream's hooks: the `coreui` icon library, the icon
table (`register_icons`), label-mode defaults (`{"form": "both"}`), the button class table
(`register_button_classes`; the `workflow:*` keys only when `crud_views_workflow` is installed), the data-attribute
prefix (`register_data_prefix("coreui")`), the JavaScript namespace (`register_js_namespace("coreui")`), the tooltip
placements (`register_tooltip_placements({"context": "bottom"})`) and the asset bundle (`register_assets`:
`crud_views_coreui.css`).

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
| `blue`, `pink` (manage page legend) | `cv-coreui-badge-blue`, `cv-coreui-badge-pink`: subtle badges built in the theme CSS from `--cui-blue` and `--cui-pink`, which CoreUI defines but gives no utility classes; light in dark mode too, like CoreUI's `bg-*-subtle` |

One key goes beyond the Tabler set: `breadcrumb:list` is `breadcrumb my-0`, as CoreUI's free admin template writes the
breadcrumb in the header's second row (CoreUI's `.breadcrumb` otherwise keeps a 1rem bottom margin; upstream #393,
tracker U9). A project that sets `breadcrumb:list` itself should keep `my-0`. The table header is upstream's: it sets
`aria-sort` and the sort icon from the table's ordering, also for tables with a `prefix` (#393, tracker U10).

The label mode decides the square shape: each action key exists as `location:variant` (labelled) and
`location:variant:icon` (icon-only, with `cv-coreui-icon-btn`). The manage page's badges never use `primary`, because
its legend names colours and a project's primary may be any colour.

## Overridden templates

The page and two templates:

```
crud_views_coreui/
  page.html                                          CRUD_VIEWS_EXTENDS target (above)
crud_views/
  snippets/form_frame.html        layout: the form in a card (bare in a modal); extends upstream's frame
  table/bootstrap5.html           layout: the table on a card, in .table-responsive, pagination in the card footer;
                                  extends upstream's table, three blocks with {{ block.super }}
```

CoreUI's layout puts the page on `--cui-tertiary-bg` (gray) and its content on cards. Stock Bootstrap 5 markup is
CoreUI markup, so a layout override is kept only where stock content would sit bare on the gray page: the form frame and
the table. The Tabler theme's other layout overrides (modal shell, alert, card, filter, card view) were dropped, because
the stock markup is right. `card:root` is `card mb-4`, since the stock card grid has no vertical gutter.

### Data attributes (U1, U2)

CoreUI's data API ignores `data-bs-*`. django-crud-views writes its data-API attributes (the `⋯` actions menu, the
language selector, the vertical-tabs object detail, the accordion group) with a registered prefix, and its object-detail
`tabs.js` reads the same prefix from `#cv-config` on every scan, also for content loaded into a modal (upstream #391).
The theme registers `coreui` in `ready()`, so those templates render `data-coreui-*` and the theme copies none of them.
A test renders every test app page, full and as a modal partial, and finds no `data-bs-`; another scans upstream's
templates and scripts and fails on any that hard-codes `data-bs-` instead of using the prefix.

## JavaScript

### The adapters (U4, U13)

Core scripts of django-crud-views call Bootstrap components only through `cv.adapters` (`modal`, `tooltip`, `tab`,
`collapse`, `alert`). CoreUI's bundle exposes the same components on `window.coreui`, so the theme registers that name
in `ready()` and ships no script of its own:

```python
register_js_namespace("coreui")
register_tooltip_placements({"context": "bottom"})
```

Both values travel on `#cv-config` (`data-js-namespace`, `data-tooltip-placements`), and upstream's stock adapters read
them on every call, so CoreUI's bundle may load deferred. The placement puts toolbar tooltips below the buttons, so
they do not cover the page header. A button with its own `data-coreui-placement` keeps it, and every other location
keeps CoreUI's default.

The stock modal adapter names the events it waits for after the data prefix (`hide.coreui.modal`,
`hidden.coreui.modal`); that is how it sees a CoreUI modal close and returns focus to the opener. A project that
copies `crud_views/tags/cv_config.html` must keep its `data-data-prefix`, `data-js-namespace` and
`data-tooltip-placements` attributes, or the adapters fall back to `window.bootstrap` and `*.bs.modal`.

### Dropdowns (U3)

There is no dropdown adapter upstream; dropdowns rely on the data API alone. The theme needs no JavaScript for that: with
the registered prefix the dropdown toggles say `data-coreui-toggle`, so CoreUI's own data API handles them.

### The shell

`django_coreui` ships `layout-switch.js` (colour mode and sidebar state, see [Layouts](layouts.md)); it never touches
`cv`. CoreUI's bundle (`window.coreui`) loads synchronously at the end of `<body>`, as in CoreUI's own admin template.

## CSS tokens (U5)

django-crud-views' `manage.css` and `formset.css` read six `--cv-*` tokens, each falling back to Bootstrap's `--bs-*`
property and then a literal (upstream #394). CoreUI does not define `--bs-*`, so without the theme the manage page and
formsets would use the literals and ignore dark mode. `crud_views_coreui.css` sets the tokens (`--cv-secondary-color`,
`--cv-secondary-text-emphasis`, `--cv-body-bg`, `--cv-border-color`, `--cv-border-radius`, `--cv-tertiary-bg`) from
the matching `--cui-*` properties, on the elements those rules style rather than on `:root`, so a `[data-coreui-theme]`
subtree is followed. The exception is `--cv-secondary-text-emphasis`, set from `--cui-body-color`: CoreUI's
`--cui-secondary-text-emphasis` stays dark in dark mode. One rule hands a value on the other way: upstream's manage help
button sets Bootstrap's `--bs-btn-color`, and CoreUI's `.btn` reads `--cui-btn-color`. A test parses upstream's CSS and
fails on a token the theme does not set. The same block exists for django-crud-views-extensions' typeahead skins
(`.cv-typeahead`, `.cv-typeahead-select`, plus `--cv-border-color-translucent` and `--cv-highlight-bg`; extensions 0.4.0,
tracker U12), whose select popup otherwise has no background.

The other rules: the square `cv-coreui-icon-btn`, `cv-coreui-section-legend` (registered for the conditional and formset
legends), the two subtle badge colours, a smaller view title below the owner tabs, and two rules that drop the inner bottom
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

## Bulk actions

Bulk selection (django-crud-views #392) needs eight button-class keys and no template or CSS:

- The toolbar buttons take their class from the destination's `cv_action_variant` (django-crud-views #400):
  `bulk:primary`, `bulk:secondary`, `bulk:tertiary` and `bulk:danger`, plus an `:icon` key each for the icon-only label
  mode. The theme sets them to the `context:*` values, because the bulk toolbar is a page-level button row like the
  context toolbar: secondary is `btn btn-outline-secondary`, danger `btn btn-outline-danger`. The demo marks "Cancel
  orders" as danger. A destination without a variant renders secondary.
- The other seven `bulk:*` keys are not set: upstream's defaults (`form-check-input`, `d-flex` flex rows,
  `position-relative` card cells) are CoreUI classes as well.
- The toolbar offers only the actions the viewer may enter (django-crud-views #399); with none left, the page has no
  toolbar and no checkboxes. The stock templates do this, so the theme needs nothing for it.
- The toolbar renders above the table card or the card grid, and carries the select-all checkbox. The table's first
  column, "Select", holds one checkbox per row inside the table card; it scrolls with the table in the card's
  `.table-responsive`, so a wide list does not widen the page (the same wrapper solves C9 of the AdminLTE tracker).
  Every checkbox posts through `form="<toolbar form id>"`.
- The review page renders in the theme's page like any custom form view; result and warning messages go through
  crud_views' own alerts, once.

## Not covered yet

- A PRO edition (above), and PRO widgets (date range picker, multi select).
- A simplebar scroll container in the sidebar (CoreUI's sidebar scrolls without it).
- A public hosted demo.
