"""The Acme app's icon vocabulary: domain meaning -> CoreUI free icon name (cil-*).

App code, templates and seed data name icons by what they stand for (``"customer"``, ``"order"``), never by picture or
library. This table is the only place that knows the library: ``settings.py`` feeds it to ``CRUD_VIEWS_ICONS`` (for
django-crud-views, as ``coreui:<name>``) and to ``COREUI_ICON_ALIASES`` (for ``{% icon %}`` in templates). Another
theme keeps the keys and swaps the values.
"""

ACME_ICONS: dict[str, str] = {
    # entities
    "customer": "cil-building",
    "address": "cil-location-pin",
    "order": "cil-description",
    "subscription": "cil-loop-circular",
    "product": "cil-gift",
    "beans": "cil-leaf",
    "equipment": "cil-settings",
    "category": "cil-layers",
    "lot": "cil-data-transfer-down",
    "cupping": "cil-coffee",
    "batch": "cil-fire",
    "shipment": "cil-truck",
    # sidebar sections
    "sales": "cil-building",
    "catalog": "cil-gift",
    "roastery": "cil-fire",
    # property groups
    "about": "cil-info",
    "pricing": "cil-tags",
    "stock": "cil-balance-scale",
    "origin": "cil-location-pin",
    # actions
    "packing-slip": "cil-print",
    "duplicate": "cil-copy",
    "run-subscriptions": "cil-media-play",
    "table-view": "cil-spreadsheet",
    "mark-default": "cil-star",
    # workflow steps and shipment events
    "confirm": "cil-check",
    "roasted": "cil-coffee",
    "shipped": "cil-gift",
    "delivered": "cil-check-circle",
    "cancelled": "cil-x-circle",
    "picked-up": "cil-gift",
    "in-transit": "cil-truck",
}
