from crud_views.lib.icons import _get_renderers, _icon_str, get_icons
from django.apps import apps
from django.core.checks import CheckMessage, Error, Tags, Warning, register

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
                    hint=(
                        "Add its SVG to django_coreui.icons.ICONS at startup (see 'Adding icons' in the Icons docs) "
                        "or use another library prefix."
                    ),
                    id="crud_views_coreui.W001",
                )
            )
    return messages


#: Apps whose templates the theme overrides (upstream tracker U11): Django's app template loader takes the first app
#: that has the template, so the theme must be listed before each of them. The two overrides left are layout,
#: crud_views/snippets/form_frame.html and crud_views/table/bootstrap5.html; since upstream #391 (the data prefix) the
#: theme overrides no crud_views_object_detail template.
OVERRIDDEN_APPS = ("crud_views",)


@register(Tags.templates)
def check_app_order(app_configs=None, **kwargs) -> list[CheckMessage]:
    """Error when crud_views_coreui comes after an app whose templates it overrides."""
    names = [config.name for config in apps.get_app_configs()]
    if "crud_views_coreui" not in names:
        return []
    theme = names.index("crud_views_coreui")
    before = [name for name in OVERRIDDEN_APPS if name in names and names.index(name) < theme]
    if not before:
        return []
    return [
        Error(
            f"crud_views_coreui is listed in INSTALLED_APPS after {', '.join(map(repr, before))}: its templates win "
            "over the theme's (the form frame and the card table lose their CoreUI layout).",
            hint="List crud_views_coreui before crud_views in INSTALLED_APPS.",
            id="crud_views_coreui.E002",
        )
    ]
