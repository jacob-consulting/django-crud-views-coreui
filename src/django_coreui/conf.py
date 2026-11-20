"""``settings.COREUI``: the shell's settings, with defaults."""

from django.conf import settings

# The CoreUI editions this package can serve. PRO is a later, separate design (see the "Edition seam").
EDITIONS = ("free",)

DEFAULTS = {"edition": "free"}


def coreui_settings() -> dict:
    """``settings.COREUI`` over the defaults."""
    return {**DEFAULTS, **(getattr(settings, "COREUI", None) or {})}
