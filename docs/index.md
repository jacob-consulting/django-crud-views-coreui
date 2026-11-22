# Django CRUD Views CoreUI

Current version: 0.1.0

A [CoreUI](https://coreui.io) 5.9.1 (free edition) theme for
[django-crud-views](https://django-crud-views.readthedocs.io/). One distribution, `django-crud-views-coreui`, ships two
Django apps:

- **`crud_views_coreui`**: the theme. Listed before `crud_views` in `INSTALLED_APPS`, it shadows a few templates of
  django-crud-views' stock Bootstrap 5 theme and registers CoreUI button classes, icons and the JS namespace through
  upstream's hooks. Your ViewSets and views need no changes.
- **`django_coreui`**: a CoreUI page shell that does not depend on django-crud-views: base template and admin layout
  (sidebar and header), sign-in page, `{% load coreui %}` icon tags, an end-user colour-mode and sidebar switch, and
  `crispy_coreui`, a django-crispy-forms template pack with CoreUI markup.

CoreUI's CSS and JavaScript load from the jsDelivr CDN with Subresource Integrity hashes; nothing from CoreUI is
bundled.

!!! note "Free edition"
    This release is the free edition: CoreUI 5.9.1 (MIT). A PRO edition is planned behind the `COREUI["edition"]`
    setting; today any value other than `"free"` is a system check error. CoreUI PRO material is never shipped with
    this package, so a PRO edition will need your own CoreUI licence.

Supported: Python 3.12-3.15, Django 4.2, 5.2 and 6.1, django-crud-views >=0.30. The theme tracks django-crud-views `main` until 1.0.0rc1 is on PyPI.

- [Installation](installation.md): settings, in the order they matter.
- [Branding](branding.md) and [Layouts](layouts.md): site name, logo, menu, default colour mode and sidebar.
- [Icons](icons.md) and the [crispy template pack](crispy_coreui.md).
- [Theme internals](theme_internals.md): what is overridden and why, and every hook the theme uses.
- [Demo](demo.md): Acme Roasters, a back office for a coffee roastery, built with django-crud-views and this theme.
- [Development](development.md): repository layout, tests, vendoring scripts.

## Attribution

Icons are [CoreUI Icons](https://github.com/coreui/coreui-icons) Free 3.1.0 by creativeLabs Łukasz Holeczek, licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (the icon package's code is MIT).
