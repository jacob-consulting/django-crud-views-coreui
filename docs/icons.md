# Icons

`django_coreui.icons.ICONS` maps [CoreUI Icons](https://coreui.io/icons/) Free names (`cil-*`) to their SVG markup.
Icons render inline, so no icon font or sprite is loaded.

!!! info "Attribution"
    The icons are CoreUI Icons Free 3.1.0 by creativeLabs Łukasz Holeczek, licensed under
    [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the icon package's code is MIT. The attribution is in the
    header of `django_coreui/icons.py` and in the README. If you redistribute the icons, keep it.

## In templates

```django
{% load coreui %}
{% icon "cil-people" %}
{% icon "cil-warning" "icon-xl text-warning" %}
```

An unknown name renders nothing.

### Icon aliases and semantic names

Application code should name icons by what they stand for (`"customer"`, `"order"`), not by picture or library.
`COREUI_ICON_ALIASES` maps those names to CoreUI icon names; `{% icon %}` resolves the name through it first, and names
that are not aliased are used as given.

```python
COREUI_ICON_ALIASES = {"customer": "cil-building"}
```

```django
{% icon "customer" "icon" %}  {# renders cil-building #}
```

The demo keeps one table, `ACME_ICONS`
(`example/config/icons.py` in the GitHub repository jacob-consulting/django-crud-views-coreui (not on this site)),
and feeds it to both settings, so the same names work in templates and in django-crud-views:

```python
CRUD_VIEWS_ICONS = {key: f"coreui:{name}" for key, name in ACME_ICONS.items()}
COREUI_ICON_ALIASES = ACME_ICONS
```

Another theme keeps the keys and swaps the values.

## In django-crud-views

The theme registers an icon library `coreui` with django-crud-views and maps crud_views' semantic icon names (list,
detail, create, update, delete, ...) to CoreUI icons. Your own views can name any icon in `ICONS` with the `coreui:`
prefix, or use a semantic name from `CRUD_VIEWS_ICONS`:

```python
class CustomerDetailView(DetailViewPermissionRequired):
    cv_icon_action = "customer"  # a semantic name
    # or a library icon: cv_icon_action = "coreui:cil-star"
```

The system check `crud_views_coreui.W001` warns about a `coreui:` name that has no SVG in `ICONS`.

The free icon set has no counterpart for a few of the icons the Tabler theme uses, so the theme substitutes the nearest
one:

| Semantic name | CoreUI icon | Note |
|---|---|---|
| `detail` | `cil-magnifying-glass` | no eye icon in the free set |
| `create` | `cil-library-add` | no plus-in-square icon |
| `actions-menu` | `cil-options` | vertical dots; no horizontal ellipsis |
| `formset-delete` | `cil-delete` | |
| `property-detail`, `message-info` | `cil-info` | |
| `message-error` | `cil-x-circle` | no exclamation-circle |
| `text-icon` | `cil-description` | |
| `workflow` | `cil-sitemap` | |
| `card` | `cil-grid` | |

Override any of them with `CRUD_VIEWS_ICONS`.

## Adding icons

`ICONS` covers the icons the theme, the shell and the demo use. To add more, run the vendoring script from a checkout of
this repository; it fetches the icon from `@coreui/icons@3.1.0` on jsDelivr and merges it into `ICONS` (names are added
or refreshed, never dropped, and the dictionary stays sorted):

```shell
python scripts/vendor_icons.py cil-rocket cil-bell     # also accepted: rocket, cilRocket
```

Only the free set (`dist/esm/free/`) is read. The generated block of `django_coreui/icons.py` is not edited by hand.

In a project that only has the installed package, extend the dictionary at startup instead (for example in
`AppConfig.ready()`) with the inner SVG markup of the icon, a 512x512 viewBox. `ICONS` is read each time an icon renders,
so `{% icon %}`, the `coreui:` renderer and the system check all see the added name; until it is added, `W001` flags
any `coreui:` value that names it.

```python
from django_coreui.icons import ICONS

ICONS["cil-rocket"] = "<path fill='var(--ci-primary-color, currentcolor)' d='...'/>"
```
