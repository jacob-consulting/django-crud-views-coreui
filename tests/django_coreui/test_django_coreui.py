import json
import re
import subprocess
import sys
from pathlib import Path

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
        self.assertRegex(layout, r'<div class="col-12 col-md">\s*\{% block page_heading %\}')
        self.assertIn('<div class="col-auto ms-auto d-print-none">', layout)

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


def render_template_with(source: str, **context) -> str:
    return Template("{% load coreui %}" + source).render(Context(context))


def render_page(source: str = '{% extends "django_coreui/layouts/app.html" %}') -> str:
    user = User(pk=1, username="alex", first_name="Alex", last_name="Jacob")
    return Template(source).render(Context({"user": user, "messages": []}))


def render_login() -> str:
    return render_to_string("registration/login.html", {"form": AuthenticationForm(), "next": "/"})


BLOCKS = [
    "title",
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
        child = '{% extends "django_coreui/layouts/app.html" %}' + "".join(
            f"{{% block {name} %}}<i>probe-{name}</i>{{% endblock %}}" for name in BLOCKS
        )
        html = render_page(child)
        for name in BLOCKS:
            with self.subTest(block=name):
                self.assertEqual(html.count(f"probe-{name}"), 1)

    def test_page_heading_wraps_page_title(self):
        html = render_page('{% extends "django_coreui/layouts/app.html" %}{% block page_title %}Probe{% endblock %}')
        self.assertRegex(html, r"<h1[^>]*>Probe</h1>")

    def test_app_layout_is_coreuis_admin_layout(self):
        html = render_page()
        self.assertIn('class="sidebar sidebar-dark sidebar-fixed border-end" id="sidebar"', html)
        self.assertIn('<ul class="sidebar-nav" data-coreui="navigation">', html)
        self.assertIn('class="wrapper d-flex flex-column min-vh-100"', html)
        self.assertIn("coreui.Sidebar.getInstance(document.querySelector('#sidebar')).toggle()", html)
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
