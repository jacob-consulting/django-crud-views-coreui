import json
import re
import subprocess
import sys
from pathlib import Path

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.core.checks import run_checks
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import SimpleTestCase, override_settings
from django.utils.safestring import mark_safe

import django_coreui
from django_coreui.icons import svg

PACKAGE = Path(django_coreui.__file__).parent
TEMPLATES = PACKAGE / "templates"
INCLUDES = TEMPLATES / "django_coreui" / "includes"


def render_messages(*messages):
    return render_to_string("django_coreui/includes/messages.html", {"messages": list(messages)})


def strip_comments(source: str) -> str:
    return re.sub(r"\{#.*?#\}", "", source, flags=re.DOTALL).strip()


class MessagesIncludeTests(SimpleTestCase):
    def test_levels_map_to_alert_classes(self):
        for level, css in (
            (constants.ERROR, "alert alert-danger"),
            (constants.WARNING, "alert alert-warning"),
            (constants.SUCCESS, "alert alert-success"),
            (constants.INFO, "alert alert-info"),
            (constants.DEBUG, "alert alert-secondary"),
        ):
            with self.subTest(level=level):
                html = render_messages(Message(level, "x"))
                self.assertIn(css, html)
                self.assertIn("<svg", html)

    def test_custom_level_renders_as_info(self):
        self.assertIn("alert alert-info", render_messages(Message(35, "x")))

    def test_body_is_escaped_and_safe_strings_pass(self):
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", render_messages(Message(constants.INFO, "<b>x</b>")))
        self.assertIn("<b>x</b>", render_messages(Message(constants.INFO, mark_safe("<b>x</b>"))))

    def test_extra_tags_reach_the_alert(self):
        html = render_messages(Message(constants.INFO, "x", extra_tags="probe"))
        self.assertRegex(html, r'class="alert [^"]*\bprobe\b')

    def test_dismiss_uses_coreuis_data_attribute(self):
        self.assertIn('data-coreui-dismiss="alert"', render_messages(Message(constants.INFO, "x")))

    def test_markup_is_bootstraps_stock_alert(self):
        # The CoreUI theme's alerts use the same markup (its MessagesParityTests compare the two): icon with me-2, the
        # text right after it, the close button; no flex row or text wrapper.
        html = render_messages(Message(constants.SUCCESS, "Saved", extra_tags="probe"))
        normalized = re.sub(r">\s+<", "><", re.sub(r"\s+", " ", html)).strip()
        expected = (
            '<div class="alert alert-success alert-dismissible fade show probe" role="alert">'
            f"{svg('cil-check', 'me-2')}Saved "
            '<button type="button" class="btn-close" data-coreui-dismiss="alert" aria-label="Close"></button></div>'
        )
        self.assertEqual(normalized, expected)

    def test_level_icons(self):
        for level, name in (
            (constants.DEBUG, "cil-bug"),
            (constants.INFO, "cil-info"),
            (constants.SUCCESS, "cil-check"),
            (constants.WARNING, "cil-warning"),
            (constants.ERROR, "cil-x-circle"),
        ):
            with self.subTest(level=level):
                self.assertIn(str(svg(name, "me-2")), render_messages(Message(level, "x")))


WITHOUT_CRISPY = """
import sys
sys.modules["crispy_forms"] = None
sys.modules["crispy_bootstrap5"] = None

import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=["django_coreui"],
    TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}],
)
django.setup()

from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.template.loader import render_to_string

import django_coreui.templatetags.coreui

html = render_to_string("django_coreui/includes/messages.html", {"messages": [Message(constants.INFO, "x")]})
assert "alert-info" in html
"""


class PackageTests(SimpleTestCase):
    def test_package_works_without_crispy_installed(self):
        result = subprocess.run([sys.executable, "-c", WITHOUT_CRISPY], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_package_does_not_reference_crud_views(self):
        for path in PACKAGE.rglob("*"):
            if path.is_file() and path.name != "tests.py" and "__pycache__" not in path.parts:
                with self.subTest(path=path):
                    self.assertIsNone(re.search(r"crud[-_ ]views|cv_", path.read_text(), re.IGNORECASE))

    def test_default_site_name(self):
        self.assertEqual((INCLUDES / "site_name.html").read_text(), "Django CoreUI")

    def test_default_head_include_is_empty(self):
        self.assertEqual(strip_comments((INCLUDES / "head.html").read_text()), "")

    def test_default_nav_menu_is_empty(self):
        self.assertEqual((INCLUDES / "nav_menu.html").read_text().strip(), "")

    def test_default_layout_defaults_include_is_empty(self):
        self.assertEqual(strip_comments((INCLUDES / "layout_defaults.html").read_text()), "")

    def test_page_header_actions_wrap_below_the_title_on_phones(self):
        layout = (TEMPLATES / "django_coreui" / "layouts" / "app.html").read_text()
        self.assertRegex(
            layout,
            r'<div class="col-12 col-md">\s*<div class="page-pretitle[^"]*">'
            r"\{% block pretitle %\}\{% endblock %\}</div>\s*\{% block page_heading %\}",
        )
        self.assertIn('<div class="col-auto ms-auto d-print-none">', layout)

    def test_empty_breadcrumb_row_is_hidden(self):
        # .header > .container-fluid has a min-height, which the breadcrumb row would keep while empty. Not :empty:
        # whitespace defeats it, and crud_views' breadcrumb tag renders a newline for a view without a breadcrumb
        # (browser pass: a blank strip on the manage page).
        css = (PACKAGE / "static" / "django_coreui" / "django_coreui.css").read_text()
        self.assertRegex(css, r"\.header > \.header-breadcrumb:not\(:has\(\*\)\) \{\s*display: none;\s*\}")
        self.assertRegex(css, r"\.header > \.header-breadcrumb:has\(\*\) \{\s*display: flex;")
        self.assertNotIn(":empty", css)
        layout = (TEMPLATES / "django_coreui" / "layouts" / "app.html").read_text()
        self.assertIn('header-breadcrumb">{% block breadcrumb %}{% endblock %}</div>', layout)

    def test_nav_menu_is_included_once_inside_the_sidebar_nav(self):
        sidebar = (INCLUDES / "sidebar.html").read_text()
        self.assertRegex(
            sidebar,
            r'<ul class="sidebar-nav" data-coreui="navigation">\s*'
            r'(\{% with [^%]*%\})?\{% include "django_coreui/includes/nav_menu.html" %\}',
        )
        includes = [
            path
            for path in TEMPLATES.rglob("*.html")
            if "django_coreui/includes/nav_menu.html" in path.read_text() and path.name != "nav_menu.html"
        ]
        self.assertEqual(includes, [INCLUDES / "sidebar.html"])
        self.assertEqual(sidebar.count("nav_menu.html"), 1)


LAYOUT_SWITCH_JS = PACKAGE / "static" / "django_coreui" / "layout-switch.js"


def render_layout_attrs(defaults: str | None = None) -> str:
    """``{% layout_defaults_attrs %}`` with the package's include, or with ``defaults`` as the include's content."""
    if defaults is None:
        return Template("{% load coreui %}{% layout_defaults_attrs %}").render(Context())
    loaders = [
        ("django.template.loaders.locmem.Loader", {"django_coreui/includes/layout_defaults.html": defaults}),
        "django.template.loaders.app_directories.Loader",
    ]
    engine = {"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "OPTIONS": {"loaders": loaders}}
    with override_settings(TEMPLATES=[engine]):
        return Template("{% load coreui %}{% layout_defaults_attrs %}").render(Context())


class LayoutDefaultsTests(SimpleTestCase):
    """A project sets its default layout in django_coreui/includes/layout_defaults.html.

    The user's choice still wins.
    """

    def test_package_default_sets_nothing(self):
        self.assertEqual(render_layout_attrs(), "")
        self.assertEqual(render_layout_attrs((INCLUDES / "layout_defaults.html").read_text()), "")
        self.assertIn(
            '<html lang="en"{% layout_defaults_attrs %}>', (TEMPLATES / "django_coreui" / "base.html").read_text()
        )

    def test_project_defaults_become_server_values_and_a_json_attribute(self):
        html = render_layout_attrs('{"theme": "dark", "sidebar": "narrow"}')
        self.assertIn(' data-coreui-theme="dark"', html)
        self.assertIn(' data-coreui-sidebar="narrow"', html)
        match = re.search(r" data-coreui-layout-defaults='([^']*)'", html)
        self.assertIsNotNone(match, html)
        self.assertEqual(json.loads(match.group(1)), {"theme": "dark", "sidebar": "narrow"})

    def test_coreui_defaults_need_no_server_value(self):
        html = render_layout_attrs('{"theme": "auto", "sidebar": "default"}')
        self.assertNotIn("data-coreui-theme=", html)
        self.assertNotIn("data-coreui-sidebar=", html)
        self.assertIn(" data-coreui-layout-defaults='", html)

    def test_unknown_keys_and_odd_values_are_refused(self):
        for bad in (
            '{"navbar-position": "vertical"}',
            '{"theme": "sepia"}',
            '{"sidebar": "folded"}',
            '{"theme": "dark\\" onload=1"}',
            '{"theme": 1}',
            '["theme"]',
            "not json",
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                render_layout_attrs(bad)

    def test_switch_reads_the_project_defaults_and_keeps_coreuis_as_fallback(self):
        js = LAYOUT_SWITCH_JS.read_text()
        self.assertIn('const COREUI_DEFAULTS = { theme: "auto", sidebar: "default" };', js)
        self.assertIn("document.documentElement.dataset.coreuiLayoutDefaults", js)
        self.assertIn("const DEFAULTS = { ...COREUI_DEFAULTS, ...projectDefaults() };", js)
        # stored only when it differs from the project default
        self.assertRegex(js, r"if \(value === DEFAULTS\[key\]\) localStorage\.removeItem")
        # colour mode follows the operating system in auto, as the free admin template's color-modes.js
        self.assertIn("prefers-color-scheme: dark", js)
        self.assertIn("ColorSchemeChange", js)
        for name in ("sidebar-narrow", "sidebar-narrow-unfoldable"):
            self.assertIn(f'"{name}"', js)

    def test_switch_menu_offers_every_accepted_value(self):
        menu = (INCLUDES / "layout_switch_menu.html").read_text()
        settings = [json.loads(s) for s in re.findall(r"data-layout-settings='([^']*)'", menu)]
        self.assertCountEqual(
            settings,
            [{"theme": v} for v in ("light", "dark", "auto")]
            + [{"sidebar": v} for v in ("default", "narrow", "unfoldable")],
        )


def render_template(source: str) -> str:
    return Template(source).render(Context())


@override_settings(COREUI_ICON_ALIASES={"customer": "cil-people"})
class IconAliasTests(SimpleTestCase):
    def test_icon_alias(self):
        self.assertEqual(
            render_template('{% load coreui %}{% icon "customer" %}'),
            render_template('{% load coreui %}{% icon "cil-people" %}'),
        )
        self.assertIn("<svg", render_template('{% load coreui %}{% icon "customer" %}'))

    def test_unaliased_name_renders_directly(self):
        self.assertIn("<svg", render_template('{% load coreui %}{% icon "cil-sun" %}'))

    def test_alias_keeps_the_css_class(self):
        self.assertIn('class="icon icon-lg"', render_template('{% load coreui %}{% icon "customer" "icon-lg" %}'))

    def test_unknown_icon_renders_nothing(self):
        self.assertEqual(render_template('{% load coreui %}{% icon "cil-nope" %}'), "")
        self.assertEqual(render_template('{% load coreui %}{% icon "" %}'), "")


class FilterTests(SimpleTestCase):
    def test_initials_and_avatar_color(self):
        full = User(pk=3, username="alex", first_name="Alex", last_name="Jacob")
        self.assertEqual(render_template_with("{{ u|initials }}", u=full), "AJ")
        self.assertEqual(render_template_with("{{ u|initials }}", u=User(username="bob")), "BO")
        colour = render_template_with("{{ u|avatar_color }}", u=full)
        self.assertEqual(colour, render_template_with("{{ u|avatar_color }}", u=full))
        self.assertRegex(colour, r"^[a-z]+$")

    def test_form_control_marks_errors(self):
        form = AuthenticationForm(data={"username": "", "password": ""})
        form.is_valid()
        html = render_template_with("{{ f.username|form_control }}", f=form)
        self.assertIn('class="form-control is-invalid"', html)
        self.assertIn('aria-invalid="true"', html)


class _FieldForm(forms.Form):
    name = forms.CharField(help_text="Your <b>full</b> name.")
    nickname = forms.CharField(required=False)
    agree = forms.BooleanField(required=False, label="I agree", help_text="Optional.")


def render_field(form, name: str) -> str:
    return render_to_string("django_coreui/includes/field.html", {"field": form[name]})


class FieldIncludeTests(SimpleTestCase):
    """django_coreui/includes/field.html: one bound field in CoreUI's form markup, for hand-written forms."""

    def test_text_field_has_a_label_and_a_form_control(self):
        html = render_field(_FieldForm(), "nickname")
        self.assertRegex(
            html, r'<label class="form-label" for="id_nickname">Nickname</label>\s*<input [^>]*class="form-control"'
        )

    def test_required_field_is_marked(self):
        html = render_field(_FieldForm(), "name")
        self.assertRegex(
            html,
            r'<label class="form-label" for="id_name">Name'
            r'<span class="text-danger ms-1" aria-hidden="true">\*</span></label>',
        )
        self.assertNotIn("aria-hidden", render_field(_FieldForm(), "nickname"))

    def test_help_text_follows_the_input(self):
        html = render_field(_FieldForm(), "name")
        self.assertIn('<div class="form-text" id="id_name-help">Your <b>full</b> name.</div>', html)

    def test_errors_mark_the_input_and_replace_the_help_text(self):
        form = _FieldForm(data={})
        form.is_valid()
        html = render_field(form, "name")
        self.assertIn('class="form-control is-invalid"', html)
        self.assertIn('<div class="invalid-feedback d-block" id="id_name-errors">This field is required.</div>', html)
        self.assertNotIn("form-text", html)

    def test_checkbox_is_a_form_check(self):
        html = render_field(_FieldForm(), "agree")
        self.assertRegex(
            html,
            r'<div class="form-check">\s*<input type="checkbox" [^>]*class="form-check-input"[^>]*>\s*'
            r'<label class="form-check-label" for="id_agree">I agree</label>',
        )
        self.assertIn('<div class="form-text" id="id_agree-help">Optional.</div>', html)


def render_template_with(source: str, **context) -> str:
    return Template("{% load coreui %}" + source).render(Context(context))


def render_page(source: str = '{% extends "django_coreui/layouts/app.html" %}') -> str:
    user = User(pk=1, username="alex", first_name="Alex", last_name="Jacob")
    return Template(source).render(Context({"user": user, "messages": []}))


def render_login() -> str:
    return render_to_string("registration/login.html", {"form": AuthenticationForm(), "next": "/"})


# Every block of django_tabler's layouts/app.html and base.html.
BLOCKS = [
    "title",
    "body",
    "pretitle",
    "page_title",
    "extra_head",
    "page_header_before",
    "page_header_top",
    "breadcrumb",
    "page_heading",
    "subtitle",
    "actions",
    "messages",
    "content",
    "extra_js",
]


class LayoutTests(SimpleTestCase):
    def test_assets_pin_version_and_sri(self):
        html = render_to_string("django_coreui/base.html")
        self.assertIn("https://cdn.jsdelivr.net/npm/@coreui/coreui@5.9.1/dist/css/coreui.min.css", html)
        self.assertIn("https://cdn.jsdelivr.net/npm/@coreui/coreui@5.9.1/dist/js/coreui.bundle.min.js", html)
        self.assertEqual(html.count('integrity="sha384-'), 2)
        self.assertEqual(html.count('crossorigin="anonymous"'), 2)

    def test_only_the_assets_include_names_coreuis_cdn(self):
        for path in TEMPLATES.rglob("*.html"):
            if path.name != "assets.html":
                with self.subTest(path=path):
                    self.assertNotIn("cdn.jsdelivr.net", path.read_text())
                    self.assertNotIn("edition", path.read_text())

    @override_settings(COREUI={"edition": "pro"})
    def test_unknown_edition_is_an_error(self):
        self.assertIn("django_coreui.E001", [message.id for message in run_checks()])

    def test_free_edition_passes_the_check(self):
        for value in ({"edition": "free"}, {}):
            with self.subTest(value=value), override_settings(COREUI=value):
                self.assertNotIn("django_coreui.E001", [message.id for message in run_checks()])

    def test_layout_has_the_tabler_block_contract(self):
        # One block at a time: body, page_heading and page_title enclose others.
        for name in BLOCKS:
            with self.subTest(block=name):
                block = f"{{% block {name} %}}<i>probe-{name}</i>{{% endblock %}}"
                html = render_page('{% extends "django_coreui/layouts/app.html" %}' + block)
                self.assertEqual(html.count(f"probe-{name}"), 1)

    def test_every_other_block_fills_at_once(self):
        nested = {"body", "page_title"}  # body replaces the layout; page_heading replaces page_title
        child = '{% extends "django_coreui/layouts/app.html" %}' + "".join(
            f"{{% block {name} %}}<i>probe-{name}</i>{{% endblock %}}" for name in BLOCKS if name not in nested
        )
        html = render_page(child)
        for name in BLOCKS:
            if name not in nested:
                with self.subTest(block=name):
                    self.assertEqual(html.count(f"probe-{name}"), 1)

    def test_pretitle_sits_above_the_heading_and_is_empty_safe(self):
        html = render_page(
            '{% extends "django_coreui/layouts/app.html" %}{% block pretitle %}Overview{% endblock %}'
            "{% block page_title %}Orders{% endblock %}"
        )
        self.assertRegex(html, r'<div class="page-pretitle[^"]*">Overview</div>\s*<h1[^>]*>Orders</h1>')
        self.assertIn('<div class="page-pretitle small text-body-secondary"></div>', render_page())

    def test_no_inline_event_handlers(self):
        for name, html in (("app.html", render_page()), ("login.html", render_login())):
            with self.subTest(name=name):
                self.assertIsNone(re.search(r"\son[a-z]+\s*=", html), name)
        for path in TEMPLATES.rglob("*.html"):
            with self.subTest(path=path):
                self.assertIsNone(re.search(r"\son[a-z]+\s*=", path.read_text()))

    def test_header_toggler_is_wired_by_layout_switch(self):
        self.assertIn('class="header-toggler" type="button" data-sidebar-toggle="#sidebar"', render_page())
        js = LAYOUT_SWITCH_JS.read_text()
        self.assertIn('event.target.closest("[data-sidebar-toggle]")', js)
        self.assertIn("coreui.Sidebar.getOrCreateInstance(", js)

    def test_footer_version_comes_from_assets(self):
        from django_coreui.assets import COREUI_VERSION

        self.assertIn(f"CoreUI</a> {COREUI_VERSION}", render_page())
        self.assertNotIn("5.9.1", (TEMPLATES / "django_coreui" / "layouts" / "app.html").read_text())

    def test_page_heading_wraps_page_title(self):
        html = render_page('{% extends "django_coreui/layouts/app.html" %}{% block page_title %}Probe{% endblock %}')
        self.assertRegex(html, r"<h1[^>]*>Probe</h1>")

    def test_app_layout_is_coreuis_admin_layout(self):
        html = render_page()
        self.assertIn('class="sidebar sidebar-dark sidebar-fixed border-end" id="sidebar"', html)
        self.assertIn('<ul class="sidebar-nav" data-coreui="navigation">', html)
        self.assertIn('class="wrapper d-flex flex-column min-vh-100"', html)
        self.assertIn('data-coreui-toggle="unfoldable"', html)
        self.assertIn('class="footer', html)
        self.assertIn(">AJ<", html)  # the user menu's avatar
        self.assertIn('action="/logout/"', html)

    def test_layout_switch_script_is_on_every_page(self):
        for html in (render_page(), render_login()):
            self.assertIn('src="/static/django_coreui/layout-switch.js"', html)

    def test_no_data_bs_attributes(self):
        for name, html in (("app.html", render_page()), ("login.html", render_login())):
            with self.subTest(name=name):
                self.assertNotIn("data-bs-", html)
        for path in PACKAGE.rglob("*"):
            if path.is_file() and path.suffix in (".html", ".js", ".css"):
                with self.subTest(path=path):
                    self.assertNotIn("data-bs-", path.read_text())

    def test_login_page(self):
        html = render_login()
        self.assertIn("<title>Sign in · Django CoreUI</title>", html)
        self.assertIn('action="/login/"', html)
        self.assertIn('name="username"', html)
        self.assertIn('class="form-control"', html)
        self.assertIn('id="toggle-password"', html)
        self.assertNotIn('id="sidebar"', html)
