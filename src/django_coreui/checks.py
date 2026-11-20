from django.core.checks import Error, register

from django_coreui.conf import EDITIONS, coreui_settings


@register()
def check_edition(app_configs, **kwargs):
    """``settings.COREUI["edition"]`` must be an edition this package serves."""
    edition = coreui_settings()["edition"]
    if edition in EDITIONS:
        return []
    return [
        Error(
            f"settings.COREUI['edition'] is {edition!r}; this version of django_coreui serves only "
            + ", ".join(repr(e) for e in EDITIONS)
            + ".",
            hint='Set COREUI = {"edition": "free"}.',
            id="django_coreui.E001",
        )
    ]
