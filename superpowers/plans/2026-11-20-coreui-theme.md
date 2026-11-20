# CoreUI theme (free edition) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `django-crud-views-coreui`, a free CoreUI 5 theme for django-crud-views (`django_coreui` shell + crispy pack, `crud_views_coreui` theme) with the Acme Roasters demo, built the way `../tabler-test` (django-crud-views-tabler) is built.

**Architecture:** A port of `../tabler-test` @ `7165eaf`, file for file where possible. CoreUI uses Bootstrap's class names, so most markup carries over. What changes is the JavaScript (`window.coreui`, `data-coreui-*`) and the CSS variables (`--cui-*`). Those are handled explicitly: the crispy vendoring script rewrites `data-bs-` to `data-coreui-`, the theme overrides the few crud_views templates that hard-code `data-bs-`, and an adapter script points `cv.adapters` at `window.coreui`. App code uses semantic icon names. Each project maps them.

**Tech Stack:** Python 3.12–3.15, Django 4.2/5.2/6.1, django-crud-views (sibling checkout `../django-crud-views` @ `fa2f0a7b`), django-crud-views-extensions, django-crispy-forms + crispy-bootstrap5 2026.9/2026.3, CoreUI 5.9.1 + @coreui/icons 3.1.0 from jsDelivr, hatchling, uv, nox, ruff, pytest(-django, -xdist), mkdocs, Task.

**Spec:** `superpowers/specs/2026-11-20-coreui-theme-design.md`. Read it before any task.

**Reference throughout:** `../tabler-test` (its `CLAUDE.md`, `docs/theme_internals.md`, `src/`, `tests/`, `example/`). "Port X" means: copy the Tabler file, rename `tabler` → `coreui` in identifiers, paths and docstrings, and change markup and classes to CoreUI's. Tabler-only behaviour that CoreUI doesn't need is dropped and logged in the tracker.

## Global Constraints

- Distribution `django-crud-views-coreui`; packages `django_coreui`, `crud_views_coreui`; crispy pack name `crispy_coreui`; icon library prefix `coreui`.
- Python 3.12–3.15 × Django 4.2, 5.2, 6.1 (4.2 only on 3.12/3.13). Local dev Python 3.14 / Django 6.1.
- `django_coreui` must not import `crud_views` (a test greps the package).
- Never commit CoreUI PRO material (SCSS, compiled CSS/JS, markup or text from the PRO zips). Reference markup comes from the free admin template (`coreui/coreui-free-bootstrap-admin-template`, MIT) and the free docs.
- CoreUI from jsDelivr with exact versions and SRI: `@coreui/coreui@5.9.1`, `@coreui/icons@3.1.0`. Icons are CC BY 4.0: attribution goes in README and in the `django_coreui/icons.py` header.
- No runtime `data-bs-*` → `data-coreui-*` shim. No patching or subclassing crud_views code. `../django-crud-views` and `../django-crud-views-extensions` are read-only.
- Fix order: an upstream hook (class keys, settings, blocks), then theme CSS, then an override template.
- Every override, theme CSS rule or workaround caused by an upstream gap gets an entry in `superpowers/notes/upstream-tracker.md` in the same commit.
- `settings.COREUI = {"edition": "free"}`. Any other edition is a system check error. Only `django_coreui/includes/assets.html` branches on it.
- Hosts: `DJANGO_ALLOWED_HOSTS` from env, default `localhost,127.0.0.1`. No `cv.jacob-consulting.org`.
- Brand "Acme Roasters", primary `#a0522d`.
- Test suites run with `pytest -n auto`, except a single test or a `-k` selection.
- Ruff config as `../tabler-test/pyproject.toml`. `uv run ruff format . && uv run ruff check .` is clean before every commit.

## Review Focus

1. **Semantic icon name with no mapping.** crud_views renders an unmapped name without a colon as a raw CSS class (`<i class="customer">`), so the icon silently disappears. Expect a failing test. Pinned in Task 2 (Tabler) and Task 9 (CoreUI): every icon name the example uses resolves to a `<library>:<name>` value with an SVG.
2. **Dynamically inserted content** (modal bodies, filter forms, formset rows added in the browser) must still get working dropdowns, tooltips and collapses with no `data-bs-*` left. Pinned in Task 7 (modal shell and `⋯` menu render `data-coreui-*`) and in Task 9's every-page test.
3. **Dark mode.** Manage page, formsets and theme badges must follow `data-coreui-theme="dark"`; upstream CSS reads `--bs-*`. Pinned in Task 6 (CSS maps every `--bs-*` that upstream CSS reads onto a `--cui-*` value).
4. **Bad project layout defaults** (unknown key, a value that isn't a token, a non-object JSON) must fail loudly, not render odd attributes. Pinned in Task 4.
5. **Narrow screens.** The sidebar collapses to an offcanvas below `lg` and the page-header actions wrap below the title. Pinned in Task 4 (markup: `sidebar-fixed`, header toggler targets `#sidebar`) plus the manual pass in Task 11.

---

### Task 1: Tabler: template icon aliases in `django_tabler`

Runs in `../tabler-test` on a new branch `semantic-icons` (never on `main`).

**Files:**
- Modify: `../tabler-test/src/django_tabler/templatetags/tabler.py` (`icon` tag)
- Test: `../tabler-test/tests/django_tabler/test_django_tabler.py` (new `IconAliasTests`)
- Modify: `../tabler-test/docs/icons.md` (document `TABLER_ICON_ALIASES`)

**Interfaces:**
- Produces: setting `TABLER_ICON_ALIASES: dict[str, str]` (semantic name → Tabler icon name, no prefix). `{% icon name css %}` resolves `name` through it first; unknown names fall through unchanged.

- [ ] **Step 1: Branch.** `cd ../tabler-test && git switch -c semantic-icons`
- [ ] **Step 2: Write the failing tests**

```python
@override_settings(TABLER_ICON_ALIASES={"customer": "building-store"})
class IconAliasTests(SimpleTestCase):
    def test_alias_renders_the_mapped_icon(self):
        self.assertEqual(render('{% load tabler %}{% icon "customer" %}'),
                         render('{% load tabler %}{% icon "building-store" %}'))
    def test_unaliased_name_renders_directly(self):
        self.assertIn("<svg", render('{% load tabler %}{% icon "coffee" %}'))
    def test_alias_keeps_the_css_class(self):
        self.assertIn('class="icon icon-sm"', render('{% load tabler %}{% icon "customer" "icon-sm" %}'))
```
(`render` = `Template(s).render(Context())`, using the file's existing helper if it has one.)

- [ ] **Step 3: Run.** `uv run pytest tests/django_tabler --ds tests.django_tabler.settings -k IconAlias`. Expected: the first test FAILS.
- [ ] **Step 4: Implement.** In `icon`, `name = getattr(settings, "TABLER_ICON_ALIASES", {}).get(name, name)` before `svg(...)`.
- [ ] **Step 5: Run.** Same command. Expected: PASS.
- [ ] **Step 6: Document** the setting in `docs/icons.md` (one paragraph plus an example). Commit: `git commit -am "Shell: TABLER_ICON_ALIASES for template icons"`.

### Task 2: Tabler: semantic icon names in the Acme app

**Files:**
- Create: `../tabler-test/example/config/icons.py`
- Modify: `../tabler-test/example/config/settings.py`; every file from `grep -rln '"tabler:' example --include=*.py` (12 files) and the 2 templates with `tabler:`; the `{% icon %}` calls in `example/**/*.html` whose names are domain concepts (not UI chrome like `sun`/`moon`/`settings`)
- Modify: `../tabler-test/dev/crud_views_upstream_findings_roastery.md` (new finding: semantic names, cross-reference the CoreUI tracker U7)
- Test: `../tabler-test/example/dashboard/tests.py` (new `IconVocabularyTests`)

**Interfaces:**
- Produces: `example/config/icons.py: ACME_ICONS: dict[str, str]`, semantic name → library-native icon name (no prefix). The CoreUI copy (Task 8) keeps the **keys** and changes the values.
- Settings: `CRUD_VIEWS_ICONS = {k: f"tabler:{v}" for k, v in ACME_ICONS.items()}`, `TABLER_ICON_ALIASES = ACME_ICONS`.

- [ ] **Step 1: Write the failing test** (`IconVocabularyTests` in `dashboard/tests.py`):
  - `test_example_code_names_no_library`: no `"tabler:` string in any `example/**/*.py` except `config/settings.py`/`config/icons.py`.
  - `test_every_semantic_name_has_an_svg`: for each key in `ACME_ICONS`, `crud_views.lib.icons.resolve_icon(key)` returns `("tabler", name)` with `name in django_tabler.icons.ICONS`.
- [ ] **Step 2: Run.** `cd example && uv run pytest dashboard/tests.py -k IconVocabulary`. Expected: FAIL (`tabler:` strings found).
- [ ] **Step 3: Implement.** Pick one semantic name per domain concept (customer, order, subscription, product, beans, equipment, category, lot, cupping, batch, shipment, address, packing-slip, duplicate, run-subscriptions, …). Write `ACME_ICONS`, replace the strings and template names, add both settings.
- [ ] **Step 4: Run** `task test` in `../tabler-test`. Expected: all suites green, `check --fail-level WARNING` clean.
- [ ] **Step 5: Log the finding, commit, push the branch:** `git commit -am "Example: semantic icon names (ACME_ICONS)" && git push -u origin semantic-icons`. Tell the user the branch is ready for review and merge. Task 8 copies the example from this branch's HEAD.

### Task 3: Repository scaffold and tooling

**Files:**
- Delete: `src/django_crud_views_core_ui/`
- Create/replace: `pyproject.toml`, `noxfile.py`, `Taskfile.yaml`, `.pre-commit-config.yaml`, `mkdocs.yml`, `CHANGELOG.md`, `LICENSE`, `README.md` (stub), `CLAUDE.md` (stub), `scripts/check_dist.py`, `scripts/check_release_floor.py`, `src/django_coreui/{__init__,apps}.py`, `src/crud_views_coreui/{__init__,apps}.py`, `tests/__init__.py`, `tests/django_coreui/{__init__,settings,test_package,test_check_dist,test_release_floor}.py`, `docs/index.md`, `dev/README.md`
- Port from `../tabler-test`, renaming: `pyproject.toml` (name, description, wheel packages, coverage sources, bumpversion files, `[project.urls]` → `jacob-consulting/django-crud-views-coreui`, ruff per-file-ignore on `src/django_coreui/icons.py`), `noxfile.py` (`SUITES`, `_INSTALLED_PROJECT_ORIGIN`), `Taskfile.yaml`, the two scripts and their tests.

**Interfaces:**
- Produces: `django_coreui.__version__ = "0.1.0"`, `crud_views_coreui.__version__ = "0.1.0"`; `DjangoCoreuiConfig` (`name="django_coreui"`), `CrudViewsCoreuiConfig` (`name="crud_views_coreui"`, empty `ready()` for now). The suite paths `tests/{crispy_coreui,crud_views_coreui,django_coreui}` with settings modules `tests.<suite>.settings`.

- [ ] **Step 1: Write the failing tests.** Port `tests/django_tabler/test_package.py` (version strings match `pyproject.toml`), `test_check_dist.py` and `test_release_floor.py`.
- [ ] **Step 2: Run.** `uv run pytest tests/django_coreui --ds tests.django_coreui.settings`. Expected: FAIL (packages missing).
- [ ] **Step 3: Implement** the files above. `LICENSE` is MIT, "Copyright (c) 2026 Jacob Consulting". `CHANGELOG.md` has an "Unreleased" heading. README stub: one paragraph plus the CoreUI Icons CC BY 4.0 attribution.
- [ ] **Step 4: Run** `uv sync --extra examples --extra test --extra dev && uv run pytest -n auto tests/django_coreui --ds tests.django_coreui.settings && uv run ruff check . && uv build && uv run python scripts/check_dist.py dist/*`. Expected: tests PASS, ruff clean, check_dist OK.
- [ ] **Step 5: Commit.** `git add -A && git commit -m "Scaffold django-crud-views-coreui: packaging, nox, Taskfile, release guards"`

### Task 4: `django_coreui` page shell

**Files:**
- Create: `src/django_coreui/icons.py`, `src/django_coreui/conf.py`, `src/django_coreui/checks.py`, `src/django_coreui/templatetags/{__init__,coreui}.py`, `scripts/vendor_icons.py`
- Create templates under `src/django_coreui/templates/`: `django_coreui/base.html`, `django_coreui/layouts/app.html`, `django_coreui/includes/{assets,head,site_name,brand,nav_menu,layout_defaults,user_menu_items,messages,layout_switch_menu,sidebar,header}.html`, `registration/login.html`
- Create static: `src/django_coreui/static/django_coreui/{django_coreui.css,layout-switch.js}`
- Test: `tests/django_coreui/test_django_coreui.py` (port of `test_django_tabler.py`), `tests/django_coreui/test_icons.py`

**Interfaces:**
- `django_coreui.icons.ICONS: dict[str, str]`: CoreUI free icon name (`"cil-people"`) → inner SVG markup (viewBox 512). Generated by `scripts/vendor_icons.py NAME…`, which reads `@coreui/icons@3.1.0` (`js/free/<camelName>.js` from jsDelivr) and rewrites the dict, sorted. The header comment carries the CC BY 4.0 attribution and the version.
- `django_coreui.icons.svg(name: str | None, css: str = "") -> SafeString`: `<svg xmlns=… viewBox="0 0 512 512" aria-hidden="true" focusable="false" class="icon {css}">…</svg>`. Empty for no name or an unknown name.
- `django_coreui.icons.resolve(name: str) -> str`: applies `settings.COREUI_ICON_ALIASES`.
- `django_coreui.conf.coreui_settings() -> dict` (defaults `{"edition": "free"}`), `EDITIONS = ("free",)`.
- `django_coreui.assets`: constants `COREUI_VERSION = "5.9.1"`, `COREUI_CSS`, `COREUI_CSS_SRI`, `COREUI_JS`, `COREUI_JS_SRI`. The SRI values are computed in Step 3 with `curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A`.
- Check `django_coreui.E001`: edition not in `EDITIONS`.
- Tags `{% load coreui %}`: `icon(name, css_class="")` (via `resolve`, then `svg`), `initials`, `avatar_color`, `form_control`, `message_alert`, `layout_defaults_attrs` (same contracts as `{% load tabler %}`).
- `COREUI_LAYOUT_DEFAULTS = {"theme": "auto", "sidebar": "default"}`, accepted values `theme ∈ {light, dark, auto}`, `sidebar ∈ {default, narrow, unfoldable}`. `layout_defaults_attrs` emits `data-coreui-theme="…"` (if not `auto`), `data-coreui-sidebar="…"` (if not `default`) and `data-coreui-layout-defaults='<json>'`. It raises `ValueError` on bad input.
- `app.html` blocks, same names and order as Tabler's: `title`, `extra_head`, `page_header_before`, `page_header_top`, `breadcrumb`, `page_heading` (wraps `page_title`), `subtitle`, `actions`, `messages`, `content`, `extra_js`. Sidebar `#sidebar.sidebar.sidebar-dark.sidebar-fixed.border-end`; header toggler `onclick` toggles `coreui.Sidebar.getInstance(#sidebar)`. `nav_menu.html` is included once, inside `.sidebar-nav`.
- `layout-switch.js` handles colour mode (light/dark/auto, follows `prefers-color-scheme` in auto) and sidebar narrow/unfoldable. It stores a choice only when it differs from the project default. For storage keys it uses the free template's colour-mode script's mechanism; record the key names in `docs/layouts.md` (Task 10).

- [ ] **Step 1: Vendor the icons.** Write `scripts/vendor_icons.py` and run it with the names needed now: the semantic map in Task 6, the shell's own (sun, moon, contrast, settings, user, account-logout, menu, code, search, bug, info, check-circle, warning, x-circle) and Acme's values (Task 8; may be extended then).
- [ ] **Step 2: Write the failing tests.** Port every `test_django_tabler.py` test and adapt it to CoreUI markup: messages map to `alert alert-<level>`, package works without crispy, no `crud_views` reference (grep), default includes empty, header actions wrap, layout defaults (package default emits nothing; project JSON becomes `data-coreui-*` plus the JSON attribute; unknown keys and odd values raise). Add:
  - `test_icon_alias` with `@override_settings(COREUI_ICON_ALIASES={"customer": "cil-people"})`
  - `test_unknown_icon_renders_nothing`
  - `test_assets_pin_version_and_sri`: rendered `base.html` contains `@coreui/coreui@5.9.1`, `integrity="sha384-`, `crossorigin="anonymous"`
  - `test_unknown_edition_is_an_error`: `@override_settings(COREUI={"edition": "pro"})` → `django_coreui.E001` in `run_checks()`
  - `test_layout_has_the_tabler_block_contract`: a child template filling every block name above renders each one
  - `test_no_data_bs_attributes`: rendered `app.html` and `login.html` contain no `data-bs-`
- [ ] **Step 3: Run.** `uv run pytest tests/django_coreui --ds tests.django_coreui.settings`. Expected: FAIL.
- [ ] **Step 4: Implement** the files listed. Base the markup on the free admin template's `index.html` and `login.html` (sidebar, wrapper, header with breadcrumb row, body, footer).
- [ ] **Step 5: Run.** `uv run pytest -n auto tests/django_coreui --ds tests.django_coreui.settings`. Expected: PASS.
- [ ] **Step 6: Commit.** `git add -A && git commit -m "Shell: django_coreui layout, sign-in, icons, colour-mode and sidebar switch"`

### Task 5: `crispy_coreui` template pack

**Files:**
- Create: `src/django_coreui/crispy/{__init__,vendored,layout,fields,widgets}.py`, `src/django_coreui/templatetags/crispy_coreui_field.py`, `src/django_coreui/templates/crispy_coreui/**` (vendored), `scripts/vendor_templates.py`
- Test: `tests/crispy_coreui/` (port all of `tests/crispy_tabler/`)

**Interfaces:**
- `vendored.py`: `CRISPY_BOOTSTRAP5_VERSION = "2026.9"`, `CRISPY_BOOTSTRAP5_COMPATIBLE = ("2026.3", "2026.9")`, `HAND_EDITED: tuple[str, ...]`, `INCLUDE_PREFIX` (→ `crispy_coreui/`), `DATA_PREFIX = re.compile(r"\bdata-bs-")`, `UPSTREAM_SHA256`, and `rewrite(text: str) -> str`, which applies both rewrites. The vendoring script and the parity test both use `rewrite`.
- Pack name `crispy_coreui`; `django_coreui.crispy.layout.FloatingField`/`Switch` subclass crispy-bootstrap5's.

- [ ] **Step 1: Port the tests.** Port `tests/crispy_tabler/*` → `tests/crispy_coreui/*`. Change `test_pack_parity.py` so each vendored file equals `provenance_line + rewrite(upstream)` except `HAND_EDITED`. Add `test_no_data_bs_in_pack`: no `data-bs-` in any pack template. The four upstream files with `data-bs-` (`accordion-group.html`, `layout/alert.html`, `layout/modal.html`, `layout/tab-link.html`) must come out with `data-coreui-`.
- [ ] **Step 2: Run.** `uv run pytest tests/crispy_coreui`. Expected: FAIL.
- [ ] **Step 3: Implement.** Port `scripts/vendor_templates.py` using `rewrite` and run it. Then decide each of Tabler's six hand-edits against CoreUI's form markup. Keep a file in `HAND_EDITED` only if CoreUI needs the change; record each decision in `dev/crispy_coreui_hand_edits.md` (one line each).
- [ ] **Step 4: Run.** `uv run pytest -n auto tests/crispy_coreui`. Expected: PASS. Also run under crispy-bootstrap5 2026.3: `uv run --with crispy-bootstrap5==2026.3 pytest -n auto tests/crispy_coreui`. Expected: PASS.
- [ ] **Step 5: Commit.** `git add -A && git commit -m "Crispy: crispy_coreui pack vendored from crispy-bootstrap5 with data-coreui attributes"`

### Task 6: `crud_views_coreui` registration: buttons, icons, adapters, CSS, check

**Files:**
- Create: `src/crud_views_coreui/{buttons,icons,checks}.py`, `src/crud_views_coreui/static/crud_views_coreui/{coreui-adapters.js,crud_views_coreui.css}`
- Modify: `src/crud_views_coreui/apps.py` (`ready()`, as `CrudViewsTablerConfig.ready()`)
- Create: `tests/crud_views_coreui/{__init__,settings,urls}.py`, `tests/crud_views_coreui/testapp/**` (port), `tests/crud_views_coreui/test_registration.py`
- Modify: `superpowers/notes/upstream-tracker.md` (U4 and U5 → confirmed, with the theme code that works around them)

**Interfaces:**
- `COREUI_BUTTON_CLASSES: dict[str, str]` has **exactly the key set** of `crud_views_tabler.buttons.TABLER_BUTTON_CLASSES`, with CoreUI values. Mappings: Tabler `btn-ghost-*` → CoreUI `btn-ghost-*`; `btn-icon` → dropped (CoreUI has no `btn-icon`; square via `crud_views_coreui.css` `.cv-coreui-icon-btn`, added to every `:icon` key); `bg-*-lt` → `bg-*-subtle text-*-emphasis`; `btn-list` → `d-flex flex-wrap gap-2`; `nav-bordered` → `nav nav-underline-border`; named colours with no CoreUI token (azure, pink, …) → the closest CoreUI colour, noted in a comment.
- `COREUI_ICONS: dict[str, str]`: the same keys as `TABLER_ICONS`, values `coreui:cil-…`.
- `crud_views_coreui.icons.render(name, *, css, config) -> SafeString` → `django_coreui.icons.svg`.
- Check `crud_views_coreui.W001`: a port of `check_tabler_icons`.
- `coreui-adapters.js`: `Object.assign(cv.adapters, cv.bootstrapAdapters(() => globalThis.coreui))`, then wrap `tooltip.init` as Tabler does, setting `data-coreui-placement` (not `data-bs-placement`).
- CSS: a `[data-cv-manage]` and formset rule block that defines every `--bs-*` read by `crud_views/css/manage.css` and `formset.css` (13 references) from the matching `--cui-*`.

- [ ] **Step 1: Write the failing tests** (`test_registration.py`):
  - `test_button_keys_match_tabler`: key-set equality with a frozen copy of Tabler's keys in the test file. Don't import tabler.
  - `test_icon_keys_cover_crud_views_defaults`: every key of `crud_views.lib.icons.DEFAULT_ICONS` is in `COREUI_ICONS`
  - `test_every_coreui_icon_has_an_svg`
  - `test_w001_flags_missing_svg` with `CRUD_VIEWS_ICONS={"detail": "coreui:cil-nope"}`
  - `test_assets_registered`
  - `test_css_maps_every_bs_variable_upstream_reads`: parse `--bs-[a-z-]+` from the two upstream CSS files on disk (via `crud_views.__file__`); each must be defined in `crud_views_coreui.css`
  - `test_adapter_script_uses_coreui_namespace_and_wraps_tooltip_init`: string checks for `globalThis.coreui`, `const init = cv.adapters.tooltip.init`, `data-coreui-placement`
- [ ] **Step 2: Run.** `uv run pytest tests/crud_views_coreui --ds tests.crud_views_coreui.settings -k registration`. Expected: FAIL.
- [ ] **Step 3: Implement** the files above.
- [ ] **Step 4: Run.** Same command with `-n auto` and no `-k`. Expected: PASS.
- [ ] **Step 5: Commit** with the tracker update. `git commit -m "Theme: crud_views_coreui button classes, icons, adapters, CSS tokens, W001"`

### Task 7: `crud_views_coreui` page and template overrides

**Files:**
- Create: `src/crud_views_coreui/templates/crud_views_coreui/page.html` (port), `src/crud_views_coreui/templatetags/{__init__,crud_views_coreui}.py` (port, `cv_coreui_heading_repeats_tab`)
- Create layout overrides under `src/crud_views_coreui/templates/crud_views/`. Start from Tabler's (`modal/shell.html`, `snippets/form_frame.html`, `table/bootstrap5.html`, `tags/{alert,card,list_filter,list_filter.inner}.html`, `view_card.content.html`) and keep each one only if a test shows stock markup is wrong under CoreUI.
- Create `data-bs` overrides: `crud_views/tags/actions_menu_toggle.html`, `crud_views/snippets/language_selector.html`, `crud_views_object_detail/layouts/tabs-vertical/object_detail.html`, `crud_views_object_detail/layouts/accordion/group.html`. Each is a copy of upstream @ `fa2f0a7b` with only `data-bs-` → `data-coreui-` changed, plus a first-line comment naming the upstream path and commit.
- Object-detail tabs: `tabs.js` selects `[data-bs-toggle=…]` (tracker U2). Add `src/crud_views_coreui/static/crud_views_coreui/coreui-tabs.js`, registered in `ready()`, which initialises `[data-coreui-toggle="tab"|"pill"|"list"]` through `cv.adapters.tab.init`. Keep upstream's `tabs.js` loaded; it finds nothing and does nothing.
- Test: `tests/crud_views_coreui/test_theme.py` (port of Tabler's 97 tests)
- Modify: `superpowers/notes/upstream-tracker.md` (U1–U3 confirmed, naming each override; U8 status after comparing `apps.py` with Tabler's)

**Interfaces:**
- Consumes: Task 4 blocks, Task 6 class keys.
- Produces: `CRUD_VIEWS_EXTENDS = "crud_views_coreui/page.html"`, `DJANGO_TABLES2_TEMPLATE = "crud_views/table/bootstrap5.html"` (whether or not the theme overrides it).

- [ ] **Step 1: Port the tests.** Port `test_theme.py` with CoreUI expectations, plus:
  - `test_no_data_bs_on_any_testapp_page`: every testapp URL rendered as a superuser; the response has no `data-bs-`
  - `test_actions_menu_toggle_uses_coreui_dropdown`: `data-coreui-toggle="dropdown"` and, on lists, `data-coreui-popper-config`
  - `test_data_bs_overrides_track_upstream`: for each of the four overrides, `override == header + upstream_text.replace("data-bs-", "data-coreui-")`, with the upstream file read from the installed `crud_views`/`crud_views_object_detail`. This fails when upstream changes the file.
  - `test_heading_repeats_tab` cases ported
- [ ] **Step 2: Run.** `uv run pytest tests/crud_views_coreui --ds tests.crud_views_coreui.settings`. Expected: FAIL.
- [ ] **Step 3: Implement** `page.html`, the tag library, the four rename overrides and `coreui-tabs.js`. Then add the layout overrides one at a time, each driven by a failing ported test.
- [ ] **Step 4: Run** `uv run pytest -n auto tests/crud_views_coreui --ds tests.crud_views_coreui.settings`. Expected: PASS.
- [ ] **Step 5: Commit** with the tracker update. `git commit -m "Theme: CoreUI page, layout overrides, data-coreui overrides, object-detail tabs"`

### Task 8: Example: copy and rewire

**Files:**
- Copy: `../tabler-test/example/` at the HEAD of branch `semantic-icons` → `example/`. Leave out `config/{settings_demo,urls_demo,ratelimit,boot}.py`, `config/test_{demo,ratelimit,boot}.py`, `db.sqlite3`, `media/`, `staticfiles/`.
- Rename: `example/templates/django_tabler/` → `example/templates/django_coreui/`
- Modify: `example/config/settings.py` (apps, `CRISPY_TEMPLATE_PACK = "crispy_coreui"`, `CRISPY_ALLOWED_TEMPLATE_PACKS = ("crispy_coreui",)`, `COREUI = {"edition": "free"}`, `CRUD_VIEWS_ICONS = {k: f"coreui:{v}" for k, v in ACME_ICONS.items()}`, `COREUI_ICON_ALIASES = ACME_ICONS`, hosts per Global Constraints, no `CSRF_TRUSTED_ORIGINS` entry), `example/config/icons.py` (same keys, `cil-*` values), `example/templates/project/crud_views.html` (extends `crud_views_coreui/page.html`), every `{% load tabler %}` → `{% load coreui %}`
- Modify: `Taskfile.yaml` tasks that reference the example (already ported in Task 3; check paths)

- [ ] **Step 1: Copy and rewire** as listed. Run `scripts/vendor_icons.py` for any `cil-*` values that are missing.
- [ ] **Step 2: Run** `uv run python example/manage.py check --fail-level WARNING`. Expected: no issues (W001 clean).
- [ ] **Step 3: Run** `task setup`. Expected: migrate and seed succeed. `cd example && uv run pytest -n auto`: record which tests fail on Tabler markup. Those failures are Task 9's work list.
- [ ] **Step 4: Commit.** `git add -A && git commit -m "Example: Acme Roasters copied from django-crud-views-tabler and rewired to CoreUI"`

### Task 9: Example: CoreUI markup and green tests

**Files:**
- Modify the templates that use Tabler classes directly: `example/dashboard/templates/dashboard/{index,user_list}.html`, `example/sales/templates/sales/{order_detail,packing_slip}.html`, `example/sales/templates/sales/snippets/*.html`, `example/catalog/templates/catalog/product_card.html`, `example/roastery/templates/roastery/session_detail.html`, `example/shipping/templates/shipping/shipment_detail.html`, `example/showcase/templates/showcase/showcaseitem_detail.html`, `example/templates/project/{theming,code_panel,code_panel_shell,429}.html`, `example/templates/registration/login.html`, `example/templates/django_coreui/includes/*.html`
- Modify: `example/config/templatetags/acme_nav.py` (vertical-only output; drop the horizontal dropdown branch), `example/static/acme/acme.css` (sienna through `--cui-primary`, `--cui-primary-rgb`, `--cui-link-color`, button vars), `example/dashboard/static/dashboard/*` if they read `--tblr-*`
- Modify: example tests (`example/*/tests.py`, `example/sales/tests/*`), adapted to CoreUI markup; drop the tests for the top-bar layout and the Tabler layout switch, replace them with colour-mode/sidebar equivalents
- Test: `example/dashboard/tests.py` (new `CoreuiPagesTests`, `IconVocabularyTests` port)

- [ ] **Step 1: Write the failing tests:**
  - `test_every_page_has_no_data_bs`: as `alex`, GET every URL from `/`, the sidebar menu, one list/detail/update/create per ViewSet, `/showcase/`, `/theming/`, `/users/`, a manage page. Each returns 200 and has no `data-bs-` in the body.
  - `IconVocabularyTests` ported from Task 2 with `coreui` and `django_coreui.icons.ICONS`
  - `test_no_tabler_left`: no `tabler` (case-insensitive) in any `example/**/*.{py,html,css,js}` except comments that credit the origin
- [ ] **Step 2: Run.** `cd example && uv run pytest -n auto`. Expected: FAIL (the list from Task 8 Step 3 plus the new tests).
- [ ] **Step 3: Rewrite** the templates, nav, CSS and tests above until it passes.
- [ ] **Step 4: Run** `task test`. Expected: every suite green, check clean.
- [ ] **Step 5: Commit.** `git commit -am "Example: CoreUI markup, sienna brand, tests green"`

### Task 10: Docs

**Files:**
- Create: `docs/{installation,branding,layouts,icons,crispy_coreui,theme_internals,demo,development}.md`, port each from `../tabler-test/docs/` (`theme_internals.md` describes the CoreUI class table, the four data-bs overrides, the adapter, the CSS tokens, the edition seam)
- Modify: `mkdocs.yml` nav, `README.md` (full: what it is, run it with `task up`, demo accounts table, pages table, free vs PRO, CoreUI Icons attribution), `CLAUDE.md` (port of Tabler's, CoreUI facts: `data-coreui`, `window.coreui`, `--cui-*`, PRO material rule, the reference archive is local and unrecorded), `CHANGELOG.md`
- Create: `dev/` notes as needed (the crispy hand-edit decisions from Task 5 are already there)

- [ ] **Step 1: Write** the docs.
- [ ] **Step 2: Run.** `uvx nox -s docs`. Expected: mkdocs strict build passes.
- [ ] **Step 3: Commit.** `git add -A && git commit -m "Docs: user guide, README, CLAUDE.md"`

### Task 11: Matrix, browser pass, tracker close-out

- [ ] **Step 1: Run** `task test:matrix` (`uvx nox`). Expected: every `tests-*` and `examples-*` row passes or is skipped as unsupported (4.2 on 3.14/3.15); `package` and `docs` pass.
- [ ] **Step 2: Manual browser pass.** Run `task run` and sign in as alex, sam and kim. In light and dark mode, check: sidebar narrow/unfoldable and its mobile offcanvas, the colour-mode switch, `⋯` row menus, modals (create user, delete), tooltips (toolbar below, rows), filter collapse, object-detail tabs and accordion, formset add/remove rows, workflow transitions, ViewSet Navigation tabs, card view and order bar, typeahead and datetimepicker, manage page badges, the login page's demo buttons. Record each fix as a commit with a tracker entry where an upstream gap caused it.
- [ ] **Step 3: Update** `superpowers/notes/upstream-tracker.md`: every entry's status is confirmed or anticipated-not-hit, with the theme file that handles it. U8 has a verdict.
- [ ] **Step 4: Commit and push.** `git commit -am "Tracker: close-out after the browser pass" && git push`
