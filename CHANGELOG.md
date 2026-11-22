# Changelog

## Unreleased

- Repository scaffold for the `django-crud-views-coreui` distribution (`django_coreui`, `crud_views_coreui`).
- `django_coreui`: CoreUI 5.9.1 (free) admin layout, sign-in page, `{% icon %}` tag with CoreUI Icons Free 3.1.0 and
  `COREUI_ICON_ALIASES`, colour-mode and sidebar switch, the `crispy_coreui` template pack, and the
  `COREUI = {"edition": "free"}` setting (check `django_coreui.E001`).
- `crud_views_coreui`: the django-crud-views theme (button classes, icons, the JavaScript namespace and tooltip placements, CSS tokens, the `data-bs` ->
  `data-coreui` overrides, `aria-sort` table header, object-detail tabs script) and the system checks
  `crud_views_coreui.W001` and `E002`.
- `example/`: the Acme Roasters demo on CoreUI.
- Documentation: user guide in `docs/`, README, CLAUDE.md.
