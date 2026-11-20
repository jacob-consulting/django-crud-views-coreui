# django-crud-views-coreui

Current version: 0.1.0

A [CoreUI](https://coreui.io) 5.9.1 (free edition) theme for [django-crud-views](https://github.com/jacob-consulting/django-crud-views).
One distribution, two Django apps:

- `crud_views_coreui`: the theme. Listed before `crud_views` in `INSTALLED_APPS`, it shadows a few stock Bootstrap 5
  templates and registers CoreUI button classes, icons and JavaScript adapters through upstream's hooks; your views need
  no changes.
- `django_coreui`: a CoreUI page shell that does not depend on django-crud-views: admin layout with sidebar and header,
  sign-in page, `{% load coreui %}` icon tags, an end-user colour-mode and sidebar switch, and `crispy_coreui`, a
  django-crispy-forms template pack.

Python 3.12-3.15, Django 4.2, 5.2 and 6.1. CoreUI loads from the jsDelivr CDN with Subresource Integrity hashes.
Work in progress: not released yet, and there is no public demo yet.

- Source and issues: https://github.com/jacob-consulting/django-crud-views-coreui
- Documentation: https://django-crud-views-coreui.readthedocs.io/ (not published yet; the sources are in `docs/`)

## Free and PRO

This release is the **free edition**: CoreUI 5.9.1, MIT licensed, loaded from jsDelivr. A PRO edition is planned behind
the `COREUI = {"edition": "free"}` setting; today any other value is a system check error (`django_coreui.E001`).
CoreUI PRO assets are never shipped with this package or kept in this repository: to use PRO you will need your own
CoreUI licence.

## Install

```shell
pip install django-crud-views-coreui
```

```python
INSTALLED_APPS = [
    # django.contrib apps, then:
    "crispy_forms",
    "django_tables2",
    "django_filters",
    "django_coreui",
    "crud_views_coreui",  # before crud_views and crud_views_object_detail: its templates shadow theirs (check E002)
    "crud_views.apps.CrudViewsConfig",
    # crud_views_object_detail, your apps
]

CRUD_VIEWS_EXTENDS = "crud_views_coreui/page.html"
CRISPY_ALLOWED_TEMPLATE_PACKS = ("crispy_coreui",)
CRISPY_TEMPLATE_PACK = "crispy_coreui"
DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"
COREUI = {"edition": "free"}
```

Branding (site name, logo, menu, default colour mode and sidebar) is done by overriding a few include templates; see
`docs/branding.md` and `docs/installation.md`.

## The demo: Acme Roasters

`example/` is a back office for a specialty coffee roastery (customers, orders, subscriptions, products, green coffee
lots, cupping, roast batches, shipments), built with django-crud-views and themed by this package. The app code never
imports the theme; every crud_views page has a "Show code" panel, and `/theming/` shows the whole theme.

### Run it

With [Task](https://taskfile.dev) and [uv](https://docs.astral.sh/uv/), next to checkouts of
[django-crud-views](https://github.com/jacob-consulting/django-crud-views) and
[django-crud-views-extensions](https://github.com/jacob-consulting/django-crud-views-extensions) (local development
installs both from `../`, because the theme tracks unreleased upstream features):

```shell
task up      # uv sync, migrate, superuser admin/admin, seed the demo data, runserver
task         # list all tasks (setup, run, seed, seed:reset, reset, test, test:matrix, ...)
```

Open http://127.0.0.1:8000/ and sign in. `task setup` is safe to re-run; `task seed:reset` rebuilds the demo data in
place; `task reset` deletes the SQLite database and uploaded media and sets everything up again.

### Demo accounts

| Account | Password | Role | Sees |
|---|---|---|---|
| `alex` | `demo` | Owner | everything, including django-crud-views' manage pages |
| `sam` | `demo` | Account manager | only the customers Guardian grants them, their orders and subscriptions; roastery and catalog read-only |
| `kim` | `demo` | Head roaster | roastery in full; customers, orders and catalog read-only, except the confirmed to roasted step |
| `admin` | `admin` | Superuser from the Taskfile | everything, plus `/admin/` |

The sign-in page has a button per demo account that fills the form.

### Pages

| Section | Page | URL |
|---|---|---|
| | Dashboard | `/` |
| Sales | Customers, Orders, Subscriptions | `/customer/`, `/orders/`, `/subscriptions/` |
| Catalog | Products, Categories | `/product/`, `/category/` |
| Roastery | Green lots, Roast batches, Shipments | `/lot/`, `/batch/`, `/shipment/` |
| Developer | Form showcase, How this is themed | `/showcase/`, `/theming/` |
| Users | Users | `/users/` |

Plus `/accounts/login/` and `/admin/` (staff). The gear in the header switches colour mode (light, dark, auto) and the
sidebar (default, narrow, unfoldable); the choice stays in the browser's `localStorage`. See `docs/demo.md` for what each
page shows.

### Settings from the environment

`DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1`/`0`, default `1`), `DJANGO_ALLOWED_HOSTS` (comma-separated) and
`CRUD_VIEWS_MANAGE_VIEWS_ENABLED` (`yes` by default: only active members of the `CRUD_VIEWS_MANAGE` group may open
django-crud-views' manage pages, whatever `DEBUG` says; the seed makes `alex` the only member. `no` closes them for
everyone, `debug_only` also requires `DEBUG`). The built-in secret key is for local development only.

## Development

```shell
task test          # all suites against the sibling checkouts, plus the system check
task test:matrix   # nox: Python 3.12-3.15 x Django 4.2/5.2/6.1 against the built package
uvx nox -s docs    # the documentation, strict
```

Everything the theme needed beyond upstream hooks (template overrides, scripts, CSS) is listed, with upstream file and
line, in [`superpowers/notes/upstream-tracker.md`](superpowers/notes/upstream-tracker.md).

## Attribution

Icons are from [CoreUI Icons](https://github.com/coreui/coreui-icons) Free 3.1.0 by creativeLabs Łukasz Holeczek,
licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (the icon package's code is MIT).

## License

MIT
