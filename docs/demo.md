# Demo

**Acme Roasters** is a back office for a specialty coffee roastery, built with django-crud-views and themed by this
package. It covers customers with per-object permissions (Guardian), addresses, orders with a workflow and a line
formset, subscriptions, polymorphic products, ordered categories, green coffee lots, cupping sessions with score
formsets, roast batches and shipments from a fake courier API. Every crud_views page has a "Show code" panel with the
code behind it, and `/theming/` shows the whole theme.

The app code never imports the theme: it is a plain django-crud-views project with `crud_views_coreui` in
`INSTALLED_APPS`. It names icons by meaning (`"customer"`, `"order"`); one table, `ACME_ICONS`, maps those names to
CoreUI icons (see [Icons](icons.md)).

There is no public demo yet: run it locally.

## Locally

```shell
git clone https://github.com/jacob-consulting/django-crud-views-coreui.git
cd django-crud-views-coreui
task up      # uv sync, migrate, superuser admin/admin, seed the demo data, runserver
```

Open <http://127.0.0.1:8000/> and sign in. See [Development](development.md) for running it without Task, and for the
sibling checkouts of django-crud-views that local development uses.

## Accounts

| Account | Password | Role |
|---|---|---|
| `alex` | `demo` | Owner: everything, including django-crud-views' manage pages |
| `sam` | `demo` | Account manager: only the customers granted to them |
| `kim` | `demo` | Head roaster: lots, cupping and roasting; customers read-only |
| `admin` | `admin` | Superuser created by `task up`: everything, plus `/admin/` |

The sign-in page has a button per demo account that fills the form.

## Pages

The sidebar shows what the account may open.

| Section | Page | URL | Features on show |
|---|---|---|---|
| | Dashboard | `/` | plain Django view: stat cards, revenue chart (ApexCharts, following the colour mode), orders to roast, recent cuppings |
| Sales | Customers | `/customer/` | Guardian per-object permissions, conditional group, object detail `split-card`, action menus, nested addresses, delete protection |
| | Orders | `/orders/`, `/customer/<id>/order/` | two ViewSets on one model, workflow, line formset, typeahead customer picker, datetimepicker, custom form, context button |
| | Subscriptions | `/subscriptions/` | nested and top-level lists, a custom form without an object |
| Catalog | Products | `/product/` | polymorphic, card view plus a table, per-kind object detail |
| | Categories | `/category/` | ordered (up/down) |
| Roastery | Green lots | `/lot/` | object detail `accordion`, nested cupping sessions with a score formset |
| | Roast batches | `/batch/` | M2M to orders, computed weight loss |
| | Shipments | `/shipment/` | a `Resource` (no ORM) from a fake courier API |
| Developer | Form showcase | `/showcase/` | every branch of the [crispy pack](crispy_coreui.md) on one form |
| | How this is themed | `/theming/` | the theme's files and line counts, computed at render time |
| Users | Users | `/users/` | searchable user list, create in a modal |

Plus `/accounts/login/` and `/admin/` (staff). The demo keeps the package's default layout (colour mode auto, default
sidebar); the gear in the header switches both, see [Layouts](layouts.md).

## Demo data

`seed_demo` builds one coherent world from a fixed random seed: customers with their addresses, orders in every
workflow state, products of three kinds, green lots with cupping sessions, roast batches, subscriptions and shipments. It
refuses to run when the demo accounts already exist; `seed_demo --reset` deletes the demo apps' rows and the demo
accounts and groups (not `admin`, not the showcase items) and builds the world again; `--seed N` varies it.

## Settings from the environment

`DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1`/`0`, default `1`), `DJANGO_ALLOWED_HOSTS` (comma-separated, default
`localhost,127.0.0.1`) and `CRUD_VIEWS_MANAGE_VIEWS_ENABLED`. The last one defaults to `yes`: django-crud-views' manage
pages list who holds which permission, so only active members of the `CRUD_VIEWS_MANAGE` group may open them, whatever
`DEBUG` says (the seed makes `alex` the only member). `no` closes them for everyone, `debug_only` also requires `DEBUG`.
The built-in secret key is for local development only. The demo also switches on `CRUD_VIEWS_MANAGE_SHOW_USERS` and
`CRUD_VIEWS_MANAGE_ACCESS_TRACE` (see `example/config/settings.py`).
