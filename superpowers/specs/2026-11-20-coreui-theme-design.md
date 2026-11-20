# CoreUI theme for django-crud-views (free edition): design

Date: 2026-11-20 · Status: approved

## Intent

**django-crud-views-coreui** (repo `jacob-consulting/django-crud-views-coreui`, public) is the CoreUI sister of
**django-crud-views-tabler** (local checkout `../tabler-test`, repo `jacob-consulting/django-crud-views-tabler`). Both
are **public showcases of what it takes to adapt django-crud-views to a UI theme**: a reusable page-shell package, a
reusable crud_views theme package, and the same demo app (Acme Roasters) on top, with the app code never importing
either package.

The project will ship a **free** and a **PRO** CoreUI edition. This design covers the **free edition only**
(CoreUI 5, MIT). PRO is a later, separate design that plugs into one seam left open here (see "Edition seam").

## Goals

1. `src/django_coreui/`: CoreUI 5 page shell (sidebar + header + footer layout, sign-in page, icon template tags,
   messages, colour-mode and sidebar switch) **and** the django-crispy-forms template pack `crispy_coreui`. Must not
   import django-crud-views (a test greps the package, as in Tabler). Counterpart of `django_tabler`.
2. `src/crud_views_coreui/`: the CoreUI theme for django-crud-views. Depends on `django_coreui`. Counterpart of
   `crud_views_tabler`, built with the same method (below), covering everything the Tabler theme covers at
   `../tabler-test` HEAD (`7165eaf`), including ViewSet Navigation (`cv_navbar_items`, upstream #383), the navbar
   class keys (#384/#386) and the object header layout.
3. `example/`: Acme Roasters copied from `../tabler-test/example/`, re-skinned to CoreUI, every page working
   (dashboard, sales, catalog, roastery, shipping, showcase, theming page, users, "Show code" panel, manage pages).
4. **Semantic icon names in both demos** (approved): the Acme app names icons by meaning (`"customer"`), each project
   maps them to its library. Done in `../tabler-test` too, so the two Acme copies stay identical.
5. Repo shape and local tooling mirror `../tabler-test` (approved scope, see "Packaging and tooling").
6. Tests at parity with the Tabler suites, all green across the local nox matrix.
7. `superpowers/notes/upstream-tracker.md` kept current: every override/CSS rule/workaround caused by an upstream
   gap is logged in the same commit.

## Non-goals

- PRO edition, PRO widgets (date/time/date-range picker, multi-select), PRO admin-template looks (modern, bright).
- A top-bar (horizontal) layout. CoreUI's admin layout is sidebar-first; sidebar-only was approved.
- GitHub-facing infrastructure in this build: GitHub workflows, Read the Docs, PyPI publish, the Render demo
  (`render.yaml`, `settings_demo`, ratelimit, `boot.py`). A follow-up design, once the code exists. *(Approved.)*
- Changing django-crud-views or django-crud-views-extensions. Both sibling checkouts are read-only; gaps go to the
  tracker.
- Sharing code with the Tabler project (no common base package). Copy now; tracker U8 records whether a shared
  abstraction is worth proposing later.

## Anti-goals (would make this a failure even if it works)

- **Any CoreUI PRO material in the repo or its history**: PRO SCSS, compiled PRO CSS/JS, markup copied from the PRO
  admin-template zips, PRO docs text. The repo is public and the PRO licence is commercial. The PRO archives (kept
  outside the repo by the maintainer; not recorded here, as Tabler does with its archives) are visual reference only.
- A JavaScript shim that rewrites `data-bs-*` to `data-coreui-*` at runtime. The showcase teaches explicit theme code.
- Patching or subclassing crud_views code.
- Breaking the Tabler project while changing its icon names (its full `task test` stays green).

## Constraints

- Python 3.12–3.15 × Django 4.2, 5.2, 6.1 (4.2 only on 3.12/3.13), as `../tabler-test/noxfile.py`. Local
  development: Python 3.14 / Django 6.1. Dependencies and extras (`examples`, `test`, `dev`) as in
  `../tabler-test/pyproject.toml`; same editable path sources `../django-crud-views` and
  `../django-crud-views-extensions`, same declared floor and the same "install crud-views from GitHub `main` in nox"
  arrangement until 1.0.0rc1 is on PyPI.
- django-crud-views reference: `main` @ `fa2f0a7b` (2026-11-19).
- CoreUI free from jsDelivr, pinned exact versions with SRI: `@coreui/coreui@5.9.1` (CSS + `coreui.bundle.min.js`,
  which includes Popper), `@coreui/icons@3.1.0` for icon paths (icons CC BY 4.0, code MIT: attribution in README and
  the `django_coreui/icons.py` header). Re-checked at build time.
- Shell markup reference: the **free** CoreUI admin template (MIT, `coreui/coreui-free-bootstrap-admin-template` on
  GitHub) and the free CoreUI docs.
- CoreUI's JavaScript only reacts to `data-coreui-*` and lives on `window.coreui`; its CSS variables are `--cui-*`.
  django-crud-views has **no** setting for the data-attribute prefix (hard-coded in four templates and `tabs.js`;
  tracker U1-U2).

## Approaches considered (for the `data-bs-*` gap)

- **A. Explicit template rewrite (picked by the user).** Vendor crispy-bootstrap5 into `crispy_coreui/` with a port of
  `../tabler-test/scripts/vendor_templates.py` that also rewrites `data-bs-` → `data-coreui-`. Override the crud_views
  templates that hard-code `data-bs-` in `crud_views_coreui`. Explicit, covered by the pack-parity test, no runtime
  magic. Cost: about 60 vendored files, and new upstream `data-bs` usages need noticing (a test catches them).
- **B. JS shim** copying `data-bs-*` to `data-coreui-*` on load and on DOM mutation, stock `bootstrap5` pack
  unchanged. Least code, but hides the problem, adds timing bugs with modal/filter content, teaches a hack. Rejected.
- **C. Bootstrap's own JS next to CoreUI's CSS.** CoreUI-only components (sidebar, navigation) need CoreUI's JS;
  two component libraries on one page double dropdown/modal handlers. Rejected.

## Design

### Packaging and tooling (mirror `../tabler-test`)

```
pyproject.toml        # name django-crud-views-coreui, hatchling, wheel = src/crud_views_coreui + src/django_coreui,
                      # sdist only-include list, ruff config, bump-my-version, coverage paths (as tabler-test)
noxfile.py            # tests-<py>(django), examples-<py>(django), package, docs sessions (as tabler-test)
Taskfile.yaml         # up, setup, seed, seed:reset, reset, test, test:matrix
.pre-commit-config.yaml, mkdocs.yml, CHANGELOG.md, LICENSE (MIT), README.md, CLAUDE.md, .gitignore
scripts/              # vendor_templates.py, check_dist.py, check_release_floor.py (ported)
src/django_coreui/, src/crud_views_coreui/   # each with __version__
example/              # Acme Roasters
tests/crispy_coreui/, tests/crud_views_coreui/, tests/django_coreui/   # pytest suites, own settings
docs/                 # published user guide (mkdocs): index, installation, branding, layouts, icons,
                      # crispy_coreui, theme_internals, demo, development
dev/                  # unpublished maintainer notes (as tabler-test/dev/)
superpowers/{specs,plans,notes}/   # designs, plans, the upstream tracker
```

The placeholder `src/django_crud_views_core_ui/`, its `[project.scripts]` entry and the `uv_build` backend are
removed. Lint: ruff with the Tabler/crud-views configuration. Tests run with `pytest -n auto`.

### `django_coreui`

- `templates/django_coreui/base.html`: `<html>` with `data-coreui-theme` (colour mode), assets from the edition
  include, project head include, body, CoreUI JS at the end.
- `templates/django_coreui/layouts/app.html`: CoreUI admin layout: `.sidebar.sidebar-fixed` (brand, `.sidebar-nav`
  from the `nav_menu` include, narrow/unfoldable toggler), `.wrapper` with `.header` (sidebar toggle, colour-mode
  dropdown, user menu) and a second header row for the breadcrumb, `.body` with the page header and content,
  `.footer`. **Blocks keep the Tabler names and contract**: `page_header_before`, `page_header_top`, `breadcrumb`,
  `page_heading` (wraps `page_title`), `subtitle`, `actions`, `messages`, `content`, so `page.html` maps the same way.
- Override points for projects: `django_coreui/includes/{site_name,nav_menu,brand,head,layout_defaults,`
  `user_menu_items,messages}.html`.
- `nav_menu.html` renders one vertical menu (sidebar `nav-title` headings + `nav-item`/`nav-group`); no horizontal
  variant. The example's menu stays defined once in `example/config/templatetags/acme_nav.py`.
- Switch: **colour mode (light/dark/auto) + sidebar state (narrow/unfoldable)**, CoreUI's own mechanisms and storage
  keys. Project default via `layout_defaults.html` → `{% layout_defaults_attrs %}` on `<html>`, same contract as Tabler.
- `registration/login.html`: CoreUI sign-in page (centred card, as the free template), with the demo-account buttons
  the example adds.
- `templatetags/coreui.py` (`{% load coreui %}`): `icon`, `initials`, `avatar_color`, `form_control`,
  `message_alert`, `layout_defaults_attrs`, same API as `{% load tabler %}`. `icon` renders inline SVG from
  `icons.py` (CoreUI free icon paths vendored from `@coreui/icons`, with attribution) and accepts **project aliases**
  from a setting `COREUI_ICON_ALIASES` (`{"customer": "cil-people"}`), so app templates use the same semantic names as
  app Python code without the shell importing crud_views (tracker U7).
- Static: `django_coreui/django_coreui.css`, `django_coreui/layout-switch.js` (pack-owned code, never copied PRO code).
- `crispy_coreui` pack: vendored from crispy-bootstrap5 by `scripts/vendor_templates.py` (provenance comment,
  `bootstrap5/` → `crispy_coreui/`, `data-bs-` → `data-coreui-`, otherwise byte-identical); `HAND_EDITED` protected
  without `--force`; `widget/` pack-owned. `django_coreui/crispy/vendored.py` carries `CRISPY_BOOTSTRAP5_VERSION` and
  `CRISPY_BOOTSTRAP5_COMPATIBLE` as Tabler does (nox pins per Django version). `django_coreui.crispy.layout`
  subclasses `FloatingField`/`Switch`. Each of Tabler's hand-edits is re-evaluated; kept only if CoreUI needs it.

### `crud_views_coreui`

Same method as `crud_views_tabler` (read `../tabler-test/docs/theme_internals.md`, `../tabler-test/CLAUDE.md` and
`../tabler-test/src/crud_views_tabler/`): an app listed **before** `crud_views` in `INSTALLED_APPS`, whose
`templates/crud_views/...` shadow stock templates; everything else falls through.

- `crud_views_coreui/page.html` = `CRUD_VIEWS_EXTENDS` target, extends `django_coreui/layouts/app.html`, maps
  `cv_navbar_items`, `cv_breadcrumb`, `cv_header_icon`/`cv_header`, `cv_paragraph`, `cv_context_actions`,
  `cv_filter`, `cv_content`, `cv_css`/`cv_js`/`cv_config` onto the layout blocks, as Tabler's `page.html` does.
- `templatetags/crud_views_coreui.py`: counterpart of `crud_views_tabler`'s tag library, whatever it carries.
- `ready()` registers:
  - button classes (`buttons.COREUI_BUTTON_CLASSES` via `register_button_classes()`): every key the Tabler table
    covers (locations × variants × `:icon`, `workflow:*`, `manage:*`, `card:*`, `card-order:*`, pagination, navbar
    keys) with CoreUI classes, chosen from CoreUI docs while building,
  - label-mode defaults (`{"form": "both"}`),
  - icon library `coreui` + `register_icons(COREUI_ICONS)` mapping crud_views' semantic names to `coreui:<name>`,
  - assets: `crud_views_coreui.css` and `coreui-adapters.js`.
- `coreui-adapters.js`: `cv.adapters = Object.assign(cv.bootstrapAdapters(() => window.coreui), …)`, keeping
  upstream's tooltip transition guard (wrap `init`, never replace it).
- System check `crud_views_coreui.W001`: `coreui:` icon names with no path in `django_coreui.icons`.
- Template overrides, two groups:
  1. **Layout**, only where CoreUI structure differs from stock Bootstrap 5. Start from Tabler's list (modal shell,
     form frame, table, card, alert, list filter, card content) and drop every one stock markup already renders
     correctly under CoreUI. Expect fewer than Tabler.
  2. **`data-bs` renames** (tracker U1-U3): `tags/actions_menu_toggle.html`, `snippets/language_selector.html`,
     `crud_views_object_detail` `tabs-vertical/object_detail.html` and `accordion/group.html`, plus whatever the
     object-detail tabs need given `tabs.js`'s hard-coded selector (override the script, or init the tabs from the
     theme's adapter script). Each gets a tracker entry.
- CSS `crud_views_coreui.css`: re-map the `--bs-*` variables upstream CSS reads from `--cui-*` (tracker U5), plus
  only what tests or the demo show is needed.
- Fix order: upstream hook first, then theme CSS, then an override as last resort.

### Edition seam (for the later PRO design)

All CoreUI CSS/JS tags come from one include, `django_coreui/includes/assets.html`, driven by
`settings.COREUI = {"edition": "free"}`; any other value is a system check error for now. Nothing else in either
package or the example branches on the edition.

### Example (Acme Roasters)

- Copy `../tabler-test/example/` at `7165eaf`, including `config/login_required.py` (the Django 4.2 stand-in) and the
  config tests that do not belong to the demo deployment. Leave out `settings_demo.py`, `urls_demo.py`,
  `ratelimit.py`, `boot.py` and their tests (follow-up, with Render).
- Rename the wiring: `INSTALLED_APPS` (`django_coreui`, `crud_views_coreui`), `CRISPY_TEMPLATE_PACK =
  "crispy_coreui"`, `CRUD_VIEWS_EXTENDS = "project/crud_views.html"` extending `crud_views_coreui/page.html`,
  `DJANGO_TABLES2_TEMPLATE`, `example/templates/django_coreui/includes/*`.
- Hosts: `DJANGO_ALLOWED_HOSTS` from env, default localhost; no `cv.jacob-consulting.org`, no `CSRF_TRUSTED_ORIGINS`
  entry. *(My call.)*
- Icons: semantic names in app code (goal 4). The mapping lives in `example/config/settings.py`
  (`CRUD_VIEWS_ICONS` for Python-side names, `COREUI_ICON_ALIASES` for template-side names), one table per project.
- App templates that use Tabler classes directly (dashboard, user list, order detail, packing slip, theming page,
  code panel, login extras) are rewritten in CoreUI markup.
- Dashboard charts stay ApexCharts. *(My call.)*
- Brand "Acme Roasters", primary sienna `#a0522d` through CoreUI's `--cui-primary*` variables in
  `example/static/acme/acme.css`.
- django-crud-views-extensions widgets (xdsoft datetimepicker, typeahead) as in Tabler; theme CSS if needed (logged).
- `/theming/` lists this project's theme files, computed at render time.

### Tabler-side change (icons)

In `../tabler-test`: replace the 47 `"tabler:<name>"` strings in `example/**/*.py` and the template `{% icon %}`
names with semantic names; add `CRUD_VIEWS_ICONS` and an equivalent template alias setting
(`TABLER_ICON_ALIASES`, read by `{% load tabler %}`'s `icon`) in `example/config/settings.py`. Same names in both
projects. Its own commit in that repo, with its `task test` green; logged in its findings file per its convention.

### Testing

- Port `tests/crud_views_tabler/`, `tests/crispy_tabler/`, `tests/django_tabler/` → `*_coreui`, rewriting
  expectations to CoreUI markup; port the example app tests.
- New theme test: render every example page (as `alex`) and assert no `data-bs-` attribute remains in the output.
- `manage.py check --fail-level WARNING`; `task test` (local checkouts) and `task test:matrix` (nox) green.
- A manual browser pass over every page in light and dark mode: dropdowns, modals, tooltips, tabs, accordions,
  collapses, filters, formsets, ViewSet Navigation, sidebar narrow/unfoldable.

## Left to the builder

- Exact CoreUI classes per button/badge/navbar key, chosen from CoreUI docs and checked in the browser.
- Which Tabler layout overrides are still needed under CoreUI (keep the list minimal).
- Which Tabler crispy hand-edits survive.
- The semantic icon vocabulary (names) for the Acme app.
- Phasing of the work (the plan).

## Decisions

From the user: free edition first, PRO later behind a seam; public repo; approach A (template rewrite); sidebar-only
layout; semantic icon names in both demos, including the Tabler-side change; repo shape and local tooling now,
GitHub-facing infrastructure later; specs/plans/tracker under `superpowers/`.

Calls made (not explicitly decided by the user): colour mode + sidebar state as the switch; ApexCharts kept;
shell markup from the free admin template; localhost-only hosts until the demo follow-up; pinned CoreUI versions;
`COREUI = {"edition": "free"}` as the PRO seam; `COREUI_ICON_ALIASES` / `TABLER_ICON_ALIASES` for template icons.
