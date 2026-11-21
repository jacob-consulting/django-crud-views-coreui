# Adopt today's upstream fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the theme's workarounds for tracker U1, U2, U5, U9, U10, U12 (and C8) with the hooks django-crud-views
`49d5173a` and django-crud-views-extensions 0.4.0 now provide.

**Architecture:** Registration moves into `CrudViewsCoreuiConfig.ready()` (`register_data_prefix("coreui")`, a
`breadcrumb:list` class key); copied templates, `coreui-tabs.js` and the copied `table.thead` block are deleted; the
theme CSS sets upstream's `--cv-*` tokens from `--cui-*` instead of re-mapping `--bs-*`. Drift tests that guarded the
copies are replaced by tests of the outcome.

**Tech Stack:** Django 6.1 / Python 3.14 locally, pytest + pytest-django, django-crud-views (editable `../django-crud-views`
@ `49d5173a`), CoreUI 5.9.1.

**Spec:** `superpowers/specs/2026-11-21-adopt-upstream-fixes-design.md`

## Global Constraints

- `../django-crud-views` (@ `49d5173a`) and `../django-crud-views-extensions` (@ `fd06c91`) are read-only.
- No fallback for older django-crud-views; no `--bs-*` fallback mapping for extensions < 0.4.0.
- U4 is out of scope: `coreui-adapters.js` and its tests stay unchanged.
- Tracker rule: every removed workaround's tracker entry is updated in the same change (Task 5 does the tracker in one
  go; each task's commit message names the entries it closes).
- Run suites with `-n auto`; `unset VIRTUAL_ENV` first; `uv run ruff format . && uv run ruff check .` after Python edits.
- Suites: `uv run pytest -n auto tests/crud_views_coreui --ds tests.crud_views_coreui.settings` (THEME below),
  `cd example && uv run pytest -n auto` (EXAMPLE).

## Review Focus

1. Object-detail tabs and accordions opened in a modal (`X-CV-Modal`) must still use `data-coreui-*` and the page must
   publish the prefix: Task 1 test `test_cv_config_publishes_the_coreui_prefix` covers full page and modal partial.
2. A theme or project app whose `ready()` runs after the theme and calls `register_data_prefix` wins (last call wins);
   the theme must not re-register later. Task 1: register in `ready()` only, no per-request call; covered by
   `test_data_prefix_is_coreui`.
3. Dark-mode subtrees: tokens must stay element-scoped, never on `:root` (a `:root` declaration resolves `--cui-*`
   once at the root and ignores `[data-coreui-theme]` subtrees). Task 4 test `test_cv_tokens_are_element_scoped`.
4. A project that overrides `breadcrumb:list` in `CRUD_VIEWS_BUTTON_CLASSES` loses `my-0`; documented in Task 3, not
   worked around.
5. The default-ordered list now shows a sort icon on first load (upstream's accepted change); Task 3's
   `test_sorted_column_is_marked` must not assume no icon without `?sort=`.

---

### Task 1: Register the `coreui` data prefix, drop the four template copies and `coreui-tabs.js` (U1, U2)

**Files:**
- Modify: `src/crud_views_coreui/apps.py` (`ready()`, asset bundle, comment)
- Delete: `src/crud_views_coreui/templates/crud_views/tags/actions_menu_toggle.html`,
  `src/crud_views_coreui/templates/crud_views/snippets/language_selector.html`,
  `src/crud_views_coreui/templates/crud_views_object_detail/` (both files, the directory goes),
  `src/crud_views_coreui/static/crud_views_coreui/coreui-tabs.js`
- Modify: `tests/crud_views_coreui/test_theme.py`, `tests/crud_views_coreui/test_registration.py`
- Modify: `docs/theme_internals.md` (sections "The four `data-bs` overrides", "Object-detail tabs (U2)", the template
  tree around line 115, the asset list at line 52)

**Interfaces:**
- Produces: `crud_views.lib.data_prefix.get_data_prefix() == "coreui"` after startup; asset bundle
  `crud_views_coreui` with js `["crud_views_coreui/coreui-adapters.js"]` only.

- [ ] **Step 1: Rework the tests.** In `test_theme.py`:
  - delete `DATA_BS_OVERRIDES`, `test_data_bs_overrides_track_upstream`, `test_upstream_tabs_script_still_selects_data_bs`,
    `test_tabs_script_is_registered_after_the_adapter` and the three `test_coreui_tabs_script_*` tests;
  - `test_no_new_upstream_data_bs_outside_the_overrides` -> rename `test_no_upstream_template_or_script_hard_codes_data_bs`,
    keep the scan, `expected = set()`; docstring: a hit means upstream added markup that bypasses `cv_data_prefix`;
  - `test_theme_overrides_exactly_these_templates`: the list is `form_frame.html`, `table/bootstrap5.html`,
    `crud_views_coreui/page.html`;
  - `test_tabs_vertical_pack_uses_coreui_pills`: drop the `coreui-tabs.js` assertion, keep upstream `tabs.js` loaded;
  - `test_scripts_use_the_coreui_adapter_without_jquery`: drop the `tabs` index and its `assertLess`;
  - add to the template-origin test (`test_upstream_templates_are_not_overridden`) the four formerly copied names;
  - add `test_cv_config_publishes_the_coreui_prefix`: for `customer-properties` and `customer-accordion`, full page
    contains `data-data-prefix="coreui"`; full page and `X-CV-Modal` partial contain `data-coreui-toggle=` and no
    `data-bs-`.
  In `test_registration.py`: `test_assets_registered` expects js `["crud_views_coreui/coreui-adapters.js"]`; add
  `test_data_prefix_is_coreui` (`from crud_views.lib.data_prefix import get_data_prefix`; `== "coreui"`).

- [ ] **Step 2: Run THEME.** Expected: `test_data_prefix_is_coreui`, `test_cv_config_publishes_the_coreui_prefix`,
  `test_assets_registered`, `test_theme_overrides_exactly_these_templates` and the origin test FAIL; others pass.

- [ ] **Step 3: Implement.** In `ready()`: `from crud_views.lib import register_data_prefix` and
  `register_data_prefix("coreui")` before the asset registration. Remove `coreui-tabs.js` from `register_assets`;
  update the comment above it (U2 sentence goes, add "the data-coreui prefix comes from register_data_prefix,
  upstream #391"). Delete the five files. Update the class docstring only if it mentions the overrides.

- [ ] **Step 4: Run THEME and EXAMPLE.** Expected: THEME passes except the Task 3/4 failures
  (`test_table_head_is_upstream_plus_aria_sort`, `test_css_maps_every_bs_variable_upstream_reads`); EXAMPLE fails only
  the three compact-heading tests (Task 4).

- [ ] **Step 5: Docs.** In `docs/theme_internals.md`, replace the two sections with one short "Data attributes (U1,
  U2)" section: the theme registers `coreui` with `register_data_prefix()`; upstream's templates and `tabs.js` read
  it; the theme keeps no copies. Fix the tree and asset list.

- [ ] **Step 6: Commit.** `git commit -m "feat: register the coreui data prefix, drop the data-bs overrides and coreui-tabs.js (U1, U2)"`

### Task 2: Narrow E002 to `crud_views` (U11)

**Files:**
- Modify: `src/crud_views_coreui/checks.py` (`OVERRIDDEN_APPS`, message, hint, comment)
- Modify: `tests/crud_views_coreui/test_registration.py` (`AppOrderCheckTests`)
- Modify: `docs/installation.md` (lines 29, 38, 91), `README.md:41`, `docs/theme_internals.md` (lines 25, 38, 140)

**Interfaces:**
- Produces: `OVERRIDDEN_APPS = ("crud_views",)`; E002 hint `"List crud_views_coreui before crud_views in INSTALLED_APPS."`

- [ ] **Step 1: Tests.** `test_theme_after_crud_views_is_an_error`: hint contains `"before crud_views in INSTALLED_APPS"`.
  `test_theme_after_object_detail_is_an_error` -> `test_theme_after_object_detail_passes` (`== []`).
  `test_theme_after_both_names_both` -> `test_theme_after_both_names_crud_views` (one message; msg contains
  `"'crud_views'"` and not `crud_views_object_detail`). Class docstring: overrides of `crud_views` templates only.
- [ ] **Step 2: Run** `uv run pytest tests/crud_views_coreui/test_registration.py -k AppOrder --ds tests.crud_views_coreui.settings`. Expected: the three changed tests FAIL.
- [ ] **Step 3: Implement.** `OVERRIDDEN_APPS = ("crud_views",)`; the comment names the two remaining overrides
  (`snippets/form_frame.html`, `table/bootstrap5.html`) and U11; message: "...after 'crud_views': its templates win
  over the theme's (the form frame and the card table lose their CoreUI layout)."
- [ ] **Step 4: Run THEME.** Expected: AppOrder tests pass.
- [ ] **Step 5: Docs.** Installation and README comments say "before crud_views"; the E002 row: "listed after
  `crud_views`". `crud_views_object_detail` may now come anywhere; say so once in `docs/installation.md`.
- [ ] **Step 6: Commit.** `git commit -m "feat: E002 checks only crud_views now that object-detail templates are stock (U11)"`

### Task 3: Breadcrumb class key and the stock table header (U9, U10, C8)

**Files:**
- Modify: `src/crud_views_coreui/buttons.py` (`COREUI_BUTTON_CLASSES`)
- Modify: `src/crud_views_coreui/static/crud_views_coreui/crud_views_coreui.css` (drop the `.header-breadcrumb .breadcrumb` rule)
- Modify: `src/crud_views_coreui/templates/crud_views/table/bootstrap5.html` (drop `{% block table.thead %}`, fix the comment)
- Modify: `tests/crud_views_coreui/test_theme.py`, `tests/crud_views_coreui/test_bulk.py`
- Modify: `docs/theme_internals.md` ("The table header override (U10)" section, the tree, the CSS list at line 205)

**Interfaces:**
- Produces: `COREUI_BUTTON_CLASSES["breadcrumb:list"] == "breadcrumb my-0"`.

- [ ] **Step 1: Tests.**
  - `test_header_breadcrumb_has_no_bottom_margin`: assert the rendered header row contains
    `<ol class="breadcrumb my-0">` and the theme CSS no longer contains `--cui-breadcrumb-margin-bottom`.
  - delete `ARIA_SORT` and `test_table_head_is_upstream_plus_aria_sort`; add `test_table_override_keeps_the_stock_header`:
    the theme's template source has no `table.thead` block.
  - `test_table_override_extends_the_stock_table`: comment no longer mentions aria-sort.
  - `test_sorted_column_is_marked`, `test_every_orderable_header_has_aria_sort`: keep; adjust only if they relied on
    no icon for the default order (Review Focus 5).
  - `test_bulk.py`: remove the `xfail` marker and the "waiting on #393" comments from
    `test_bulk_prefixed_sort_shows_the_icon`; `test_bulk_prefixed_sort_sets_aria_sort` comment: upstream header (#393).
- [ ] **Step 2: Run THEME.** Expected: the breadcrumb test and `test_table_override_keeps_the_stock_header` FAIL;
  `test_bulk_prefixed_sort_shows_the_icon` FAILs (no longer xfail).
- [ ] **Step 3: Implement.** Add `"breadcrumb:list": "breadcrumb my-0"` (comment: CoreUI header row, as the free admin
  template writes it; upstream #393). Delete the CSS rule and its comment. Delete the template's `table.thead` block
  and the two comment lines about it.
- [ ] **Step 4: Run THEME and EXAMPLE.** Expected: THEME passes except `test_css_maps_every_bs_variable_upstream_reads`.
  `test_every_theme_key_is_an_upstream_key` must pass (the key now exists upstream).
- [ ] **Step 5: Docs.** Drop the U10 section; the table override is three layout blocks. CSS list: the breadcrumb
  margin is the `breadcrumb:list` key now; note that a project overriding `breadcrumb:list` should keep `my-0`.
- [ ] **Step 6: Commit.** `git commit -m "feat: breadcrumb:list key and the stock table header (U9, U10, C8)"`

### Task 4: `--cv-*` tokens instead of `--bs-*` re-mapping (U5, U12)

**Files:**
- Modify: `src/crud_views_coreui/static/crud_views_coreui/crud_views_coreui.css` (the two token blocks, drop the
  gutter rule, keep the help-button bridge)
- Modify: `tests/crud_views_coreui/test_registration.py` (`AssetTests`)
- Modify: `example/sales/tests/test_orders.py:94`, `example/roastery/tests.py:85,98` (`class="row gx-3 cv-formset-compact-headings"`)
- Modify: `pyproject.toml` (`django-crud-views-extensions (>=0.4.0)`), `uv.lock` (`uv lock`)
- Modify: `docs/theme_internals.md` ("CSS tokens (U5)"), `docs/installation.md` (one line: typeahead styling needs
  django-crud-views-extensions 0.4.0)

**Interfaces:**
- Produces: theme blocks on `[data-cv-manage], .cv-formset-row-card, .cv-formset-row-compact, .cv-formset-compact-child`
  setting `--cv-secondary-color`, `--cv-secondary-text-emphasis` (from `--cui-body-color`), `--cv-body-bg`,
  `--cv-border-color`, `--cv-border-radius`, `--cv-tertiary-bg`; and on `.cv-typeahead, .cv-typeahead-select` setting
  `--cv-secondary-color`, `--cv-body-bg`, `--cv-border-color-translucent`, `--cv-border-radius`, `--cv-highlight-bg`;
  each `--cv-x: var(--cui-x)` unless named otherwise.

- [ ] **Step 1: Tests.** Replace the two `test_css_maps_every_bs_variable_*` tests:
  - `test_css_sets_every_cv_token_upstream_reads`: tokens = `set(re.findall(r"var\((--cv-[a-z-]+)", manage.css + formset.css))`,
    `len >= 6`; for each, theme matches `rf"{name}:\s*var\({source}\)"` with source `--cui-{name[5:]}` except
    `--cv-secondary-text-emphasis` -> `--cui-body-color`.
  - `test_css_sets_every_cv_token_the_typeahead_reads`: same over the installed skins (skip without the extensions),
    inside the `.cv-typeahead, .cv-typeahead-select` block, `len >= 5`.
  - `test_css_re_maps_no_bs_variable`: the theme sets no `--bs-*` property (`not re.search(r"--bs-[a-z-]+\s*:", theme)`),
    and the only `var(--bs-` read is `--cui-btn-color: var(--bs-btn-color)`; upstream's manage.css still sets
    `--bs-btn-color` (assert), so the bridge is needed.
  - `test_cv_tokens_are_element_scoped`: no `:root` and no `html` selector in front of a `--cv-` declaration.
  Example: the three assertions use `class="row gx-3 cv-formset-compact-headings"`.
- [ ] **Step 2: Run THEME.** Expected: the four new tests FAIL; EXAMPLE passes after the class-string edit.
- [ ] **Step 3: Implement.** Rewrite the two blocks to set `--cv-*` (same selectors), update their comments (upstream
  #394, extensions #6; why `--cui-body-color`; element scope for `[data-coreui-theme]` subtrees). Delete the gutter
  rule (upstream uses `gx-3`, which CoreUI's `.gx-3` turns into `--cui-gutter-x`). Keep the help-button rule. Bump the
  extensions floor, `uv lock`.
- [ ] **Step 4: Run THEME, EXAMPLE, ruff.** Expected: all pass.
- [ ] **Step 5: Docs.** Rewrite "CSS tokens (U5)" to describe the token blocks and the help-button bridge.
- [ ] **Step 6: Commit.** `git commit -m "feat: set upstream's --cv-* tokens from --cui-* (U5, U12), extensions >= 0.4.0"`

### Task 5: Tracker, project docs, browser pass, full verification

**Files:**
- Modify: `superpowers/notes/upstream-tracker.md`, `CLAUDE.md` (lines 52-53, 70-83), `docs/development.md:77-78`

- [ ] **Step 1: Tracker.** References line: `../django-crud-views` @ `49d5173a`, extensions @ `fd06c91`. Close-out
  table: U1, U2, U5, U9, U10, U12 -> done (adopted 2026-11-21) with what replaced each workaround; U11 -> reduced
  (E002 checks `crud_views` only); U3 note: the U1 overrides it relied on are gone, dropdowns use CoreUI's data API via
  the prefix; U4 unchanged. Each entry's Status line and a dated "Adopted" bullet; C8 in the bulk section: done.
  "Not yet adopted" paragraph -> "Adopted".
- [ ] **Step 2: CLAUDE.md and development.md.** Remove the four copies, `coreui-tabs.js` and the `table.thead` copy from
  the theme description; add `register_data_prefix("coreui")`, `breadcrumb:list`, "sets `--cv-*` tokens". E002:
  "theme listed after `crud_views`". development.md: replace the two drift-test bullets with the `--cv-*` token test
  and the no-`data-bs-` scan.
- [ ] **Step 3: Browser pass** (`task up` or runserver; chrome-devtools; alex; light and dark; 1280 and 375):
  object-detail tabs switch (full page and modal), accordion opens, row `⋯` menu and language selector open, manage
  page headers/help buttons readable in dark, order formset compact rows aligned, typeahead select popup opaque in
  both modes, sorted and `?c-sort=` prefixed lists show icon + `aria-sort`, header breadcrumb has no bottom margin.
  Record results as a short table under the tracker's close-out.
- [ ] **Step 4: Full verification.** `task test`, `uv run ruff format --check . && uv run ruff check .`,
  `uvx nox -s docs`. Expected: all green.
- [ ] **Step 5: Commit.** `git commit -m "docs: tracker — U1, U2, U5, U9, U10, U12 adopted; U11 reduced"`
