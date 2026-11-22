# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The distribution **django-crud-views-coreui** (repo `jacob-consulting/django-crud-views-coreui`): a CoreUI 5 (free
edition, 5.9.1) sister of django-crud-views-tabler, ported from `../tabler-test`. Two reusable packages under `src/`
and a demo project under `example/`. Supported: Python 3.12-3.15 x Django 4.2, 5.2, 6.1 (the nox matrix; 4.2 only on
3.12/3.13); local development runs Python 3.14 / Django 6.1.

- `src/django_coreui/`: CoreUI page shell (CSS and JS from the jsDelivr CDN, pinned with SRI hashes in `assets.py`),
  admin layout (sidebar, header with breadcrumb row), sign-in page, `{% load coreui %}` tags (`icon`, `initials`,
  `form_control`, ...), CoreUI Icons Free as SVG (`icons.py`), the end-user colour-mode and sidebar switch, **and** the
  django-crispy-forms template pack `crispy_coreui` (`templates/crispy_coreui/` + `django_coreui.crispy`). Must not
  import django-crud-views (a test greps the package), although the distribution depends on it.
- `src/crud_views_coreui/`: CoreUI theme for django-crud-views. Depends on `django_coreui`.
- `example/`: the Acme Roasters demo: `config/` (settings, `icons.py` with `ACME_ICONS`, the "Show code" collector
  `showcode.py`, tag libraries `showcode` and `acme_nav` registered in `TEMPLATES['OPTIONS']['libraries']` because
  `config` is not an app, date formats in `config/formats/`), apps `dashboard`, `sales`, `catalog`, `roastery`,
  `shipping` and `showcase` (the crispy pack coverage form). App code never imports `django_coreui` or
  `crud_views_coreui` (the showcase imports the pack's layout objects on purpose); icon names are semantic strings
  (`"customer"`), mapped to `cil-*` in `ACME_ICONS`.

`../django-crud-views` and `../django-crud-views-extensions` are editable path sources (`[tool.uv.sources]`), because the
theme tracks unreleased upstream features. Both checkouts are read-only for this repo: gaps are worked around here and
logged in `superpowers/notes/upstream-tracker.md`. nox installs django-crud-views from GitHub `main` (`CRUD_VIEWS` in
`noxfile.py`) until 1.0.0rc1 is on PyPI, and the declared floor stays lower; `scripts/check_release_floor.py` guards
the publish step.

## Commands

```shell
unset VIRTUAL_ENV   # before every uv / uvx command, if the parent environment sets one
task up             # Taskfile.yaml: uv sync --extra examples --extra test --extra dev, migrate, superuser, seed, runserver
task setup          # the same without runserver; idempotent
task reset          # delete example/db.sqlite3 + example/media, then setup (asks first)
task seed:reset     # seed_demo --reset: rebuild the demo data in place

# Always run test suites on all cores: pytest -n auto. Single-core only for one test or a -k selection.
uv run pytest -n auto tests/crispy_coreui                                              # crispy pack (default settings)
uv run pytest -n auto tests/crud_views_coreui --ds tests.crud_views_coreui.settings    # theme (own test app)
uv run pytest -n auto tests/django_coreui --ds tests.django_coreui.settings            # shell, packaging scripts
cd example && uv run pytest -n auto                                                    # demo apps (pytest-django)
task test          # all of the above plus the system check, against the sibling checkouts
task test:matrix   # uvx nox: tests, examples, package, docs
uv run python example/manage.py check --fail-level WARNING   # includes the coreui checks
uvx nox -s docs    # mkdocs, strict
uv run ruff format . && uv run ruff check .
```

System checks: `django_coreui.E001` (unknown `COREUI["edition"]`), `crud_views_coreui.E002` (theme listed after
`crud_views`), `crud_views_coreui.W001` (a `coreui:` icon without SVG).

## Architecture

**Template chain.** `django_coreui/base.html` <- `django_coreui/layouts/app.html` (sidebar, header, page header with
blocks `breadcrumb` (the header's second row), `page_header_before`, `page_header_top`, `pretitle`, `page_heading` (wraps
`page_title`), `subtitle`, `actions`, `messages`, `content`; base adds `title`, `extra_head`, `body`, `extra_js`) <-
`crud_views_coreui/page.html`, which is `CRUD_VIEWS_EXTENDS` and maps crud_views tags onto those blocks. Projects
customise branding by overriding `django_coreui/includes/{site_name,nav_menu,brand,head,layout_defaults,
user_menu_items}.html` (the example does so in `example/templates/`). There is one navigation, the sidebar;
`nav_menu.html` is included once, inside `ul.sidebar-nav`. The example's `CRUD_VIEWS_EXTENDS` is
`project/crud_views.html`, which extends the theme's page and adds the "Show code" panel.

**CoreUI facts.** CoreUI 5 is a Bootstrap 5 fork: same class names, but the JS namespace is `window.coreui`, the data
API reads only `data-coreui-*` (never `data-bs-*`), and the CSS custom properties are `--cui-*`. Everything in the theme
that looks odd exists because of one of those three.

**How the crud_views theme works** (details in `docs/theme_internals.md`): the theme is an app listed *before*
`crud_views`, so its templates shadow upstream's. Overrides: only `form_frame.html` and `table/bootstrap5.html` (layout:
a card; the table override extends upstream's and wraps three blocks). Everything else is registered in
`CrudViewsCoreuiConfig.ready()`:
- data-attribute prefix: `register_data_prefix("coreui")` (upstream #391), so upstream's templates and object-detail
  `tabs.js` write and read `data-coreui-*`,
- button classes: `buttons.COREUI_BUTTON_CLASSES` (the Tabler theme's keys with CoreUI values, plus `breadcrumb:list`
  = `breadcrumb my-0`; icon-only buttons get `cv-coreui-icon-btn`),
- label modes: `{"form": "both"}`,
- icons: the `coreui` library and `COREUI_ICONS` (semantic name -> `coreui:cil-*`); SVGs live in
  `django_coreui.icons.ICONS` (CoreUI Icons Free 3.1.0, CC BY 4.0; add icons with `scripts/vendor_icons.py`),
- JavaScript: `register_js_namespace("coreui")` and `register_tooltip_placements({"context": "bottom"})`
  (upstream #398, U4), so upstream's stock adapters use `window.coreui` and toolbar tooltips open below the buttons.
  The theme ships no script; the stock modal adapter follows the data prefix (upstream #403, U13),
- assets: `crud_views_coreui.css` (sets upstream's and the typeahead's `--cv-*` tokens from `--cui-*`,
  element-scoped, U5/U12, plus the theme's few rules).

Prefer solving theme problems through upstream hooks (class keys, blocks, settings) rather than new template overrides;
copied templates drift from upstream silently.

**crispy_coreui pack.** Vendored from crispy-bootstrap5 by `scripts/vendor_templates.py` (rewrites `bootstrap5/` includes
to `crispy_coreui/` and `data-bs-` to `data-coreui-`, adds a provenance comment, otherwise byte-identical). Two
templates are hand-edited (`HAND_EDITED` in `django_coreui/crispy/vendored.py`; why: `dev/crispy_coreui_hand_edits.md`)
and the script refuses to overwrite them without `--force`; files under `widget/` are pack-owned.
`CRISPY_BOOTSTRAP5_VERSION` (2026.9) is the vendored release; the installed one must be in
`CRISPY_BOOTSTRAP5_COMPATIBLE` (2026.3 for Django 4.2, 2026.9), which nox pins per Django version.

**Layout switch.** The header gear (`layout_switch_menu.html` + `static/django_coreui/layout-switch.js`) stores the
user's colour mode and sidebar state in `localStorage` under `django-coreui-theme` (`light|dark|auto`) and
`django-coreui-sidebar` (`default|narrow|unfoldable`). A project's *default* is the JSON object in
`django_coreui/includes/layout_defaults.html` (keys `theme`, `sidebar`; anything else raises `ValueError`); the
`{% layout_defaults_attrs %}` tag on `<html>` turns it into `data-coreui-theme`, `data-coreui-sidebar` and
`data-coreui-layout-defaults`. A choice equal to the default is not stored.

**Edition seam.** `settings.COREUI = {"edition": "free"}`; `django_coreui.conf.EDITIONS = ("free",)`. Only
`includes/assets.html` reads the edition. A PRO edition is a later, separate design; see
`superpowers/specs/2026-11-20-coreui-theme-design.md`.

## Conventions

- All pages require login (`LoginRequiredMiddleware`); the login view is the exception.
- Settings from env: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1`/`0`), `DJANGO_ALLOWED_HOSTS`,
  `CRUD_VIEWS_MANAGE_VIEWS_ENABLED` (default `yes`).
- Demo accounts: `alex` (Owner; the only member of the `CRUD_VIEWS_MANAGE` group), `sam` (Account managers; Guardian
  grants on their own customers), `kim` (Roasters); password `demo`. `admin`/`admin` is the superuser from the Taskfile.
  Brand "Acme Roasters", primary colour sienna `#a0522d` (`example/static/acme/acme.css`).
- Theme fix order: an upstream hook (class keys, settings, blocks), then CSS in `crud_views_coreui.css`, then a new
  override template as a last resort.
- **Upstream tracker rule:** every theme template override, theme CSS rule or demo workaround that exists because of an
  upstream gap gets an entry in `superpowers/notes/upstream-tracker.md` in the same change that adds it.
- Design specs, implementation plans and notes live in `superpowers/{specs,plans,notes}/`. `docs/` is the published user
  guide (mkdocs, strict); maintainer notes live in `dev/`, which is not published.
- Ruff with django-crud-views' configuration; run `uv run ruff format . && uv run ruff check .` after touching Python.

## CoreUI PRO material

**Never commit CoreUI PRO material**: PRO SCSS, compiled PRO CSS/JS, markup copied from the PRO admin templates, text
copied from the PRO documentation. The repository is public and the PRO licence is commercial; this includes any file
derived from those, and the history. The maintainer keeps the PRO archives locally, outside this repository (the path
is deliberately not recorded here; ask for it). Use them as reference only. The free edition's sources (MIT) are fine:
`@coreui/coreui`, `@coreui/icons` (icons CC BY 4.0, keep the attribution) and the free admin template.
