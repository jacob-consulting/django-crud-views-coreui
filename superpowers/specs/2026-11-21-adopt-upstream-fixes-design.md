# Adopt today's upstream fixes (design)

Date: 2026-11-21 · Size: small change · Approved in conversation

## Intent

Four upstream issues filed from this theme were fixed on 2026-11-21: django-crud-views #391 (PR #395, `95d40ddf`),
#393 (PR #396, `4ec93cb9`), #394 (PR #397, `49d5173a`) and django-crud-views-extensions #6 (PR #7, released in 0.4.0).
Replace the theme's workarounds (tracker U1, U2, U5, U9, U10, U12, C8) with the upstream hooks, so the theme stops
carrying copied templates and scripts that drift from upstream.

## Goals

1. U1/U2: `register_data_prefix("coreui")` in `CrudViewsCoreuiConfig.ready()`. Delete the four `data-coreui-` template
   overrides, `coreui-tabs.js` (and its asset registration) and their drift tests. Keep a test that no rendered page
   (full page and modal partial, object-detail packs included) contains `data-bs-`.
2. U11: narrow `crud_views_coreui.E002` to "theme listed before `crud_views`": the theme still overrides
   `crud_views/snippets/form_frame.html` and `crud_views/table/bootstrap5.html`. The `crud_views_object_detail` half
   goes.
3. U9: set `breadcrumb:list` to `breadcrumb my-0` in `COREUI_BUTTON_CLASSES`; drop the
   `.header-breadcrumb .breadcrumb` CSS rule; the existing no-bottom-margin test keeps checking the outcome.
4. U10/C8: drop the theme's `table.thead` block copy (the table override keeps its three layout blocks). The strict
   xfail `test_bulk_prefixed_sort_shows_the_icon` becomes an ordinary passing test; the aria-sort output tests stay.
5. U5/U12: set the six `--cv-*` tokens (plus `--cv-border-color-translucent`, `--cv-highlight-bg` for the typeahead)
   from `--cui-*`, on the same element scopes as today (`[data-cv-manage]`, formset elements,
   `.cv-typeahead, .cv-typeahead-select`), so a `[data-coreui-theme]` subtree is still followed. Drop the `--bs-*`
   re-mapping and the `--cui-gutter-x` rule (upstream uses `gx-3`). The help-button `--cui-btn-color` bridge stays.
   The CSS tests switch from "maps every `--bs-*` upstream reads" to "sets every `--cv-*` token upstream reads".
6. Example: `django-crud-views-extensions (>=0.4.0)`; docs say the theme's typeahead styling needs 0.4.0.
7. Tracker: U1, U2, U5, U9, U10, U12 -> done; U11 -> reduced; C8 icon half done. `docs/theme_internals.md` and
   `CLAUDE.md` updated where they describe the removed pieces.

## Non-goals

- U4 (`coreui-adapters.js`): upstream `adapters.js` is unchanged; the script and its tooltip-placement wrapper stay.
- U3, U8, C10, C11: not touched.
- No fallback for older django-crud-views: the theme already depends on unreleased upstream (bulk selection); nox
  installs `main`.

## Constraints

- `../django-crud-views` updated to `origin/main` @ `49d5173a`; both sibling checkouts stay read-only.
- Fix order from CLAUDE.md: upstream hook first, theme CSS second, override template last.

## Approaches

- **Adopt fully, no compatibility shim** (picked): the theme already requires unreleased upstream, so a shim for old
  upstream would protect nobody and keep the drift tests alive.
- Adopt with a fallback (keep overrides when `register_data_prefix` is missing): doubles the code paths for a
  version no release of the theme supports. Dropped.
- Keep the `--bs-*` typeahead mapping next to the tokens for extensions < 0.4.0: cheap, but 0.4.0 is on PyPI and the
  example floor can say so. Dropped; documented instead.

## Left to the builder

Test names and file layout of the reworked tests; exact wording in the docs; the browser pass (light, dark; manage
page, a formset, object-detail tabs and accordion, row action menu, language selector, typeahead select, sorted and
prefixed-sorted lists, breadcrumb row).
