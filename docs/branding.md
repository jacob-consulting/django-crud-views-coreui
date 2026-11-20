# Branding

Branding is done by overriding small include templates of `django_coreui`. Put files with the same path in a directory
listed in `TEMPLATES[0]["DIRS"]`, which Django searches before app templates.

| Template | Default | Purpose |
|---|---|---|
| `django_coreui/includes/site_name.html` | `Django CoreUI` | Name in the `<title>`, the sidebar and the sign-in page |
| `django_coreui/includes/brand.html` | speedometer icon and site name | Logo and name at the top of the sidebar |
| `django_coreui/includes/head.html` | empty | Extra `<head>` content on every page: favicon, stylesheets |
| `django_coreui/includes/nav_menu.html` | empty | The sidebar menu entries (see below) |
| `django_coreui/includes/user_menu_items.html` | admin links for staff, Sign out | The user dropdown in the header (keep the Sign out form when overriding) |
| `django_coreui/includes/layout_defaults.html` | empty (comments only) | The project's default colour mode and sidebar (see [Layouts](layouts.md)) |

Other includes (`header.html`, `sidebar.html`, `messages.html`, `layout_switch_menu.html`, `assets.html`) are part of
the layout; `field.html` renders one bound field in CoreUI markup for hand-written forms.

The demo's files are in
`example/templates/django_coreui/includes/` in the repository.

## Brand and colour

```django
{# templates/django_coreui/includes/brand.html #}
{% load coreui %}<a href="{% url 'home' %}" class="d-inline-flex align-items-center gap-2 text-reset text-decoration-none">
  <span class="avatar avatar-md bg-primary text-white">{% icon "cil-coffee" %}</span>
  <span class="sidebar-brand-full fw-semibold">{% include "django_coreui/includes/site_name.html" %}</span>
</a>
```

The `sidebar-brand-full` class hides the name in the narrow sidebar and keeps the mark.

The primary colour is CoreUI's CSS custom properties; set them in a stylesheet loaded from `head.html`. CoreUI compiles
the hex value of the primary into some component classes (`.btn-primary`, `.btn-outline-primary`, ...), so a brand
colour needs those restated as well; the demo's
`acme.css` (`example/static/acme/acme.css` in the repository) shows
a complete sienna brand for light and dark mode.

```css
:root { --cui-primary: #a0522d; --cui-primary-rgb: 160, 82, 45; }
```

## The menu

`nav_menu.html` is included once, inside the sidebar's `ul.sidebar-nav`. Render `li.nav-item` entries and `li.nav-title`
section headings:

```django
{% load coreui %}
<li class="nav-item">
  <a class="nav-link" href="{% url 'customer-list' %}">{% icon "cil-people" "nav-icon" %} Customers</a>
</li>
<li class="nav-title">Catalog</li>
```

The demo builds its menu, with permission checks and the active entry, in one template tag
(`example/config/templatetags/acme_nav.py` in the repository).
