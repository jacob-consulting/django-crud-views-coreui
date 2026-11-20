# Layouts

`django_coreui/layouts/app.html` renders CoreUI's admin layout: a sidebar, a header with the breadcrumb row, the page
header (title and actions), the content and a footer. The shell has one navigation, the sidebar. Two settings decide how
it looks: the colour mode and the sidebar state. Both have a project default and a per-user choice.

| Setting | Values | Default |
|---|---|---|
| `theme` (colour mode) | `light`, `dark`, `auto` (follows the operating system) | `auto` |
| `sidebar` | `default`, `narrow`, `unfoldable` | `default` |

## The project default

`django_coreui/includes/layout_defaults.html` holds a JSON object with those two keys. It is empty in the package
(comments only), which gives `auto` and `default`. A project that wants a dark, narrow sidebar:

```json
{"theme": "dark", "sidebar": "narrow"}
```

Anything else (an unknown key or value, a non-string value, invalid JSON) raises a `ValueError` when a page renders, so
a typo cannot go unnoticed.

The `{% layout_defaults_attrs %}` tag on `<html>` (in `django_coreui/base.html`) turns the object into
`data-coreui-theme` (CoreUI's own colour-mode attribute, so a dark default renders dark even before JavaScript runs),
`data-coreui-sidebar` and a `data-coreui-layout-defaults` attribute that `layout-switch.js` reads.

## The user's choice

A gear in the header opens the layout switch: colour mode (Light, Dark, Auto) and sidebar
(Default, Narrow, Unfoldable). The choice is stored in the browser's `localStorage`, one key per setting, so it
survives reloads and applies on every page, the sign-in page included:

| Key | Values |
|---|---|
| `django-coreui-theme` | `light`, `dark`, `auto` |
| `django-coreui-sidebar` | `default`, `narrow`, `unfoldable` |

A choice equal to the project default is not stored (the key is removed), so changing the default later reaches users
who never picked anything else. A stored value that is not one of the listed ones is ignored. `layout-switch.js` loads in
the `<head>` so the colour mode applies before the first paint; in `auto` it follows `prefers-color-scheme` and its
changes. When the colour mode changes it dispatches a `ColorSchemeChange` event on `<html>`, which scripts that draw
charts can listen to (the demo's revenue chart does).

The sidebar's own unfoldable toggle in its footer is stored too, under the same key (`django-coreui-sidebar`).
