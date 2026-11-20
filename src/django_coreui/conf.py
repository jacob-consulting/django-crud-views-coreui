"""``settings.COREUI``: the shell's settings, with defaults."""

from collections.abc import Mapping

from django.conf import settings

# The CoreUI editions this package can serve. PRO is a later, separate design (see the "Edition seam").
EDITIONS = ("free",)

DEFAULTS = {"edition": "free"}


def coreui_settings() -> dict:
    """``settings.COREUI`` over the defaults."""
    raw = getattr(settings, "COREUI", None) or {}
    return {**DEFAULTS, **(raw if isinstance(raw, Mapping) else {})}


def coreui_setting_is_mapping() -> bool:
    """False when ``settings.COREUI`` is set to something other than a mapping (reported by E001)."""
    return isinstance(getattr(settings, "COREUI", None) or {}, Mapping)
