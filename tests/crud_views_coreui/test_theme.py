"""The CoreUI theme rendered: page.html, the layout overrides, the data-coreui overrides and the stock templates.

Ported from the Tabler theme's tests/crud_views_tabler/test_theme.py (tabler-test, branch semantic-icons) with CoreUI
expectations. What ready() registers (classes, icons, assets, W001, adapter script, CSS tokens) is in
test_registration.py; the Tabler tests that only covered that are not repeated here.
"""

import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import crud_views
import crud_views_object_detail
from crud_views.lib.assets import get_registered
from crud_views.lib.button_classes import _get_default_button_classes, get_button_classes
from crud_views.lib.crispy import CrispyDeleteForm
from crud_views.lib.icons import render_icon as cv_render_icon
from crud_views.lib.settings import crud_views_settings
from crud_views.lib.view.label_mode import LABEL_MODES
from crud_views.lib.view.variant import VARIANTS
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.template import Context, Template, engines
from django.template.loader import get_template, render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

import crud_views_coreui
from crud_views_coreui.buttons import COREUI_BUTTON_CLASSES
from crud_views_coreui.icons import COREUI_ICONS, render
from django_coreui.icons import ICONS, svg
from tests.crud_views_coreui.testapp.models import Customer
from tests.crud_views_coreui.testapp.views import CustomerDeleteView, CustomerListView, cv_customer

THEME = Path(crud_views_coreui.__file__).resolve().parent
THEME_CSS = THEME / "static/crud_views_coreui/crud_views_coreui.css"
UPSTREAM_COMMIT = "fa2f0a7b"

# What the theme's table.thead adds to upstream's <th> (tracker U10), as Tabler's table header does.
ARIA_SORT = (
    '{% if column.orderable %} aria-sort="{% if column.is_ordered %}{% if column.order_by_alias.is_descending %}'
    'descending{% else %}ascending{% endif %}{% else %}none{% endif %}"{% endif %}'
)

# The four templates the theme copies only to rename data-bs- to data-coreui- (upstream tracker U1). Each is the
# upstream file with that one change and a first-line comment naming its origin; test_data_bs_overrides_track_upstream
# fails as soon as upstream edits one, so the copy is refreshed (or dropped, once upstream has a prefix hook).
DATA_BS_OVERRIDES = {
    "crud_views/tags/actions_menu_toggle.html": crud_views,
    "crud_views/snippets/language_selector.html": crud_views,
    "crud_views_object_detail/layouts/tabs-vertical/object_detail.html": crud_views_object_detail,
    "crud_views_object_detail/layouts/accordion/group.html": crud_views_object_detail,
}


def icon_paths(name):
    """The d attributes of a CoreUI icon's paths, in order."""
    return re.findall(r"\bd='([^']*)'", ICONS[name])


def coreui_name(semantic):
    return COREUI_ICONS[semantic].split(":", 1)[1]


class ProbeWidget(forms.TextInput):
    class Media:
        js = ("probe/probe.js",)
        css = {"all": ("probe/probe.css",)}


class ProbeForm(forms.Form):
    x = forms.CharField(widget=ProbeWidget)


class IconRenderTests(SimpleTestCase):
    def test_unknown_or_empty_name_renders_nothing(self):
        self.assertEqual(svg("not-an-icon"), "")
        self.assertEqual(svg(None), "")
        self.assertEqual(render("not-an-icon", css="", config={}), "")

    def test_css_is_escaped(self):
        self.assertIn('class="icon a&quot; onload=&quot;x"', svg("cil-pencil", 'a" onload="x'))

    def test_renderer_matches_svg(self):
        self.assertEqual(render("cil-trash", css="me-2", config={"renderer": "x"}), svg("cil-trash", "me-2"))

    @override_settings(CRUD_VIEWS_ICONS={"detail": "far:eye"})
    def test_project_setting_wins_over_the_theme(self):
        self.assertEqual(cv_render_icon("detail"), '<i class="fa-regular fa-eye" aria-hidden="true"></i>')


class ButtonClassTests(SimpleTestCase):
    def test_every_theme_key_is_an_upstream_key(self):
        # A label-mode key (location:variant:mode, #209) extends an upstream action key.
        for key in COREUI_BUTTON_CLASSES:
            base, _, mode = key.rpartition(":") if key.count(":") == 2 else (key, "", "")
            self.assertIn(base, _get_default_button_classes(), key)
            if mode:
                self.assertIn(mode, LABEL_MODES, key)

    def test_square_class_only_on_icon_only_buttons(self):
        # cv-coreui-icon-btn squares a button; a labelled button (label or both) must not get it.
        for key, classes in COREUI_BUTTON_CLASSES.items():
            if key.split(":")[0] in ("context", "list", "card") and key.split(":")[1] in VARIANTS:
                self.assertEqual("cv-coreui-icon-btn" in classes.split(), key.endswith(":icon"), key)

    @override_settings(CRUD_VIEWS_BUTTON_CLASSES={"list:danger": "x-danger"})
    def test_project_setting_wins_over_the_theme_classes(self):
        self.assertEqual(get_button_classes()["list:danger"], "x-danger")


class ThemeRenderingTests(TestCase):
    """Renders the test app's customers ViewSet through the theme's templates."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser("root", "root@example.com", "s3cret-pass")
        Customer.objects.bulk_create(Customer(name=f"Customer {i:02}", revenue=i) for i in range(15))
        cls.customer = Customer.objects.get(name="Customer 03")

    def setUp(self):
        self.client.force_login(self.admin)

    @staticmethod
    def tag(html, key):
        """The first opening <a> or <button> tag with cv-key=key."""
        return re.search(rf'<(?:a|button)\b[^>]*\bcv-key="{key}"[^>]*>', html).group(0)

    @staticmethod
    def page_header(html):
        return html[html.index('class="page-header') : html.index("<main>")]

    @staticmethod
    def header_row(html):
        """The sticky CoreUI header (top row and breadcrumb row)."""
        return html[html.index("<header") : html.index("</header>")]

    def list_html(self, **params):
        return self.client.get(reverse("customer-list"), params).content.decode()

    def detail_html(self):
        return self.client.get(reverse("customer-detail", kwargs={"pk": self.customer.pk})).content.decode()

    def test_system_checks_pass(self):
        call_command("check", "--fail-level", "WARNING")

    def test_page_extends_the_coreui_layout(self):
        html = self.list_html()
        self.assertIn('class="sidebar sidebar-dark sidebar-fixed', html)
        self.assertIn('<div class="wrapper d-flex flex-column min-vh-100">', html)
        self.assertIn('class="page-header mb-4 d-print-none"', html)

    def test_theme_css_loads_after_coreui_css(self):
        # Theme rules tie CoreUI's on specificity (badges, the square icon button), so the later stylesheet must win.
        html = self.list_html()
        coreui = html.index("/dist/css/coreui.min.css")
        theme = html.index("crud_views_coreui/crud_views_coreui.css")
        self.assertLess(coreui, theme)
        self.assertLess(html.index("crud_views/css/"), theme)  # after crud_views' own CSS too

    # Breadcrumb: CoreUI's layout has its own row for it, the header's second row, on every page.
    def test_breadcrumb_renders_once_in_the_header_row(self):
        for html in (self.list_html(), self.detail_html()):
            header = self.header_row(html)
            self.assertEqual(html.count('<ol class="breadcrumb'), 1)
            self.assertRegex(
                header, r'<div class="container-fluid px-4 header-breadcrumb">\s*<nav aria-label="breadcrumb">'
            )
            self.assertNotIn('class="breadcrumb', self.page_header(html))

    def test_header_breadcrumb_has_no_bottom_margin(self):
        # CoreUI's .breadcrumb keeps a 1rem bottom margin, which the free template drops in the header (my-0);
        # upstream's breadcrumb has no class key (tracker U9), so the theme CSS sets CoreUI's variable.
        css = THEME_CSS.read_text()
        self.assertRegex(css, r"\.header-breadcrumb \.breadcrumb \{\s*--cui-breadcrumb-margin-bottom: 0;")

    # ViewSet Navigation (PR #383): the owner header at the top of the page header, the view's title row below the tabs
    def test_bar_page_builds_the_owner_header(self):
        html = self.detail_html()
        header = self.page_header(html)
        order = [
            header.index("<h1"),
            header.index('class="cv-coreui-navbar'),
            header.index("<h2"),
            header.index('cv-key="update"'),
        ]
        self.assertEqual(order, sorted(order))
        self.assertRegex(header, r'<h1 class="page-title[^"]*">\s*Customer 03\s*</h1>')
        self.assertNotIn('class="cv-navbar ', html)  # the full wrapper tag is not used
        self.assertIn('aria-label="Sections for Customer 03"', header)
        # Upstream #384's navbar:* keys: CoreUI's underline tabs instead of the stock pills
        self.assertIn('<ul class="nav nav-underline-border flex-wrap row-gap-1">', header)
        sections = header[header.index('<nav aria-label="Sections') :]
        sections = sections[: sections.index("</nav>")]
        self.assertGreater(sections.count("<li "), 1)
        self.assertEqual(sections.count('<li class="nav-item mw-100">'), sections.count("<li "))
        self.assertNotIn("nav-pills", header)
        self.assertRegex(
            header,
            r'class="nav-link d-flex align-items-center mw-100 text-break gap-2 active" '
            r'href="[^"]+" aria-current="true"',
        )

    def test_project_setting_overrides_the_navbar_keys(self):
        with override_settings(CRUD_VIEWS_BUTTON_CLASSES={"navbar:nav": "nav nav-tabs"}):
            html = self.detail_html()
        self.assertIn('<ul class="nav nav-tabs">', html)

    def test_bar_page_title_names_the_owner(self):
        self.assertRegex(self.detail_html(), r"<title>[^<]*· Customer 03 · ")

    def test_owner_icon_is_a_coreui_svg(self):
        header = self.page_header(self.detail_html())
        owner = header[header.index('class="avatar') : header.index("</h1>")]
        tabs_start = header.index('class="cv-coreui-navbar')
        tabs = header[tabs_start : header.index("</nav>", tabs_start)]
        self.assertIn(str(svg("cil-building")), owner)
        self.assertIn("<svg", tabs)
        self.assertNotIn("fa-", owner + tabs)

    def test_emptying_the_navbar_block_drops_only_the_tabs(self):
        # a project drops the tabs by overriding the cv_navbar block; the owner row stays
        response = self.client.get(reverse("customer-detail", kwargs={"pk": self.customer.pk}))
        source = '{% extends "crud_views_coreui/page.html" %}{% block cv_navbar %}{% endblock %}'
        html = engines["django"].from_string(source).render(response.context_data, response.wsgi_request)
        self.assertNotIn("cv-coreui-navbar", html)
        self.assertNotIn('<nav aria-label="Sections', html)
        self.assertIn('<h1 class="page-title', html)

    def test_page_without_navbar_keeps_the_plain_header(self):
        html = self.list_html()
        self.assertNotIn("cv-coreui-navbar", html)
        self.assertNotIn("cv-coreui-owner", html)
        header = self.page_header(html)
        self.assertNotIn("<h1", header)
        self.assertRegex(header, r'<h2 class="h3 page-title mb-0">')

    def test_list_uses_coreui_card_table_and_icons(self):
        html = self.list_html()
        self.assertRegex(html, r'<div class="card cv-coreui-table">\s*<div class="table-container">')
        self.assertRegex(html, r'<div class="table-responsive">\s*<table class="table">')
        self.assertIn('cv-key="delete"', html)
        self.assertIn("btn-ghost-danger", html)
        self.assertNotIn("fa-regular", html)
        self.assertNotIn("fa-solid", html)
        self.assertNotIn("<i class=", html)  # every icon on the page is a CoreUI SVG
        self.assertIn(str(svg("cil-building")), html)  # the ViewSet header icon, coreui:cil-building

    def test_table_override_extends_the_stock_table(self):
        # The theme adds the card, the responsive wrapper and aria-sort; rows, sorting and pagination stay upstream's.
        source = (THEME / "templates/crud_views/table/bootstrap5.html").read_text()
        self.assertIn('{% extends "crud_views/table/bootstrap5.html" %}', source)
        self.assertIn("{{ block.super }}", source)
        self.assertNotIn("<table", source)
        self.assertNotIn("page-item", source)

    def test_table_pagination_sits_in_the_card_footer(self):
        html = self.list_html()
        footer = html[html.index('<div class="card-footer">') :][:3000]
        self.assertIn('<nav aria-label="pagination">', footer)
        self.assertLess(html.index("</table>"), html.index('<div class="card-footer">'))

    def test_single_page_table_has_no_empty_footer(self):
        html = self.list_html(name="Customer 03")
        self.assertIn("Customer 03", html)
        self.assertNotIn('class="pagination', html)
        self.assertNotIn('<div class="card-footer">', html)

    def test_table_pagination_uses_the_semantic_arrows(self):
        html = self.list_html()
        footer = html[html.index('class="pagination') :]
        self.assertIn(str(svg("cil-chevron-right")), footer[:2000])
        with override_settings(CRUD_VIEWS_ICONS={"page-next": "coreui:cil-arrow-left"}):
            html = self.list_html()
        self.assertIn(str(svg("cil-arrow-left")), html[html.index('class="pagination') :][:2000])

    def test_table_pagination_matches_upstream_accessibility(self):
        # upstream Phase 05 (pagination parity): a labelled <nav> landmark, the current page as a non-link, the
        # ellipsis disabled; the hidden labels use the pagination:hidden-label class key
        page = self.list_html()
        nav = re.search(r'<nav aria-label="pagination">.*?</nav>', page, re.S).group(0)
        self.assertRegex(nav, r'<li class="page-item active" aria-current="page"><span class="page-link">1</span>')
        self.assertIn('<span class="visually-hidden">next</span>', nav)
        self.assertNotRegex(nav, r'<a class="page-link"\s*>')  # every link-less item says it is disabled

    def test_disabled_action_renders_a_coreui_icon(self):
        viewer = get_user_model().objects.create_user("viewer", password="viewer-pass")
        viewer.user_permissions.add(Permission.objects.get(codename="view_customer", content_type__app_label="testapp"))
        self.client.force_login(viewer)
        with mock.patch.object(CustomerDeleteView, "cv_inaccessible_actions", "disable"):
            html = self.list_html()
        button = re.search(r'<button[^>]*data-cv-disabled="permission"[^>]*>.*?</button>', html, re.S)
        self.assertIsNotNone(button)
        self.assertIn(f'class="{COREUI_BUTTON_CLASSES["list:danger:icon"]}"', button.group(0))
        self.assertIn(str(svg("cil-trash")), button.group(0))
        self.assertNotIn("<i class=", button.group(0))

    def test_sorted_column_is_marked(self):
        # The stock header marks the sorted column with the table-sort-* icon; the theme's table.thead adds aria-sort,
        # which the stock header lacks (tracker U10), so screen readers get the sort state too.
        html = self.list_html(sort="-revenue")
        revenue = re.search(r'<th class="[^"]*\btext-end" scope="col" aria-sort="[a-z]+">.*?</th>', html, re.S)
        self.assertIn('aria-sort="descending"', revenue.group(0))
        self.assertIn(str(svg(coreui_name("table-sort-desc"))), revenue.group(0))
        self.assertLess(html.index("Customer 14"), html.index("Customer 13"))

    def test_every_orderable_header_has_aria_sort(self):
        html = self.list_html(sort="name")
        thead = html[html.index("<thead") : html.index("</thead>")]
        headers = re.findall(r"<th\b[^>]*>", thead)
        self.assertGreater(len(headers), 3)
        for th in headers:
            self.assertEqual("orderable" in th, "aria-sort=" in th, th)
        self.assertEqual(thead.count('aria-sort="ascending"'), 1)
        self.assertNotIn('aria-sort="descending"', thead)
        self.assertGreater(thead.count('aria-sort="none"'), 1)

    def test_table_head_is_upstream_plus_aria_sort(self):
        # The theme's table.thead block is a copy (blocks cannot add an attribute to upstream's <th>); it must equal
        # the installed upstream block with only the aria-sort attribute added. Fails when upstream changes the header.
        def head(source):
            return re.search(r"\{% block table\.thead %\}.*?\{% endblock table\.thead %\}", source, re.S).group(0)

        upstream = (
            Path(crud_views.__file__).resolve().parent / "templates/crud_views/table/bootstrap5.html"
        ).read_text()
        theme = (THEME / "templates/crud_views/table/bootstrap5.html").read_text()
        self.assertEqual(head(theme).replace(ARIA_SORT, ""), head(upstream))
        self.assertEqual(head(theme).count(ARIA_SORT), 1)
        self.assertNotIn("aria-sort", upstream)  # the copy exists only while upstream has no aria-sort

    def test_scripts_use_the_coreui_adapter_without_jquery(self):
        html = self.list_html()
        self.assertNotIn("jquery", html.lower())
        self.assertNotIn("bootstrap-shim", html)
        bundle = html.index("/dist/js/coreui.bundle.min.js")
        core = html.index("crud_views/js/adapters.js")
        theme = html.index("crud_views_coreui/coreui-adapters.js")
        tabs = html.index("crud_views_coreui/coreui-tabs.js")
        self.assertLess(bundle, core)
        self.assertLess(core, theme)
        self.assertLess(theme, tabs)
        self.assertIn("crud_views/js/modal.js", html)

    def test_tooltip_adapter_places_toolbar_tooltips_below(self):
        with open(finders.find("crud_views_coreui/coreui-adapters.js"), encoding="utf-8") as f:
            source = f.read()
        self.assertIn('location === "context"', source)
        self.assertIn('setAttribute("data-coreui-placement", "bottom")', source)

    def test_upstream_adapter_set_includes_tab_and_theme_takes_all_of_it(self):
        # crud_views/js/adapters.js's bootstrapAdapters returns a `tab:` entry using component(ns, "Tab"), which
        # the object-detail tab init uses (#328); the theme assigns the whole set, so no tab adapter of its own.
        with open(finders.find("crud_views/js/adapters.js"), encoding="utf-8") as f:
            core = f.read()
        self.assertRegex(core, r'tab: \{\s*init\(el\) \{ component\(ns, "Tab"\)')
        with open(finders.find("crud_views_coreui/coreui-adapters.js"), encoding="utf-8") as f:
            source = f.read()
        self.assertIn("Object.assign(cv.adapters, cv.bootstrapAdapters(() => globalThis.coreui))", source)
        self.assertNotRegex(source, r"cv\.adapters\.tab\b")

    def test_tooltip_adapter_keeps_upstream_lifecycle(self):
        # Only init is replaced, so crud_views' hide(el) / dispose(el) (#205) keep resolving coreui.Tooltip.
        with open(finders.find("crud_views_coreui/coreui-adapters.js"), encoding="utf-8") as f:
            source = f.read()
        self.assertIn("init(el, options);", source)
        self.assertNotIn("getOrCreateInstance", source)
        self.assertNotIn("cv.adapters.tooltip.hide", source)
        self.assertNotIn("cv.adapters.tooltip.dispose", source)
        with open(finders.find("crud_views/js/adapters.js"), encoding="utf-8") as f:
            core = f.read()
        self.assertIn("hide(el)", core)
        self.assertIn("dispose(el)", core)

    def test_form_page_wraps_form_in_card(self):
        html = self.client.get(reverse("customer-create")).content.decode()
        self.assertRegex(html, r'<div class="card"><div class="card-body">\s*<form class="cv-form"')

    def test_modal_form_has_no_card(self):
        html = self.client.get(reverse("customer-create"), headers={"X-CV-Modal": "true"}).content.decode()
        self.assertIn('class="cv-form"', html)
        self.assertNotIn('<div class="card">', html)

    def test_form_pages_frame_through_upstream_content_templates(self):
        # upstream #239: the theme overrides only the frame, not the form templates; the frame extends upstream's
        self.assertEqual(
            Path(get_template("crud_views/snippets/form_frame.html").origin.name),
            THEME / "templates/crud_views/snippets/form_frame.html",
        )
        source = (THEME / "templates/crud_views/snippets/form_frame.html").read_text()
        self.assertIn('{% extends "crud_views/snippets/form_frame.html" %}', source)
        for name in ("view_create", "view_update", "view_delete", "view_custom_form"):
            template = f"crud_views/{name}.content.html"
            self.assertNotIn("crud_views_coreui", get_template(template).origin.name, template)

    def test_alerts_render_through_the_upstream_frame(self):
        # upstream #250: every alert renders through tags/alert.html; stock Bootstrap alert markup is CoreUI's too
        for name in (
            "tags/alert.html",
            "tags/messages.html",
            "snippets/delete/protection_errors.html",
            "snippets/delete/related_objects.html",
            "snippets/alert/text.html",
            "snippets/alert/list.html",
        ):
            self.assertNotIn("crud_views_coreui", get_template(f"crud_views/{name}").origin.name, name)

    def test_protection_errors_render_as_coreui_alert(self):
        html = render_to_string(
            "crud_views/snippets/delete/protection_errors.html", {"delete_protection_errors": ["Has open orders"]}
        )
        self.assertIn('class="alert alert-danger"', html)
        self.assertIn(str(svg(coreui_name("message-error"), "me-2")), html)
        self.assertIn("<strong>This object cannot be deleted:</strong>", html)
        self.assertRegex(html, r"<ul[^>]*>\s*<li>Has open orders</li>")
        self.assertNotIn("btn-close", html)

    def test_related_objects_alerts_get_coreui_icons(self):
        html = render_to_string(
            "crud_views/snippets/delete/related_objects.html",
            {
                "has_protected_objects": True,
                "protected_objects": ["Order 7"],
                "related_summary": {"order": 2},
                "related_summary_items": ["order: 2"],
                "related_objects": [],
            },
        )
        self.assertEqual(html.count('role="alert"'), 2)
        self.assertNotIn("Details about the related objects to be deleted:", html)
        self.assertIn(str(svg(coreui_name("message-warning"), "me-2")), html)  # warning
        self.assertIn(str(svg(coreui_name("message-error"), "me-2")), html)
        self.assertIn("<li>order: 2</li>", html)

    def test_create_and_update_post_multipart(self):
        # upstream #236: without the enctype a FileField arrives empty
        for url in (reverse("customer-create"), reverse("customer-update", args=[self.customer.pk])):
            html = self.client.get(url).content.decode()
            form = re.search(r'<form class="cv-form"[^>]*>', html).group(0)
            self.assertIn('enctype="multipart/form-data"', form, url)

    def test_create_and_update_emit_widget_media_once(self):
        # upstream #191: crispy already renders form.media; the content template must not add it again
        request = RequestFactory().get("/")
        for template in ("crud_views/view_create.content.html", "crud_views/view_update.content.html"):
            html = render_to_string(template, {"form": ProbeForm(), "request": request, "view": None}, request=request)
            self.assertEqual(html.count("probe/probe.js"), 1, template)
            self.assertEqual(html.count("probe/probe.css"), 1, template)

    def test_messages_render_as_coreui_alerts(self):
        url = reverse("customer-delete", args=[self.customer.pk])
        html = self.client.post(url, {"confirm": "on", "delete": "Delete"}, follow=True).content.decode()
        alert = re.search(r'<div class="alert alert-success[^"]*"\s+role="alert">.*?</div>', html, re.S).group(0)
        self.assertIn("alert-dismissible fade show", alert)
        self.assertIn(str(svg(coreui_name("message-success"), "me-2")), alert)
        self.assertIn("Deleted »Customer 03«", alert)
        self.assertIn('class="btn-close" data-cv-alert-dismiss', alert)
        self.assertNotIn("data-coreui-dismiss", alert)  # crud_views dismisses through cv.adapters.alert

    def test_delete_modal_partial_has_no_card_and_a_danger_button(self):
        url = reverse("customer-delete", args=[self.customer.pk])
        html = self.client.get(url, headers={"X-CV-Modal": "true"}).content.decode()
        self.assertIn('class="modal-header"', html)
        self.assertNotIn('<div class="card">', html)
        self.assertIn("btn btn-danger", html)
        self.assertIn("data-cv-modal-dismiss", html)
        self.assertNotIn("data-bs-dismiss", html)

    def test_delete_form_is_the_stock_crispy_delete_form(self):
        self.assertIs(CustomerDeleteView.form_class, CrispyDeleteForm)
        html = self.client.get(reverse("customer-delete", args=[self.customer.pk])).content.decode()
        self.assertRegex(html, r'<button type="submit" name="delete"[^>]*class="btn btn-danger"')
        self.assertNotIn("btn-primary btn-danger", html)

    def test_delete(self):
        url = reverse("customer-delete", args=[self.customer.pk])
        response = self.client.post(url, {"confirm": "on", "delete": "Delete"}, follow=True)
        self.assertContains(response, "Deleted »Customer 03«")
        self.assertFalse(Customer.objects.filter(pk=self.customer.pk).exists())

    def test_invalid_form_shows_coreui_validation(self):
        response = self.client.post(reverse("customer-create"), {"email": "nope", "status": "lead", "revenue": "0"})
        self.assertContains(response, "is-invalid")
        self.assertContains(response, "invalid-feedback")

    def test_modal_shell_is_stock(self):
        # Bootstrap's modal markup is CoreUI's; the three ids are crud_views' contract (modal.js, cv.adapters.modal).
        self.assertNotIn("crud_views_coreui", get_template("crud_views/modal/shell.html").origin.name)
        html = self.list_html()
        self.assertIn('<div class="modal fade" id="cv-modal" tabindex="-1" aria-hidden="true">', html)
        self.assertIn('id="cv-modal-dialog"', html)
        self.assertIn('id="cv-modal-content"', html)

    def test_filter_toggle_contract(self):
        html = self.list_html()
        button = re.search(r'<button[^>]*id="cv-filter-toggle"[^>]*>.*?</button>', html, re.S).group(0)
        self.assertIn('aria-controls="filter-collapse"', button)
        self.assertIn('aria-expanded="false"', button)
        self.assertIn(f'class="{COREUI_BUTTON_CLASSES["context:secondary:icon"]}"', button)
        self.assertIn('data-cv-tooltip="context"', button)
        self.assertIn('<span data-cv-filter-icon="open">', button)
        self.assertIn('<span data-cv-filter-icon="close" hidden>', button)
        self.assertEqual(button.count("<svg"), 2)

    def test_filter_toggle_reflects_the_session_state(self):
        response = self.client.post(
            reverse("customer-list"), data='{"filter_expanded": true}', content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        html = self.list_html()
        button = re.search(r'<button[^>]*id="cv-filter-toggle"[^>]*>.*?</button>', html, re.S).group(0)
        self.assertIn('aria-expanded="true"', button)
        self.assertIn('<span data-cv-filter-icon="open" hidden>', button)
        self.assertIn('<span data-cv-filter-icon="close">', button)
        self.assertIn('class="collapse show" id="filter-collapse"', html)

    def test_pinned_filter_has_no_toggle(self):
        with mock.patch.object(CustomerListView, "cv_filter_pinned", True):
            html = self.list_html()
        self.assertIn('id="filter-pinned"', html)
        self.assertNotIn('id="cv-filter-toggle"', html)
        self.assertIn("<svg", html[html.index('id="filter-pinned"') :][:800])  # the card header's filter icon

    def test_filter_is_the_stock_card(self):
        # Bootstrap's card markup is CoreUI's: the stock filter card needs no override.
        for name in ("crud_views/tags/list_filter.html", "crud_views/tags/list_filter.inner.html"):
            self.assertNotIn("crud_views_coreui", get_template(name).origin.name, name)
        html = self.list_html()
        self.assertRegex(
            html, r'<div class="collapse" id="filter-collapse">\s*<div class="card">\s*<div class="card-header">'
        )

    def test_action_tooltips_are_initialised_by_crud_views(self):
        html = self.list_html()
        buttons = re.findall(r"<(?:a|button)\b[^>]*\bcv-key=[^>]*>", html)
        self.assertGreater(len(buttons), 3)
        for tag in buttons:
            self.assertNotIn('data-bs-toggle="tooltip"', tag)
            self.assertNotIn('data-coreui-toggle="tooltip"', tag)
        self.assertTrue(any("data-cv-tooltip" in tag for tag in buttons))
        for key in ("list", "card", "create"):  # the filter toggle is checked by id in test_filter_toggle_contract
            self.assertIn('data-cv-tooltip="context"', self.tag(html, key), key)

    def test_toolbar_uses_theme_classes(self):
        html = self.list_html()
        create = self.tag(html, "create")
        self.assertIn('class="btn btn-primary cv-coreui-icon-btn"', create)
        self.assertIn('data-cv-tooltip="context"', create)
        self.assertIn('class="btn btn-outline-secondary cv-coreui-icon-btn active"', self.tag(html, "list"))
        self.assertIn('aria-current="page"', self.tag(html, "list"))
        self.assertRegex(
            html, r'<fieldset class="d-flex flex-wrap gap-2" aria-label="Actions" cv-context-container="true">'
        )

    def test_row_actions_use_theme_classes(self):
        html = self.list_html()
        delete = self.tag(html, "delete")
        self.assertIn('class="btn btn-sm btn-ghost-danger cv-coreui-icon-btn"', delete)
        self.assertIn('data-cv-tooltip="list"', delete)
        self.assertIn('class="btn btn-sm btn-ghost-secondary cv-coreui-icon-btn"', self.tag(html, "update"))
        self.assertIn('<fieldset class="d-flex flex-nowrap justify-content-end gap-1"', html)

    def test_overflow_menu_uses_theme_classes(self):
        with mock.patch.object(CustomerListView, "cv_list_actions_inline", ["detail"]):
            html = self.list_html()
        self.assertIn('<div class="dropdown">', html)
        self.assertRegex(
            html, r'class="btn btn-sm btn-ghost-secondary cv-coreui-icon-btn dropdown-toggle cv-menu-toggle"'
        )

    def test_actions_menu_toggle_uses_coreui_dropdown(self):
        with mock.patch.object(CustomerListView, "cv_list_actions_inline", ["detail"]):
            html = self.list_html()
        toggle = re.search(r'<button[^>]*class="[^"]*cv-menu-toggle[^"]*"[^>]*>', html, re.S).group(0)
        self.assertIn('data-coreui-toggle="dropdown"', toggle)
        self.assertIn("""data-coreui-popper-config='{"strategy":"fixed"}'""", toggle)  # list rows only
        self.assertNotIn("data-bs-", toggle)
        context = render_to_string("crud_views/tags/actions_menu_toggle.html", {"cv_location": "context"})
        self.assertIn('data-coreui-toggle="dropdown"', context)
        self.assertNotIn("popper-config", context)

    def test_language_selector_uses_coreui_dropdown(self):
        request = RequestFactory().get("/")
        html = render_to_string(
            "crud_views/snippets/language_selector.html",
            {"languages": [("en", "English"), ("de", "Deutsch")], "current": "en", "next": "/"},
            request=request,
        )
        self.assertIn('data-coreui-toggle="dropdown"', html)
        self.assertNotIn("data-bs-", html)

    def test_upstream_templates_are_not_overridden(self):
        # Every template whose stock Bootstrap 5 markup is already correct CoreUI markup: buttons and containers go
        # through the class table and crud_views' leaves; the modal shell, alert frame, card, filter and card grid are
        # plain Bootstrap components, which CoreUI keeps.
        for name in (
            "crud_views/modal/content.html",
            "crud_views/modal/shell.html",
            "crud_views/tags/alert.html",
            "crud_views/tags/card.html",
            "crud_views/tags/list_filter.html",
            "crud_views/tags/list_filter.inner.html",
            "crud_views/view_card.content.html",
            "crud_views/tags/actions_menu_item_label.html",
            "crud_views/tags/breadcrumb.html",
            "crud_views/tags/context_action.html",
            "crud_views/tags/list_action.html",
            "crud_views/tags/card_action.html",
            "crud_views/tags/context_actions.html",
            "crud_views/tags/navbar_items.html",
            "crud_views/columns/actions.html",
            "crud_views/tags/context_action_filter.html",
            "crud_views/snippets/card_order.html",
            "crud_views/snippets/pagination.html",
            "crud_views/tags/button/action.html",
            "crud_views/tags/button/container.html",
            "crud_views/tags/button/menu_item.html",
            "crud_views/tags/button/menu_item_label.html",
        ):
            self.assertNotIn("crud_views_coreui", get_template(name).origin.name, name)

    def test_theme_overrides_exactly_these_templates(self):
        overrides = sorted(str(path.relative_to(THEME / "templates")) for path in (THEME / "templates").rglob("*.html"))
        self.assertEqual(
            overrides,
            sorted(
                [
                    "crud_views/snippets/form_frame.html",
                    "crud_views/table/bootstrap5.html",
                    "crud_views_coreui/page.html",
                    *DATA_BS_OVERRIDES,
                ]
            ),
        )

    def test_menu_items_use_the_fixed_width_icon_slot(self):
        with mock.patch.object(CustomerListView, "cv_list_actions_inline", ["detail"]):
            html = self.list_html()
        item = re.search(r'<a\b[^>]*class="dropdown-item[^"]*"[^>]*cv-key="update"[^>]*>.*?</a>', html, re.S).group(0)
        self.assertIn('class="icon cv-icon-fw"', item)

    def test_breadcrumb_is_a_nav_landmark(self):
        self.assertIn('<nav aria-label="breadcrumb">', self.list_html())


class DataCoreuiTests(TestCase):
    """No data-bs-* reaches a page: CoreUI's data API only reads data-coreui-* (upstream tracker U1-U3)."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser("root", "root@example.com", "s3cret-pass")
        # the manage page is for the manage group's members only (upstream #361)
        cls.admin.groups.add(Group.objects.create(name=crud_views_settings.manage_group))
        Customer.objects.bulk_create(Customer(name=f"Customer {i:02}", revenue=i) for i in range(15))
        cls.customer = Customer.objects.get(name="Customer 03")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_no_data_bs_on_any_testapp_page(self):
        seen = 0
        for pattern in cv_customer.urlpatterns:  # the bulk ViewSet has no plain GET pages: test_bulk.py
            kwargs = {"pk": self.customer.pk} if "pk" in pattern.pattern.regex.groupindex else {}
            url = reverse(pattern.name, kwargs=kwargs)
            for headers in ({}, {"X-CV-Modal": "true"}):
                with self.subTest(url=url, headers=headers):
                    response = self.client.get(url, headers=headers)
                    self.assertEqual(response.status_code, 200)
                    self.assertNotIn("data-bs-", response.content.decode())
                    seen += 1
        self.assertGreaterEqual(seen, 2 * 9)  # every customer view, the two object-detail packs included
        # the list's row actions are all inline by default; with an overflow menu the ⋯ toggle renders too
        with mock.patch.object(CustomerListView, "cv_list_actions_inline", ["detail"]):
            html = self.client.get(reverse("customer-list")).content.decode()
        self.assertIn("cv-menu-toggle", html)
        self.assertNotIn("data-bs-", html)

    def test_data_bs_overrides_track_upstream(self):
        for name, package in DATA_BS_OVERRIDES.items():
            with self.subTest(name=name):
                upstream = Path(package.__file__).resolve().parent / "templates" / name
                override = THEME / "templates" / name
                self.assertEqual(Path(get_template(name).origin.name), override)
                header = (
                    f"{{# crud_views_coreui: {package.__name__}/templates/{name} @ {UPSTREAM_COMMIT}, "
                    "data-bs- renamed to data-coreui- (upstream tracker U1). #}\n"
                )
                expected = header + upstream.read_text().replace("data-bs-", "data-coreui-")
                self.assertEqual(override.read_text(), expected)
                self.assertIn("data-bs-", upstream.read_text())  # the copy exists only while upstream hard-codes it

    def test_no_new_upstream_data_bs_outside_the_overrides(self):
        """Every installed upstream crud_views* template or JS file that hard-codes data-bs- is already handled.

        The handled set is the four DATA_BS_OVERRIDES templates plus object_detail's tabs.js (the theme's
        coreui-tabs.js does its work). Comments do not count: JS `//` and `/* */` comments and Django `{# #}`
        comments are stripped before searching, so tooltip.js, which only names data-bs-toggle="tooltip" in a `//`
        comment, is not a hit. A new hit means upstream added Bootstrap-only markup the theme must override.
        """
        import importlib

        names = ("crud_views", "crud_views_object_detail", "crud_views_workflow", "crud_views_polymorphic")
        names += ("crud_views_guardian",)
        found = set()
        for name in names:
            root = Path(importlib.import_module(name).__file__).resolve().parent
            for path in list(root.rglob("*.html")) + list(root.rglob("*.js")):
                text = path.read_text()
                if path.suffix == ".js":
                    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
                    text = re.sub(r"(?m)//.*$", "", text)
                else:
                    text = re.sub(r"\{#.*?#\}", "", text, flags=re.S)
                    text = re.sub(r"\{% comment %\}.*?\{% endcomment %\}", "", text, flags=re.S)
                if "data-bs-" in text:
                    found.add(path.relative_to(root.parent).as_posix())
        expected = {f"{package.__name__}/templates/{name}" for name, package in DATA_BS_OVERRIDES.items()} | {
            "crud_views_object_detail/static/crud_views_object_detail/js/tabs.js"
        }
        self.assertEqual(found, expected)

    def test_tabs_vertical_pack_uses_coreui_pills(self):
        html = self.client.get(reverse("customer-properties", args=[self.customer.pk])).content.decode()
        self.assertIn("data-cv-od-tabs", html)
        self.assertIn('data-coreui-toggle="pill"', html)
        self.assertRegex(html, r'data-coreui-target="#[^"]+"')
        self.assertIn("crud_views_object_detail/js/tabs.js", html)  # upstream's init stays loaded; it finds nothing
        self.assertIn("crud_views_coreui/coreui-tabs.js", html)

    def test_accordion_pack_uses_coreui_collapse(self):
        html = self.client.get(reverse("customer-accordion", args=[self.customer.pk])).content.decode()
        self.assertIn('data-coreui-toggle="collapse"', html)
        self.assertRegex(html, r'data-coreui-target="#[^"]+"')
        self.assertRegex(html, r'data-coreui-parent="#[^"]+"')

    def test_coreui_tabs_script_initialises_coreui_triggers_through_the_adapter(self):
        script = (THEME / "static/crud_views_coreui/coreui-tabs.js").read_text()
        self.assertIn(
            '\'[data-coreui-toggle="tab"], [data-coreui-toggle="pill"], [data-coreui-toggle="list"]\'', script
        )
        self.assertIn("[data-cv-od-tabs]", script)
        self.assertIn("cv?.adapters?.tab", script)
        self.assertIn("tab.init(el)", script)
        self.assertIn("tab.dispose(el)", script)
        self.assertIn('"cv:modal:loaded"', script)
        self.assertIn('"cv:modal:unload"', script)
        self.assertNotIn("data-bs-", script)
        self.assertNotIn("globalThis.coreui", script)  # only through cv.adapters

    def test_coreui_tabs_script_keeps_the_adapter_contract(self):
        # upstream's tabs.js: a missing tab entry is a no-op, a present one must supply init and dispose
        script = (THEME / "static/crud_views_coreui/coreui-tabs.js").read_text()
        self.assertIn('typeof tab.init !== "function" || typeof tab.dispose !== "function"', script)
        self.assertIn('throw new TypeError("cv.adapters.tab must supply init(element) and dispose(element)")', script)
        self.assertIn("if (tab == null) return null;", script)
        upstream = (
            Path(crud_views_object_detail.__file__).resolve().parent / "static/crud_views_object_detail/js/tabs.js"
        ).read_text()
        self.assertIn('throw new TypeError("cv.adapters.tab must supply init(element) and dispose(element)")', upstream)

    def test_coreui_tabs_script_wraps_the_public_initializer(self):
        # cv.initObjectDetailTabs(root) is upstream's documented hook (custom insertion, a late UI library). tabs.js
        # loads after the theme script and assigns it unconditionally, so until then the global is a one-shot accessor:
        # that first assignment becomes the upstream part, and the global turns into a plain writable property holding
        # the wrapper, so a project's own wrapping composes without recursion. If tabs.js ran first, the plain
        # property is defined directly. Assigning the wrapper to itself keeps the accessor.
        script = (THEME / "static/crud_views_coreui/coreui-tabs.js").read_text()
        self.assertRegex(
            script,
            r"function publish\(fn\) \{\s*upstreamInit = fn;\s*Object\.defineProperty\(cv, \"initObjectDetailTabs\", \{"
            r"\s*configurable: true,\s*enumerable: true,\s*writable: true,\s*value: initObjectDetailTabs,",
        )
        self.assertRegex(
            script,
            r'if \(typeof cv\.initObjectDetailTabs === "function"\) \{\s*publish\(cv\.initObjectDetailTabs\);',
        )
        self.assertIn("get: () => initObjectDetailTabs,", script)
        self.assertRegex(
            script,
            r"set: fn => \{\s*if \(fn !== initObjectDetailTabs\) \{\s*"
            r'publish\(typeof fn === "function" \? fn : null\);',
        )
        self.assertRegex(
            script,
            r"function initObjectDetailTabs\(root = document\) \{\s*if \(upstreamInit\) \{\s*upstreamInit\(root\);"
            r"\s*\}\s*initCoreuiObjectDetailTabs\(root\);",
        )
        upstream = (
            Path(crud_views_object_detail.__file__).resolve().parent / "static/crud_views_object_detail/js/tabs.js"
        ).read_text()
        self.assertIn("globalThis.cv.initObjectDetailTabs = initObjectDetailTabs;", upstream)  # a plain assignment
        html = self.client.get(reverse("customer-properties", args=[self.customer.pk])).content.decode()
        self.assertLess(  # the accessor must exist before tabs.js assigns
            html.index("crud_views_coreui/coreui-tabs.js"), html.index("crud_views_object_detail/js/tabs.js")
        )

    def test_upstream_tabs_script_still_selects_data_bs(self):
        # The theme's coreui-tabs.js exists because upstream's tabs.js hard-codes data-bs-toggle (tracker U2). When
        # this fails, upstream has a hook: drop coreui-tabs.js.
        package = Path(crud_views_object_detail.__file__).resolve().parent
        source = (package / "static/crud_views_object_detail/js/tabs.js").read_text()
        self.assertIn("""'[data-bs-toggle="tab"], [data-bs-toggle="pill"], [data-bs-toggle="list"]'""", source)

    def test_tabs_script_is_registered_after_the_adapter(self):
        bundle = {bundle.key: bundle for bundle in get_registered()}["crud_views_coreui"]
        self.assertEqual(
            [asset.path for asset in bundle.js],
            ["crud_views_coreui/coreui-adapters.js", "crud_views_coreui/coreui-tabs.js"],
        )


class CardThemeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser("root", "root@example.com", "s3cret-pass")
        Customer.objects.bulk_create(Customer(name=f"Customer {i:02}", revenue=i * 10) for i in range(15))

    def setUp(self):
        self.client.force_login(self.admin)

    def get(self, **params):
        return self.client.get(reverse("customer-card"), params).content.decode()

    def test_cards_render_in_the_stock_grid(self):
        html = self.get()
        self.assertRegex(html, r'<div class="row">\s*<div class="col-sm-6 col-lg-4">')
        self.assertEqual(html.count('<div class="card mb-4">'), 12)  # paginate_by
        self.assertEqual(html.count('class="d-flex flex-wrap gap-2" cv-card-container="true"'), 12)
        self.assertIn('class="pagination', html)
        self.assertNotIn("fa-solid", html)
        self.assertNotIn("<i class=", html)

    def test_card_root_spaces_the_stock_grid(self):
        # The stock card grid is a .row without a vertical gutter: card:root keeps upstream's bottom margin.
        self.assertEqual(COREUI_BUTTON_CLASSES["card:root"], "card mb-4")

    def test_card_action_variants(self):
        html = self.get()
        self.assertIn('class="btn btn-sm btn-primary flex-grow-1"', html)  # primary + flex, labelled: not square
        self.assertIn('class="btn btn-sm btn-ghost-secondary cv-coreui-icon-btn"', html)  # tertiary:icon (delete)
        open_ = re.search(r'<a\b[^>]*cv-key="detail"[^>]*>.*?</a>', html, re.S).group(0)
        self.assertIn("<svg", open_)  # label mode "both", upstream's card default (#213): icon and text
        self.assertIn("<span>Open</span>", open_)
        self.assertIn('<span class="visually-hidden">Delete</span>', html)  # icon-only keeps a name

    def _render_card(self, template, classes=None):
        page = self.client.get(reverse("customer-card")).context
        customer = Customer.objects.get(name="Customer 03")
        with override_settings(CRUD_VIEWS_BUTTON_CLASSES=classes or {}):
            return template.render(Context({"object": customer, "view": page["view"], "request": page["request"]}))

    def test_card_follows_upstream_block_names_and_class_keys(self):
        # upstream #243: a cv_card_template extends crud_views' card and fills its blocks
        template = Template(
            '{% extends "crud_views/tags/card.html" %}'
            "{% block card_title %}T{% endblock %}{% block card_content %}<p>C</p>{% endblock %}"
            "{% block card_actions %}{% endblock %}"
        )
        html = self._render_card(template, {"card:title": "card-title x-title"})
        self.assertIn('<div class="card mb-4">', html)
        self.assertIn('<h5 class="card-title x-title">T</h5>', html)
        self.assertIn("<p>C</p>", html)
        self.assertNotIn("cv-card-container", html)

    def test_card_new_blocks_are_empty_by_default(self):
        # upstream #325: card_root and card_header exist and render nothing unless filled
        html = self._render_card(Template('{% extends "crud_views/tags/card.html" %}'))
        self.assertRegex(html, r'<div class="card mb-4">\s*<div class="card-body">\s*<h5 class="card-title">')

    def test_card_root_and_header_blocks_render_in_place(self):
        html = self._render_card(get_template("testapp/customer_card_blocks.html").template)
        self.assertRegex(html, r'<div class="card mb-4"><i data-root></i>\s*<div class="card-body"><i data-head></i>')

    def test_card_links_carry_their_origin(self):
        html = self.get()
        self.assertIn("/update/?cv_from=card", html)
        self.assertIn("/delete/?cv_from=card", html)

    def test_pagination_is_upstream_with_coreui_chevrons(self):
        # upstream #241: accessible markup and arrows from the icon registry; the theme maps the icons only
        html = self.get(page=2)
        nav = re.search(r'<nav aria-label="pagination".*?</nav>', html, re.S).group(0)
        self.assertIn(str(svg("cil-chevron-left")), nav)
        self.assertIn(str(svg("cil-chevron-right")), nav)
        self.assertIn('<li class="page-item active" aria-current="page">', nav)
        self.assertIn('<a class="page-link" aria-disabled="true">', nav)  # page 2 of 2: no next page
        self.assertIn('<span class="visually-hidden">previous</span>', nav)

    def test_order_bar(self):
        html = self.get(order="revenue", dir="desc")
        self.assertIn('id="cv-card-order-form"', html)
        self.assertRegex(html, r'value="desc"\s+class="btn btn-outline-secondary cv-coreui-icon-btn active"')
        self.assertIn('<fieldset class="btn-group"', html)
        self.assertRegex(html, r'<button[^>]*value="asc"[^>]*>\s*<svg')
        self.assertLess(html.index("Customer 14"), html.index("Customer 13"))

    def test_empty_state(self):
        html = self.get(name="nothing-matches", submit="Apply Filter")
        self.assertIn('<p class="text-muted">No items found.</p>', html)

    @override_settings(LANGUAGE_CODE="de")
    def test_empty_state_is_translated(self):
        # crud_views' card list translates its empty state upstream (#246)
        html = self.get(name="nothing-matches", submit="Apply Filter")
        self.assertIn("Keine Einträge gefunden.", html)

    def test_delete_from_card_returns_to_cards(self):
        customer = Customer.objects.get(name="Customer 03")
        url = reverse("customer-delete", args=[customer.pk]) + "?cv_from=card"
        response = self.client.post(url, {"confirm": "on", "delete": "Delete"})
        self.assertRedirects(response, reverse("customer-card"), fetch_redirect_response=False)

    def test_headings_follow_crud_views_header_level(self):
        # page title and card titles go through {% cv_heading %} (#251), like the stock templates; the page title keeps
        # CoreUI's h3 size at any level (size=3)
        html = self.get()
        self.assertRegex(html, r'<h2 class="h3 page-title mb-0">')
        self.assertRegex(html, r'<h5 class="card-title">')
        # crud_views reads the setting once into crud_views_settings; its own tests patch that object the same way
        with mock.patch.object(crud_views_settings, "header_level", 1):
            html = self.get()
        self.assertRegex(html, r'<h1 class="h3 page-title mb-0">')
        self.assertRegex(html, r'<h2 class="h5 card-title">')

    def test_icon_only_card_action_has_a_crud_views_tooltip(self):
        html = self.get()
        delete = re.search(r"<a\b[^>]*/delete/\?cv_from=card[^>]*>", html).group(0)  # the label_mode="icon" action
        self.assertIn("cv-coreui-icon-btn", delete)
        self.assertIn('data-cv-tooltip="card"', delete)
        self.assertNotIn('data-bs-toggle="tooltip"', delete)


class MessagesParityTests(SimpleTestCase):
    """The shell's messages include and crud_views' {% cv_messages %} render the same alert but the dismiss hook."""

    def assert_message_parity(self, plain, themed):
        class Hooks(HTMLParser):
            def __init__(self):
                super().__init__()
                self.alerts = 0
                self.buttons = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if attrs.get("role") == "alert":
                    self.alerts += 1
                if tag == "button":
                    self.buttons.append(attrs)

        native, crud = Hooks(), Hooks()
        native.feed(plain)
        crud.feed(themed)
        self.assertGreater(native.alerts, 0)
        self.assertEqual(native.alerts, crud.alerts)
        self.assertEqual(len(native.buttons), native.alerts)
        self.assertEqual(len(crud.buttons), crud.alerts)
        for button in native.buttons:
            self.assertEqual(button.get("data-coreui-dismiss"), "alert")
            self.assertNotIn("data-cv-alert-dismiss", button)
        for button in crud.buttons:
            self.assertIn(button.get("data-cv-alert-dismiss", "missing"), ("", None))
            self.assertNotIn("data-coreui-dismiss", button)

        def normalized(value):
            return re.sub(r">\s+<", "><", re.sub(r"\s+", " ", value)).strip()

        self.assertEqual(
            normalized(plain.replace('data-coreui-dismiss="alert"', "data-cv-alert-dismiss")), normalized(themed)
        )

    def test_parity_rejects_wrong_missing_dual_hooks_and_unrelated_changes(self):
        messages = [Message(constants.INFO, "unchanged body")]
        native = render_to_string("django_coreui/includes/messages.html", {"messages": messages})
        crud = Template("{% load crud_views %}{% cv_messages %}").render(Context({"messages": messages}))
        self.assert_message_parity(native, crud)
        for changed in (
            crud.replace("data-cv-alert-dismiss", 'data-cv-alert-dismiss="wrong"'),
            crud.replace("data-cv-alert-dismiss", ""),
            crud.replace("data-cv-alert-dismiss", 'data-cv-alert-dismiss data-coreui-dismiss="alert"'),
            crud.replace('role="alert"', 'role="status"'),
            crud.replace("unchanged body", "changed body"),
        ):
            with self.subTest(changed=changed), self.assertRaises(AssertionError):
                self.assert_message_parity(native, changed)

    def test_plain_include_matches_cv_messages(self):
        messages = [
            Message(constants.DEBUG, "d"),
            Message(constants.INFO, "i"),
            Message(constants.SUCCESS, "s", extra_tags="probe"),
            Message(constants.WARNING, "<b>w</b>"),
            Message(constants.ERROR, "e"),
            Message(35, "custom"),
        ]
        plain = render_to_string("django_coreui/includes/messages.html", {"messages": messages})
        themed = Template("{% load crud_views %}{% cv_messages %}").render(Context({"messages": messages}))
        self.assert_message_parity(plain, themed)


class HeadingRepeatsTabTests(SimpleTestCase):
    """cv_coreui_heading_repeats_tab: with a bar, a view heading that says the same as the active tab is left out."""

    @staticmethod
    def repeats(header, items, navbar=True):
        from crud_views_coreui.templatetags.crud_views_coreui import cv_coreui_heading_repeats_tab

        context = Context(
            {"view": SimpleNamespace(cv_header=header), "cv_navbar": {"items": items} if navbar else None}
        )
        return cv_coreui_heading_repeats_tab(context)

    def test_heading_equal_to_the_active_tab_repeats(self):
        items = [{"label": "Details", "active": False}, {"label": "Orders", "active": True}]
        self.assertTrue(self.repeats("Orders", items))

    def test_markup_and_whitespace_are_ignored(self):
        self.assertTrue(self.repeats('<span class="x">\n  Orders </span>', [{"label": "Orders", "active": True}]))

    def test_heading_that_says_more_does_not_repeat(self):
        self.assertFalse(self.repeats("Order #1073", [{"label": "Orders", "active": True}]))

    def test_inactive_tab_with_the_same_label_does_not_count(self):
        items = [{"label": "Orders", "active": False}, {"label": "Details", "active": True}]
        self.assertFalse(self.repeats("Orders", items))

    def test_no_active_tab_or_no_bar_never_repeats(self):
        self.assertFalse(self.repeats("Orders", [{"label": "Orders", "active": False}]))
        self.assertFalse(self.repeats("Orders", [{"label": "Orders", "active": True}], navbar=False))


class ThemeCssTests(SimpleTestCase):
    def test_object_navbar_tabs_use_coreui_classes(self):
        # Upstream #384: the tabs take CoreUI's nav-underline-border through the navbar:* keys; the CSS keeps only the
        # smaller view title below the tabs
        css = THEME_CSS.read_text()
        self.assertNotIn(".nav-pills", css)
        self.assertRegex(css, r"\.cv-coreui-owner ~ \.row \.page-title \{\s*font-size: 1rem;")
        self.assertEqual(
            {key: value for key, value in COREUI_BUTTON_CLASSES.items() if key.startswith("navbar:")},
            {
                "navbar:nav": "nav nav-underline-border flex-wrap row-gap-1",
                "navbar:item": "nav-item mw-100",
                "navbar:link": "nav-link d-flex align-items-center mw-100 text-break gap-2",
            },
        )

    def test_icon_buttons_are_square_in_both_directions(self):
        # Browser pass: as a flex container the button lost its text line box, so its height followed the 16px icon
        # (26px instead of 31px for .btn-sm) and the menu toggle next to a link button was shorter. Width and height
        # come from the same size.
        css = THEME_CSS.read_text()
        rule = re.search(r"\.cv-coreui-icon-btn \{(.*?)\n\}", css, re.S).group(1)
        self.assertIn("--cv-coreui-icon-btn-size: calc(", rule)
        self.assertIn("width: var(--cv-coreui-icon-btn-size);", rule)
        self.assertIn("height: var(--cv-coreui-icon-btn-size);", rule)

    def test_card_table_drops_the_inner_margins(self):
        css = THEME_CSS.read_text()
        wrapper = r"\.cv-coreui-table > \.table-container > "
        self.assertRegex(css, wrapper + r"\.table-responsive > \.table \{\s*margin-bottom: 0;")
        self.assertRegex(css, wrapper + r"\.card-footer \.pagination \{\s*margin-bottom: 0;")


class ThemeAdoptionTests(TestCase):
    """Native form floor, exact registrations and real action rendering contracts."""

    @classmethod
    def setUpTestData(cls):
        cls.actor = get_user_model().objects.create_superuser("adoption", "adoption@example.invalid", None)
        cls.customer = Customer.objects.create(name="Adoption")

    def setUp(self):
        self.client.force_login(self.actor)

    def controls(self, markup):
        class Controls(HTMLParser):
            def __init__(self):
                super().__init__()
                self.rows = []
                self.current = None

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag in ("button", "a"):
                    self.current = {"tag": tag, "attrs": attrs, "paths": [], "text": "", "hidden": False}
                elif self.current is not None and tag == "path":
                    self.current["paths"].append(attrs.get("d"))
                elif self.current is not None and tag == "span" and "visually-hidden" in attrs.get("class", ""):
                    self.current["hidden"] = True

            def handle_data(self, data):
                if self.current is not None:
                    self.current["text"] += data

            def handle_endtag(self, tag):
                if tag in ("button", "a") and self.current is not None:
                    self.rows.append(self.current)
                    self.current = None

        parser = Controls()
        parser.feed(str(markup))
        return parser.rows

    def render_actions(self, mode=None, owner_mode=None, kind_mode=None, destination="absent", tag="button"):
        from crispy_forms.bootstrap import FormActions
        from crispy_forms.helper import FormHelper
        from crispy_forms.layout import Layout
        from crispy_forms.utils import render_crispy_form
        from crud_views.lib.crispy.buttons import Button, Submit
        from crud_views.lib.view import CrudView
        from crud_views.lib.views.list import ListViewFilterFormHelper

        class Owner(CrudView):
            cv_abstract = True
            cv_form_actions_label_mode = (
                dict.fromkeys(("submit", "delete", "cancel", "filter-submit", "filter-reset"), owner_mode)
                if owner_mode
                else {}
            ) | ({"cancel": kind_mode} if kind_mode else {})

        owner = Owner()
        form = ProbeForm(initial={"x": "initial"})
        form.cv_view = owner
        helper = FormHelper()
        helper.form_tag = False
        kwargs = {} if destination == "absent" else {"data_cv_cancel_url": None if destination == "none" else ""}
        helper.layout = Layout(
            "x",
            FormActions(
                Submit("save", "Save"),
                Submit("delete", "Delete", slot="form:delete"),
                Button("cancel", "Cancel", tag=tag, **kwargs),
            ),
        )
        filtered = ProbeForm(initial={"x": "initial"})
        filtered.helper = ListViewFilterFormHelper(view=owner, request=RequestFactory().get("/"))
        filtered.helper.layout = Layout("x")
        with override_settings(CRUD_VIEWS_LABEL_MODE_DEFAULTS={} if mode is None else {"form": mode}):
            markup = render_crispy_form(form, helper) + render_crispy_form(filtered, filtered.helper)
        return self.controls(markup), str(markup)

    def test_registered_floor_exact_maps_and_native_action_modes(self):
        from crud_views.lib.view.label_mode import default_label_mode

        with override_settings(CRUD_VIEWS_LABEL_MODE_DEFAULTS={}):
            self.assertEqual(default_label_mode("form"), "both")
        self.assertEqual(
            {name: COREUI_ICONS[name] for name in ("save", "cancel", "filter-reset")},
            {"save": "coreui:cil-check", "cancel": "coreui:cil-arrow-left", "filter-reset": "coreui:cil-filter-x"},
        )
        self.assertEqual(
            {
                name: COREUI_BUTTON_CLASSES[name]
                for name in ("form:actions", "form:filter-actions", "alert:dismissible", "alert:close")
            },
            {
                "form:actions": "d-flex flex-wrap gap-2",
                "form:filter-actions": "d-flex flex-wrap gap-1",
                "alert:dismissible": "alert-dismissible fade show",
                "alert:close": "btn-close",
            },
        )
        glyphs = ("cil-check", "cil-trash", "cil-arrow-left", "cil-filter", "cil-filter-x")
        for mode in ("both", "icon", "label"):
            rows, markup = self.render_actions(mode)
            self.assertEqual(len(rows), 5)
            self.assertNotIn("fa-solid", markup)
            for row, name in zip(rows, glyphs, strict=True):
                self.assertEqual(row["paths"], [] if mode == "label" else icon_paths(name))
                self.assertTrue(row["text"].strip())
                self.assertEqual(row["hidden"], mode == "icon")
            self.assertEqual(rows[-1]["attrs"]["type"], "reset")
            self.assertTrue(rows[-1]["attrs"]["value"])
        rows, _ = self.render_actions("label", "icon", "both")
        self.assertTrue(rows[0]["hidden"])
        self.assertFalse(rows[2]["hidden"])
        self.assertEqual(rows[2]["paths"], icon_paths("cil-arrow-left"))
        self.assertEqual(self.render_actions()[0][0]["paths"], icon_paths("cil-check"))

    def test_missing_each_new_mapping_fails_native_render_assertion(self):
        from crud_views.lib import icons

        mappings = (("save", 0, "cil-check"), ("cancel", 2, "cil-arrow-left"), ("filter-reset", 4, "cil-filter-x"))
        for name, position, glyph in mappings:
            with self.subTest(name=name), mock.patch.dict(icons._THEME_ICONS), override_settings(CRUD_VIEWS_ICONS={}):
                icons._THEME_ICONS.pop(name)
                icons.reset_icon_cache()
                rows, _ = self.render_actions("both")
                with self.assertRaises(AssertionError):
                    self.assertEqual(rows[position]["paths"], icon_paths(glyph))

    def test_cancel_absent_none_empty_all_modes_and_requested_tags(self):
        for destination in ("absent", "none", "empty"):
            for tag in ("button", "a"):
                for mode in ("both", "icon", "label"):
                    with self.subTest(destination=destination, tag=tag, mode=mode):
                        rows, _ = self.render_actions(mode, destination=destination, tag=tag)
                        cancel = rows[2]
                        self.assertEqual(cancel["tag"], "button")
                        self.assertEqual(cancel["attrs"]["type"], "button")
                        self.assertNotIn("href", cancel["attrs"])
                        self.assertEqual("data-cv-cancel-url" in cancel["attrs"], destination == "empty")
                        self.assertEqual(
                            cancel["attrs"].get("data-cv-cancel-url"), "" if destination == "empty" else None
                        )
                        self.assertEqual(cancel["text"].strip(), "Cancel")
                        self.assertEqual(cancel["paths"], [] if mode == "label" else icon_paths("cil-arrow-left"))

    def test_real_create_update_delete_and_filter_pages_have_native_controls(self):
        for name, args in (
            ("customer-create", []),
            ("customer-update", [self.customer.pk]),
            ("customer-delete", [self.customer.pk]),
            ("customer-list", []),
        ):
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)
                markup = response.content.decode()
                self.assertNotIn("fa-solid", markup)
                self.assertNotIn("fa-regular", markup)
                glyph = {"customer-list": "cil-filter", "customer-delete": "cil-trash"}.get(name, "cil-check")
                self.assertTrue(any(row["paths"] == icon_paths(glyph) for row in self.controls(markup)))


class WorkflowBadgeTests(SimpleTestCase):
    def badge(self, colour="success"):
        from crud_views_workflow.lib.mixins import WorkflowModelMixin
        from django.db.models import TextChoices

        class States(TextChoices):
            DONE = "done", '<Done "now"> {{ untouched }}'

        class Item(WorkflowModelMixin):
            STATE_CHOICES = States
            STATE_BADGES = {"done": colour}

        return Item().get_state_badge("done")

    def test_badge_uses_current_upstream_source(self):
        import crud_views_workflow.lib.mixins as mixins

        # The installed crud_views_workflow (sibling checkout locally, git main under nox); CV_WORKFLOW_UPSTREAM_SRC
        # pins a specific source tree. Either way the badge template must come from that same tree, not a theme copy.
        installed = Path(mixins.__file__).resolve().parents[2]
        upstream = Path(os.environ.get("CV_WORKFLOW_UPSTREAM_SRC", installed)).resolve()
        self.assertEqual(Path(mixins.__file__).resolve(), upstream / "crud_views_workflow/lib/mixins.py")
        self.assertEqual(
            Path(get_template("crud_views_workflow/badge.html").origin.name).resolve(),
            upstream / "crud_views_workflow/templates/crud_views_workflow/badge.html",
        )

    def test_all_state_colours_are_subtle_badges(self):
        from crud_views_workflow.lib.enums import BadgeEnum

        for colour in BadgeEnum:
            with self.subTest(colour=colour):
                html = self.badge(colour)
                self.assertIn(f'class="badge bg-{colour}-subtle text-{colour}-emphasis"', html)
                self.assertIn("&lt;Done &quot;now&quot;&gt; {{ untouched }}", html)
                self.assertNotIn("<Done", html)

    def test_history_table_matches_the_theme_list_table(self):
        self.assertEqual(get_button_classes()["workflow:history-table"], "table align-middle")

    def test_project_classes_override_theme_including_disabled_values(self):
        for value in ("", None, 'custom" onmouseover="bad'):
            with (
                self.subTest(value=value),
                override_settings(CRUD_VIEWS_BUTTON_CLASSES={"workflow:badge-success": value}),
            ):
                html = self.badge()
                expected = "custom&quot; onmouseover=&quot;bad" if value else ""
                self.assertIn(f'class="{expected}"', html)
                self.assertNotIn(' onmouseover="', html)

    def test_optional_workflow_and_ready_orders_in_isolated_processes(self):
        script = """
import sys
from django.conf import settings
from tests.crud_views_coreui import settings as test_settings
values = {key: getattr(test_settings, key) for key in dir(test_settings) if key.isupper()}
apps = list(values["INSTALLED_APPS"])
apps.remove("crud_views_workflow")
if sys.argv[1] != "absent":
    apps.insert(apps.index("crud_views_coreui") + (sys.argv[1] == "after"), "crud_views_workflow")
values["INSTALLED_APPS"] = apps
settings.configure(**values)
import django
django.setup()
from crud_views.lib.button_classes import get_button_classes, _THEME_BUTTON_CLASSES
from django.core.checks import run_checks
classes = get_button_classes()
if sys.argv[1] == "absent":
    assert not any(key.startswith("workflow:") for key in _THEME_BUTTON_CLASSES)
    assert not any(key.startswith("workflow:") for key in classes)
else:
    assert classes["workflow:badge-success"] == "badge bg-success-subtle text-success-emphasis"
    from django.test import override_settings
    with override_settings(CRUD_VIEWS_BUTTON_CLASSES={"workflow:badge-success": "project"}):
        assert get_button_classes()["workflow:badge-success"] == "project"
assert not any(check.id == "crud_views.W362" for check in run_checks())
"""
        for order in ("absent", "before", "after"):
            with self.subTest(order=order):
                result = subprocess.run([sys.executable, "-c", script, order], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class WorkflowMarkup(HTMLParser):
    """Retain raw ancestry, including nested forms that browser parsers would repair."""

    def __init__(self, markup):
        super().__init__()
        self.nodes = []
        self.stack = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        node = SimpleNamespace(tag=tag, attrs=dict(attrs), parents=tuple(self.stack))
        self.nodes.append(node)
        if tag not in {"input", "br", "hr", "img", "meta", "link", "wbr"}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1].tag == tag:
            self.stack.pop()

    def select(self, tag):
        return [node for node in self.nodes if node.tag == tag]


class WorkflowPresentationTests(SimpleTestCase):
    def render_workflow(self, choices=True, history=True, invalid=False, modal=False, settings_classes=None):
        from crud_views.lib.view import CrudView
        from crud_views_workflow.lib.enums import WorkflowComment
        from crud_views_workflow.lib.forms import WorkflowForm
        from django.contrib.auth.models import AnonymousUser

        class Owner(CrudView):
            cv_abstract = True

            def get_cancel_button_context(self, **kwargs):
                return {"cv_url": None}

        request = RequestFactory().get("/workflow/", headers={"X-Cv-Modal": "true"} if modal else {})
        request.user = AnonymousUser()
        owner = Owner()
        owner.request = request
        # WorkflowForm.clean() asks the view's object for business blockers (upstream #322); this one has none
        owner.object = SimpleNamespace(workflow_check_transition=lambda name, *, user: None)
        form = WorkflowForm(
            owner,
            data={"transition": "finish", "comment": ""} if invalid else None,
            choices=[("finish", '<Finish "now">')] if choices else [],
            transition_comments={"finish": WorkflowComment.REQUIRED},
        )
        if invalid:
            self.assertFalse(form.is_valid())
            form.add_error(None, '<Invalid "workflow">')
        rows = (
            [
                {
                    "transition_label": "<Finish>",
                    "user": SimpleNamespace(get_full_name=lambda: "<Actor>"),
                    "state_old_badge": WorkflowBadgeTests().badge(),
                    "state_new_badge": WorkflowBadgeTests().badge(),
                    "comment": "<script>bad</script>",
                }
            ]
            if history
            else []
        )
        context = {"form": form, "has_workflow_choices": choices, "object": SimpleNamespace(workflow_data=rows)}
        template = (
            "crud_views/view_custom_form.content.html" if modal else "crud_views_workflow/view_workflow.content.html"
        )
        with override_settings(CRUD_VIEWS_BUTTON_CLASSES=settings_classes or {}):
            markup = render_to_string(template, context, request=request)
        return markup, WorkflowMarkup(markup)

    def test_actual_template_and_pack_origins(self):
        self.assertEqual(
            Path(get_template("crud_views/snippets/form_frame.html").origin.name),
            THEME / "templates/crud_views/snippets/form_frame.html",
        )
        import crud_views_workflow

        upstream = Path(crud_views_workflow.__file__).resolve().parent
        for leaf in ("action", "history", "content"):
            name = f"crud_views_workflow/view_workflow.{leaf}.html"
            self.assertEqual(Path(get_template(name).origin.name), upstream / "templates" / name)
        import django_coreui

        self.assertEqual(
            Path(get_template("crispy_coreui/field.html").origin.name),
            Path(django_coreui.__file__).resolve().parent / "templates/crispy_coreui/field.html",
        )

    def test_action_frame_history_order_and_error_ownership(self):
        for invalid in (False, True):
            with self.subTest(invalid=invalid):
                markup, tree = self.render_workflow(invalid=invalid)
                self.assertEqual(len(tree.select("form")), 1)
                form = tree.select("form")[0]
                self.assertEqual(form.attrs, {"class": "cv-form", "method": "post", "novalidate": None})
                self.assertEqual(form.parents[-1].attrs["class"], "card-body")
                self.assertEqual(form.parents[-2].attrs["class"], "card")
                headings = tree.select("h5")
                self.assertEqual(headings[-1].parents, form.parents)
                table = tree.select("table")[0]
                wrapper = table.parents[-1]
                self.assertEqual(wrapper.attrs["class"], "table-responsive")
                self.assertEqual(
                    [node.tag for node in tree.nodes if node.parents and node.parents[-1] is wrapper], ["table"]
                )
                self.assertNotIn(wrapper, form.parents)
                self.assertNotIn(wrapper, headings[0].parents)
                self.assertLess(tree.nodes.index(table), tree.nodes.index(form))
                tokens = [node for node in tree.select("input") if node.attrs.get("name") == "csrfmiddlewaretoken"]
                self.assertEqual(len(tokens), 1)
                self.assertIn(form, tokens[0].parents)
                submits = [node for node in tree.nodes if node.attrs.get("type") == "submit"]
                self.assertEqual(len(submits), 1)
                self.assertIn(form, submits[0].parents)
                self.assertNotIn("<script>", markup)
                self.assertIn("&lt;Finish &quot;now&quot;&gt;", markup)
                if invalid:
                    self.assertIn("Comment is required for this transition", markup)
                    self.assertIn("&lt;Invalid &quot;workflow&quot;&gt;", markup)
                    errors = [node for node in tree.nodes if "invalid-feedback" in node.attrs.get("class", "")]
                    self.assertTrue(errors)
                    self.assertTrue(all(form in node.parents for node in errors))
                self.assertFalse(tree.stack)

    def test_empty_actions_and_history_are_independent(self):
        for history in (False, True):
            markup, tree = self.render_workflow(choices=False, history=history)
            self.assertIn('class="card-body"', markup)
            self.assertIn("There are no workflow steps available from the current state.", markup)
            self.assertNotIn("Workflow Action", markup)
            self.assertFalse(tree.select("form"))
            self.assertNotIn("csrfmiddlewaretoken", markup)
            self.assertEqual(len(tree.select("table")), int(history))
        markup, tree = self.render_workflow(history=False)
        self.assertNotIn("Workflow History", markup)
        self.assertFalse(tree.select("table"))
        self.assertEqual(len(tree.select("form")), 1)

    def test_history_wrapper_and_table_classes_are_independent(self):
        for wrapper_class in ("table-responsive", "custom-wrap", "", None):
            for table_class in ("table", "custom-table", "", None):
                _markup, tree = self.render_workflow(
                    settings_classes={"workflow:history-wrapper": wrapper_class, "workflow:history-table": table_class}
                )
                table = tree.select("table")[0]
                self.assertEqual(table.attrs["class"], table_class or "")
                self.assertEqual(table.parents[-1].attrs["class"], wrapper_class or "")
                self.assertEqual(len(tree.select("th")), 6)

    def test_supported_modal_keeps_the_actual_frame_bare(self):
        for choices in (False, True):
            markup, tree = self.render_workflow(choices=choices, modal=True)
            self.assertNotIn('class="card"', markup)
            self.assertNotIn('class="card-body"', markup)
            self.assertNotIn("Workflow History", markup)
            self.assertEqual(len(tree.select("form")), 1)
            self.assertFalse(tree.stack)
