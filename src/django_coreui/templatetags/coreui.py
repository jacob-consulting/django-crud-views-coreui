import json

from django import template
from django.contrib.messages import constants
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from django_coreui import assets
from django_coreui.conf import coreui_settings
from django_coreui.icons import resolve, svg

register = template.Library()

MESSAGE_ALERTS = {
    constants.DEBUG: {"css": "alert alert-secondary", "icon": "cil-bug"},
    constants.INFO: {"css": "alert alert-info", "icon": "cil-info"},
    constants.SUCCESS: {"css": "alert alert-success", "icon": "cil-check-circle"},
    constants.WARNING: {"css": "alert alert-warning", "icon": "cil-warning"},
    constants.ERROR: {"css": "alert alert-danger", "icon": "cil-x-circle"},
}

# CoreUI theme colours; the avatar uses the subtle background with the emphasis text colour of one of them.
AVATAR_COLORS = ["primary", "success", "info", "warning", "danger", "secondary"]


@register.simple_tag
def icon(name, css_class=""):
    """Render a CoreUI free icon as inline SVG: {% icon "cil-people" "icon-lg" %}.

    ``name`` is resolved through ``settings.COREUI_ICON_ALIASES`` first; unknown names render nothing.
    """
    return svg(resolve(name), css_class)


@register.filter
def initials(user):
    """Two-letter initials from the user's name, falling back to the username."""
    name = user.get_full_name().split()
    if len(name) >= 2:
        return (name[0][0] + name[-1][0]).upper()
    return user.get_username()[:2].upper()


@register.filter
def avatar_color(user):
    """A stable avatar colour per user."""
    return AVATAR_COLORS[(user.pk or 0) % len(AVATAR_COLORS)]


@register.filter
def form_control(field, css_class="form-control"):
    """Render a bound field's widget with a CoreUI class, marked invalid when it has errors."""
    attrs = {"class": css_class}
    if field.errors:
        attrs["class"] += " is-invalid"
        attrs["aria-invalid"] = "true"
        attrs["aria-describedby"] = f"{field.auto_id}-errors"
    elif field.help_text:
        attrs["aria-describedby"] = f"{field.auto_id}-help"
    return field.as_widget(attrs=attrs)


@register.filter
def message_alert(message):
    """Alert class and icon for a Django message; a custom level renders as info."""
    return MESSAGE_ALERTS.get(getattr(message, "level", None), MESSAGE_ALERTS[constants.INFO])


@register.simple_tag
def coreui_assets():
    """The edition and its asset URLs, for ``django_coreui/includes/assets.html`` (the only template to use it)."""
    return {
        "edition": coreui_settings()["edition"],
        "css": assets.COREUI_CSS,
        "css_sri": assets.COREUI_CSS_SRI,
        "js": assets.COREUI_JS,
        "js_sri": assets.COREUI_JS_SRI,
    }


# The layout settings a project may preset, with CoreUI's defaults, and the values layout-switch.js accepts.
COREUI_LAYOUT_DEFAULTS = {"theme": "auto", "sidebar": "default"}
COREUI_LAYOUT_VALUES = {
    "theme": ("light", "dark", "auto"),
    "sidebar": ("default", "narrow", "unfoldable"),
}


@register.simple_tag
def layout_defaults_attrs():
    """Attributes for <html> from the project's default layout (``django_coreui/includes/layout_defaults.html``).

    Each value that differs from CoreUI's default becomes ``data-coreui-<key>``: the server value layout-switch.js
    uses when the user has stored no choice (``data-coreui-theme`` is also CoreUI's own colour-mode attribute, so a
    dark default needs no script). ``data-coreui-layout-defaults`` hands the defaults to layout-switch.js. Renders
    nothing for the package's empty default.
    """
    raw = render_to_string("django_coreui/includes/layout_defaults.html").strip()
    try:
        defaults = json.loads(raw or "{}")
    except json.JSONDecodeError as error:
        raise ValueError(f"django_coreui/includes/layout_defaults.html is not JSON: {error}") from None
    if not isinstance(defaults, dict):
        raise ValueError("django_coreui/includes/layout_defaults.html must hold a JSON object")
    for key, value in defaults.items():
        if key not in COREUI_LAYOUT_VALUES or value not in COREUI_LAYOUT_VALUES[key]:
            raise ValueError(f"layout default {key!r}: {value!r} is not a CoreUI layout setting")
    if not defaults:
        return ""
    attrs = [format_html(' data-coreui-{}="{}"', k, v) for k, v in defaults.items() if v != COREUI_LAYOUT_DEFAULTS[k]]
    # Keys and values are from the fixed lists above, so the JSON needs no escaping inside the single quotes.
    attrs.append(mark_safe(f" data-coreui-layout-defaults='{json.dumps(defaults, separators=(',', ':'))}'"))
    return mark_safe("".join(attrs))
