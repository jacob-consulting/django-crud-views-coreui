# Installation

```shell
pip install django-crud-views-coreui
```

This installs django-crud-views, django-crispy-forms and crispy-bootstrap5 with it. For django-crud-views' optional
features (workflow, polymorphic, ordered, guardian) install its extras as usual, e.g.
`pip install "django-crud-views[workflow]"`. The theme styles the type-ahead widgets of
[django-crud-views-extensions](https://github.com/jacob-consulting/django-crud-views-extensions) from version 0.4.0 on,
whose skins read the same `--cv-*` tokens as django-crud-views.

## `INSTALLED_APPS`

The theme overrides two `crud_views` templates (the form frame and the table), so **`crud_views_coreui` must come before
`crud_views`**. Django's app template loader takes the first app that has a template; anything the theme does not override
falls through to the stock templates.

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "django_tables2",
    "django_filters",
    "django_coreui",
    "crud_views_coreui",  # before crud_views
    "crud_views.apps.CrudViewsConfig",
    "crud_views_object_detail",  # if you use it
    # crud_views_workflow, crud_views_polymorphic, ... as you use them
    "your_app",
]
```

If the order is wrong, crud_views' stock form frame and table win over the theme's: forms and lists sit bare on CoreUI's
gray page instead of on cards. The system check `crud_views_coreui.E002` turns that into an error (see below).
`crud_views_object_detail` and the other crud_views apps may come anywhere.

`crispy_bootstrap5` does not need to be in `INSTALLED_APPS`: the pack's templates live in `django_coreui`, and only two
layout objects subclass crispy-bootstrap5's Python classes.

## Settings

```python
# Pages of django-crud-views extend the theme's page template (or your own template that extends it).
CRUD_VIEWS_EXTENDS = "crud_views_coreui/page.html"

# Forms render through the CoreUI template pack.
CRISPY_ALLOWED_TEMPLATE_PACKS = ("crispy_coreui",)
CRISPY_TEMPLATE_PACK = "crispy_coreui"

# django-tables2 tables use the theme's table template.
DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"

# The CoreUI edition. "free" is the only one this release serves; it is also the default.
COREUI = {"edition": "free"}
```

Two optional settings deal with icons (see [Icons](icons.md)):

```python
# Your own semantic names for CoreUI icons, for {% icon %} in templates (django_coreui).
COREUI_ICON_ALIASES = {"customer": "cil-building"}

# The same names for django-crud-views (views, ViewSets, buttons): "<library>:<name>".
CRUD_VIEWS_ICONS = {"customer": "coreui:cil-building"}
```

The theme registers a CoreUI icon for every semantic name django-crud-views defines, so `CRUD_VIEWS_ICONS` is only
needed for your own names or to change one.

## Public pages and the admin

The shell works for anonymous visitors: the header shows a "Sign in" link (to `settings.LOGIN_URL`) instead of the user
menu, so a page without a login requirement renders. The "Admin site" and "Change password" entries of the user menu
appear for staff only when `django.contrib.admin`'s URLconf is mounted; without it they are left out. The shell's
templates carry no inline scripts or `style=` attributes, so a strict Content-Security-Policy only needs to allow the
CoreUI CDN and your static files.

## System checks

```shell
python manage.py check --fail-level WARNING
```

| Id | Level | Meaning |
|---|---|---|
| `django_coreui.E001` | Error | `COREUI` is not a dict, or `COREUI["edition"]` is not an edition this version serves (only `"free"`). |
| `crud_views_coreui.E002` | Error | `crud_views_coreui` is listed after `crud_views` in `INSTALLED_APPS`. |
| `crud_views_coreui.W001` | Warning | A `coreui:` icon in `CRUD_VIEWS_ICONS` has no SVG in `django_coreui.icons.ICONS`; add its SVG to `ICONS` at startup (see [Icons](icons.md#adding-icons)) or use another library prefix. |

## Your own page layer

To add something to every crud_views page (a panel, a script), point `CRUD_VIEWS_EXTENDS` at your own template that
extends the theme's page. The demo does this for its "Show code" panel:

```django
{% extends "crud_views_coreui/page.html" %}
{% block actions %}{{ block.super }}<a class="btn btn-outline-secondary" href="#help">Help</a>{% endblock %}
```

The blocks available are those of `django_coreui/layouts/app.html`: `breadcrumb`, `page_header_before`,
`page_header_top`, `pretitle`, `page_heading` (wraps `page_title`), `subtitle`, `actions`, `messages`, `content`, plus
`title`, `extra_head`, `body` and `extra_js` from `django_coreui/base.html`. The theme's page adds `cv_navbar` (the
ViewSet Navigation tabs), `cv_paragraph`, `cv_context`, `cv_filter` and `cv_content`.

## Pages outside django-crud-views

Any template can use the shell directly:

```django
{% extends "django_coreui/layouts/app.html" %}
{% block title %}Reports{% endblock %}
{% block page_title %}Reports{% endblock %}
{% block content %}<div class="card"><div class="card-body">...</div></div>{% endblock %}
```

`django_coreui` also ships `registration/login.html`, a CoreUI sign-in page for Django's `LoginView`, with a
`login_after` block below the form.
