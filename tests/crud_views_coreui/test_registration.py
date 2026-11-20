"""What CrudViewsCoreuiConfig.ready() registers: button classes, icons, assets, the W001 check, adapters and CSS."""

import re
from pathlib import Path

import crud_views
from crud_views.lib.assets import get_registered
from crud_views.lib.button_classes import get_button_classes
from crud_views.lib.icons import DEFAULT_ICONS, get_icons
from crud_views.lib.icons import render_icon as cv_render_icon
from django.core.checks import run_checks
from django.test import SimpleTestCase, TestCase, override_settings

import crud_views_coreui
from crud_views_coreui.buttons import COREUI_BUTTON_CLASSES
from crud_views_coreui.icons import COREUI_ICONS
from django_coreui.icons import ICONS, svg

STATIC = Path(crud_views_coreui.__file__).parent / "static" / "crud_views_coreui"
UPSTREAM_CSS = Path(crud_views.__file__).parent / "static" / "crud_views" / "css"

# Frozen copy of crud_views_tabler.buttons.TABLER_BUTTON_CLASSES' keys (tabler-test 7165eaf). The CoreUI theme covers
# exactly the keys the Tabler theme covers; when Tabler gains a key, add it here and in COREUI_BUTTON_CLASSES.
TABLER_BUTTON_KEYS = frozenset(
    {
        "alert:close",
        "alert:dismissible",
        "card-order:container",
        "card-order:toggle",
        "card:container",
        "card:danger",
        "card:danger:icon",
        "card:menu-toggle",
        "card:primary",
        "card:primary:icon",
        "card:root",
        "card:secondary",
        "card:secondary:icon",
        "card:tertiary",
        "card:tertiary:icon",
        "conditional:legend",
        "context:container",
        "context:danger",
        "context:danger:icon",
        "context:menu-toggle",
        "context:menu-wrapper",
        "context:primary",
        "context:primary:icon",
        "context:secondary",
        "context:secondary:icon",
        "context:tertiary",
        "context:tertiary:icon",
        "form:actions",
        "form:delete",
        "form:filter-actions",
        "formset:control",
        "formset:control-danger",
        "formset:legend",
        "list:container",
        "list:danger",
        "list:danger:icon",
        "list:menu-toggle",
        "list:menu-wrapper",
        "list:primary",
        "list:primary:icon",
        "list:secondary",
        "list:secondary:icon",
        "list:tertiary",
        "list:tertiary:icon",
        "manage:badge-group",
        "manage:badge-model",
        "manage:badge-objects",
        "manage:badge-permission",
        "manage:badge-policy-global",
        "manage:badge-policy-na",
        "manage:badge-policy-strict",
        "manage:badge-resource",
        "manage:help",
        "manage:trace-allowed",
        "manage:trace-denied",
        "manage:trace-error",
        "manage:trace-login-redirect",
        "manage:trace-no-such-route",
        "manage:trace-not-evaluated",
        "manage:trace-not-found",
        "manage:trace-not-reached",
        "manage:trace-passed",
        "manage:trace-skipped",
        "navbar:item",
        "navbar:link",
        "navbar:nav",
        "workflow:badge-danger",
        "workflow:badge-dark",
        "workflow:badge-info",
        "workflow:badge-light",
        "workflow:badge-primary",
        "workflow:badge-secondary",
        "workflow:badge-success",
        "workflow:badge-warning",
        "workflow:history-table",
        "workflow:transition-danger",
        "workflow:transition-dark",
        "workflow:transition-info",
        "workflow:transition-light",
        "workflow:transition-primary",
        "workflow:transition-secondary",
        "workflow:transition-success",
        "workflow:transition-warning",
    }
)

# Tabler-only classes that have no CoreUI counterpart and must not leak into the CoreUI table.
TABLER_ONLY = re.compile(
    r"(?<![\w-])(btn-icon|btn-list|nav-bordered|table-vcenter|badge-outline|bg-[a-z]+-lt)(?![\w-])"
)


class ButtonClassTests(SimpleTestCase):
    def test_button_keys_match_tabler(self):
        self.assertEqual(set(COREUI_BUTTON_CLASSES), TABLER_BUTTON_KEYS)

    def test_no_tabler_only_classes(self):
        leaks = {key: value for key, value in COREUI_BUTTON_CLASSES.items() if TABLER_ONLY.search(value)}
        self.assertEqual(leaks, {})

    def test_icon_keys_are_square(self):
        for key, value in COREUI_BUTTON_CLASSES.items():
            if key.endswith(":icon"):
                self.assertIn("cv-coreui-icon-btn", value.split(), key)

    def test_classes_are_registered(self):
        # crud_views_workflow is installed in the test settings, so the workflow:* keys are registered too.
        classes = get_button_classes()
        for key, value in COREUI_BUTTON_CLASSES.items():
            self.assertEqual(classes[key], value, key)


class IconTests(SimpleTestCase):
    def test_icon_keys_cover_crud_views_defaults(self):
        self.assertEqual(set(DEFAULT_ICONS) - set(COREUI_ICONS), set())

    def test_every_coreui_icon_has_an_svg(self):
        for key, value in COREUI_ICONS.items():
            prefix, name = value.split(":", 1)
            self.assertEqual(prefix, "coreui", key)
            self.assertIn(name, ICONS, key)

    def test_icons_are_registered(self):
        icons = get_icons()
        for key, value in COREUI_ICONS.items():
            self.assertEqual(icons[key], value, key)

    def test_renderer_is_django_coreui_svg(self):
        self.assertEqual(cv_render_icon("update"), svg("cil-pencil"))
        self.assertEqual(cv_render_icon("coreui:cil-people", css="me-2"), svg("cil-people", "me-2"))

    @override_settings(COREUI_ICON_ALIASES={"cil-pencil": "cil-trash"})
    def test_renderer_ignores_shell_aliases(self):
        # crud_views has its own semantic table (CRUD_VIEWS_ICONS); the shell's aliases are for {% icon %} only.
        self.assertEqual(cv_render_icon("update"), svg("cil-pencil"))


class IconCheckTests(TestCase):
    @override_settings(CRUD_VIEWS_ICONS={"detail": "coreui:cil-nope"})
    def test_w001_flags_missing_svg(self):
        messages = [m for m in run_checks() if m.id == "crud_views_coreui.W001"]
        self.assertEqual(len(messages), 1)
        self.assertIn("'detail'", messages[0].msg)
        self.assertIn("'coreui:cil-nope'", messages[0].msg)

    def test_w001_silent_by_default(self):
        self.assertEqual([m.id for m in run_checks() if m.id.startswith("crud_views_coreui.")], [])

    @override_settings(CRUD_VIEWS_ICONS={"detail": "far:eye", "person": "coreui:cil-user"})
    def test_w001_ignores_other_libraries(self):
        self.assertEqual([m.id for m in run_checks() if m.id.startswith("crud_views_coreui.")], [])

    @override_settings(
        CRUD_VIEWS_ICONS={"detail": "coreui:cil-nope"},
        CRUD_VIEWS_ICON_LIBRARIES={"coreui": {"renderer": "font", "class": "icon {name}"}},
    )
    def test_w001_silent_when_prefix_remapped(self):
        self.assertEqual([m.id for m in run_checks() if m.id.startswith("crud_views_coreui.")], [])


class AssetTests(SimpleTestCase):
    def test_assets_registered(self):
        bundles = {bundle.key: bundle for bundle in get_registered()}
        bundle = bundles["crud_views_coreui"]
        self.assertEqual([a.path for a in bundle.js], ["crud_views_coreui/coreui-adapters.js"])
        self.assertEqual([a.path for a in bundle.css], ["crud_views_coreui/crud_views_coreui.css"])
        self.assertTrue(bundle.emit)
        for asset in (*bundle.js, *bundle.css):
            self.assertTrue((STATIC.parent / asset.path).is_file(), asset.path)

    def test_css_maps_every_bs_variable_upstream_reads(self):
        upstream = "\n".join((UPSTREAM_CSS / name).read_text() for name in ("manage.css", "formset.css"))
        theme = (STATIC / "crud_views_coreui.css").read_text()
        names = set(re.findall(r"--bs-[a-z-]+", upstream))
        self.assertGreaterEqual(len(names), 8)  # 13 references to 8 properties at crud_views fa2f0a7b
        for name in sorted(names):
            if re.search(rf"var\({name}\b", upstream):
                # upstream reads it: the theme defines it from CoreUI's --cui-* counterpart
                self.assertRegex(theme, rf"{name}:\s*var\(--cui-{name[5:]}\)", name)
            else:
                # upstream only sets it (a Bootstrap component variable): the theme hands it to CoreUI's
                self.assertRegex(theme, rf"--cui-{name[5:]}:\s*var\({name}\)", name)

    def test_adapter_script_uses_coreui_namespace_and_wraps_tooltip_init(self):
        script = (STATIC / "coreui-adapters.js").read_text()
        self.assertIn("cv.bootstrapAdapters(() => globalThis.coreui)", script)
        self.assertIn("const init = cv.adapters.tooltip.init", script)
        self.assertIn("data-coreui-placement", script)
        self.assertNotIn("data-bs-", script)
        self.assertNotIn("cv.adapters.tooltip = ", script)  # wrap init, never replace the tooltip object
