"""django_coreui.icons: vendored CoreUI free icons, and scripts/vendor_icons.py that writes them."""

import importlib.util
import re
from pathlib import Path

from django.test import SimpleTestCase, override_settings

import django_coreui
from django_coreui import icons
from django_coreui.templatetags.coreui import MESSAGE_ALERTS

PACKAGE = Path(django_coreui.__file__).parent
ICONS_PY = PACKAGE / "icons.py"
SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "vendor_icons.py"

# The shell's own icons (brief, Task 4): colour mode, menus, alerts.
SHELL_ICONS = [
    "cil-sun",
    "cil-moon",
    "cil-contrast",
    "cil-settings",
    "cil-user",
    "cil-account-logout",
    "cil-menu",
    "cil-code",
    "cil-search",
    "cil-bug",
    "cil-info",
    "cil-check-circle",
    "cil-warning",
    "cil-x-circle",
]


def load_script():
    spec = importlib.util.spec_from_file_location("vendor_icons", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IconsTests(SimpleTestCase):
    def test_header_carries_the_attribution_and_version(self):
        header = ICONS_PY.read_text().split('"""', 2)[1]
        self.assertIn("CC BY 4.0", header)
        self.assertIn("@coreui/icons@3.1.0", header)
        self.assertIn("https://creativecommons.org/licenses/by/4.0/", header)

    def test_icons_are_sorted_free_names(self):
        self.assertEqual(list(icons.ICONS), sorted(icons.ICONS))
        for name, markup in icons.ICONS.items():
            with self.subTest(name=name):
                self.assertRegex(name, r"^cil-[a-z0-9-]+$")
                self.assertTrue(markup.startswith("<"), markup[:40])
                self.assertNotIn("<svg", markup)
                self.assertNotIn("<script", markup.lower())

    def test_shell_icons_are_vendored(self):
        for name in SHELL_ICONS:
            self.assertIn(name, icons.ICONS)

    def test_every_icon_the_templates_name_is_vendored(self):
        names = set()
        for path in (PACKAGE / "templates").rglob("*.html"):
            names |= set(re.findall(r'\{% icon "([^"]+)"', path.read_text()))
        names |= {alert["icon"] for alert in MESSAGE_ALERTS.values()}
        self.assertTrue(names)
        self.assertEqual(sorted(names - set(icons.ICONS)), [])

    def test_svg_markup(self):
        html = icons.svg("cil-sun", "icon-lg")
        self.assertTrue(
            html.startswith(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" aria-hidden="true" focusable="false" '
                'class="icon icon-lg">'
            ),
            html,
        )
        self.assertTrue(html.endswith(icons.ICONS["cil-sun"] + "</svg>"))
        self.assertIn('class="icon">', icons.svg("cil-sun"))

    def test_svg_is_empty_for_no_or_unknown_name(self):
        self.assertEqual(icons.svg(None), "")
        self.assertEqual(icons.svg(""), "")
        self.assertEqual(icons.svg("cil-nope"), "")

    def test_svg_escapes_the_css_class(self):
        self.assertIn('class="icon &quot;x"', icons.svg("cil-sun", '"x'))

    @override_settings(COREUI_ICON_ALIASES={"customer": "cil-people"})
    def test_resolve_applies_aliases(self):
        self.assertEqual(icons.resolve("customer"), "cil-people")
        self.assertEqual(icons.resolve("cil-sun"), "cil-sun")

    def test_resolve_without_aliases(self):
        self.assertEqual(icons.resolve("customer"), "customer")


class VendorScriptTests(SimpleTestCase):
    """The script merges into ICONS: it adds names and never drops one."""

    def test_names_are_normalised(self):
        script = load_script()
        self.assertEqual(script.normalise("cilPeople"), "cil-people")
        self.assertEqual(script.normalise("people"), "cil-people")
        self.assertEqual(script.normalise("cil-people"), "cil-people")
        self.assertEqual(script.normalise("cilCheckCircle"), "cil-check-circle")

    def test_parse_reads_the_esm_module(self):
        script = load_script()
        source = "var cilX = [\"512 512\", \"<path d='M0 0' class='ci-primary'/>\"];\n\nexport { cilX };\n"
        self.assertEqual(script.parse(source), "<path d='M0 0' class='ci-primary'/>")
        with self.assertRaises(ValueError):
            script.parse('var cilX = ["24 24", "<path/>"];')

    def test_merge_keeps_existing_names_and_sorts(self):
        script = load_script()
        merged = script.merge({"cil-b": "<b/>", "cil-a": "<a/>"}, {"cil-c": "<c/>", "cil-a": "<a2/>"})
        self.assertEqual(list(merged), ["cil-a", "cil-b", "cil-c"])
        self.assertEqual(merged["cil-a"], "<a2/>")

    def test_rewrite_round_trips_the_module(self):
        script = load_script()
        source = ICONS_PY.read_text()
        self.assertEqual(script.rewrite(source, script.read_icons(source)), source)

    def test_rewrite_adds_a_name(self):
        script = load_script()
        source = ICONS_PY.read_text()
        new = script.rewrite(source, script.merge(script.read_icons(source), {"cil-zzz": "<path d='M1 1'/>"}))
        self.assertIn("""    "cil-zzz": "<path d='M1 1'/>",\n}""", new)
        self.assertEqual(script.read_icons(new)["cil-zzz"], "<path d='M1 1'/>")
        self.assertEqual(len(script.read_icons(new)), len(icons.ICONS) + 1)
