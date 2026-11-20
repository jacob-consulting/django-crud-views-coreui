from crud_views.lib.icons import _get_renderers, _icon_str, get_icons
from django.core.checks import CheckMessage, Tags, Warning, register

from crud_views_coreui.icons import render
from django_coreui.icons import ICONS


@register(Tags.templates)
def check_coreui_icons(app_configs=None, **kwargs) -> list[CheckMessage]:
    """Warn when a ``coreui:`` icon value has no SVG in ``django_coreui.icons.ICONS``."""
    messages: list[CheckMessage] = []
    if _get_renderers().get("coreui") is not render:
        return messages  # the project remapped the prefix to another renderer
    for key, value in get_icons().items():
        stripped = _icon_str(value)
        if stripped is None or not stripped.startswith("coreui:"):
            continue
        name = stripped.split(":", 1)[1]
        if name not in ICONS:
            messages.append(
                Warning(
                    f"Icon {key!r} = {value!r}: crud_views_coreui has no SVG for CoreUI icon {name!r}.",
                    hint="Vendor it with scripts/vendor_icons.py (CoreUI Icons Free) or use another library prefix.",
                    id="crud_views_coreui.W001",
                )
            )
    return messages
