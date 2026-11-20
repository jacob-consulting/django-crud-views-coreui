"""The CoreUI icons in django-crud-views' icon registry.

They plug in as the ``coreui`` library (``coreui:cil-pencil``, see ``render``). ``COREUI_ICONS`` maps the package's
semantic icon names to CoreUI free icons; a project overrides single keys with ``CRUD_VIEWS_ICONS``. The icons
themselves live in ``django_coreui.icons`` (add one with ``scripts/vendor_icons.py``).

Where CoreUI Icons Free has no icon for the Tabler theme's choice, the closest free one is used: ``detail``
(Tabler ``eye``, no free eye) is a magnifying glass, ``create`` (``square-plus``) is ``cil-library-add``,
``actions-menu`` (horizontal ``dots``) is the vertical ``cil-options``, ``formset-delete`` (``square-x``) is
``cil-delete``, ``property-detail``/``message-info`` (``info-circle``) are the boxed ``cil-info``,
``message-error`` (``alert-circle``) is ``cil-x-circle`` and ``text-icon`` (``file-text``) is ``cil-description``.
"""

from django.utils.safestring import SafeString

from django_coreui.icons import svg

COREUI_ICONS: dict[str, str] = {
    "list": "coreui:cil-list",
    "card": "coreui:cil-grid",
    "detail": "coreui:cil-magnifying-glass",
    "create": "coreui:cil-library-add",
    "update": "coreui:cil-pencil",
    "delete": "coreui:cil-trash",
    "save": "coreui:cil-check",
    "cancel": "coreui:cil-arrow-left",
    "filter-reset": "coreui:cil-filter-x",
    "order-up": "coreui:cil-arrow-top",
    "order-down": "coreui:cil-arrow-bottom",
    "manage": "coreui:cil-settings",
    "workflow": "coreui:cil-sitemap",
    "actions-menu": "coreui:cil-options",
    "filter": "coreui:cil-filter",
    "filter-close": "coreui:cil-filter-x",
    "language": "coreui:cil-language",
    "sort-asc": "coreui:cil-sort-ascending",
    "sort-desc": "coreui:cil-sort-descending",
    "table-sort-asc": "coreui:cil-chevron-double-up",
    "table-sort-desc": "coreui:cil-chevron-double-down",
    "formset-up": "coreui:cil-caret-top",
    "formset-down": "coreui:cil-caret-bottom",
    "formset-add": "coreui:cil-plus",
    "formset-delete": "coreui:cil-delete",
    "field-marker": "coreui:cil-chevron-double-right",
    "boolean-true": "coreui:cil-check-circle",
    "boolean-false": "coreui:cil-x-circle",
    "property-detail": "coreui:cil-info",
    "text-icon": "coreui:cil-description",
    "message-success": "coreui:cil-check",
    "message-info": "coreui:cil-info",
    "message-warning": "coreui:cil-warning",
    "message-error": "coreui:cil-x-circle",
    "message-debug": "coreui:cil-bug",
    "page-previous": "coreui:cil-chevron-left",
    "page-next": "coreui:cil-chevron-right",
}


def render(name: str, *, css: str, config: dict) -> SafeString:
    """Renderer of the ``coreui`` icon library in django-crud-views' icon registry.

    ``name`` is used as is: crud_views' own icon table (``CRUD_VIEWS_ICONS``) is the alias layer here, so the shell's
    ``COREUI_ICON_ALIASES`` (for the ``{% icon %}`` tag) is not applied.
    """
    return svg(name, css)
