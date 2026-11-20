# Crispy template pack

`crispy_coreui` is a [django-crispy-forms](https://django-crispy-forms.readthedocs.io/) template pack with CoreUI
markup, shipped in `django_coreui`. CoreUI 5 uses Bootstrap 5.3's form markup (`form-control`, `form-select`,
`form-check`, `is-invalid`, ...), so the pack is vendored from crispy-bootstrap5 2026.9 and differs very little: the
templates are byte-identical except for the rewritten include paths, the `data-bs-` to `data-coreui-` rename, and two
hand-edited templates. A parity test fails when they drift from the installed crispy-bootstrap5.
crispy-bootstrap5 2026.3, the newest release on Django 4.2, has byte-identical templates (the test checks whichever
release is installed), so the pack's markup is the same on every supported Django version. Django 4.2 itself adds less
to form fields: `aria-describedby` and `aria-invalid` come from Django 5.0.

```python
CRISPY_ALLOWED_TEMPLATE_PACKS = ("crispy_coreui",)
CRISPY_TEMPLATE_PACK = "crispy_coreui"
```

django-crud-views' forms render through it, and so does any `{% crispy form %}` or `{{ form|crispy }}` of your own.

## What the vendoring rewrites

`scripts/vendor_templates.py` copies the templates from the installed crispy-bootstrap5 and applies two rewrites
(`django_coreui/crispy/vendored.py:rewrite`):

- `bootstrap5/` include paths become `crispy_coreui/`, so the pack does not need `crispy_bootstrap5` in
  `INSTALLED_APPS`;
- `data-bs-` becomes `data-coreui-`, because CoreUI's JavaScript only reacts to `data-coreui-*` attributes. Four
  upstream templates (accordion, tab link, modal, alert dismissal) carry such attributes.

## Fields, widgets and layout objects

| Import | What it does |
|---|---|
| `django_coreui.crispy.fields.RangeField` (`widgets.RangeInput`) | an integer field as a range input (`form-range`) |
| `django_coreui.crispy.fields.ColorField` (`widgets.ColorInput`) | a colour input (`form-control form-control-color`) |
| `django_coreui.crispy.fields.PlaintextField` (`widgets.PlaintextInput`) | a read-only, disabled value in the form's grid |
| `django_coreui.crispy.layout.FloatingField` | crispy-bootstrap5's `FloatingField`, rendered from this pack's template |
| `django_coreui.crispy.layout.Switch` | crispy-bootstrap5's `Switch`, rendered from this pack's template |
| `django_coreui.crispy.layout.UneditableField` | crispy-forms' `UneditableField` with CoreUI's `form-control-plaintext` |

crispy-bootstrap5's `FloatingField` and `Switch` hard-code `bootstrap5/` template paths, so they would ignore the pack;
use these in a `FormHelper` layout instead. crispy-forms' `UneditableField` sets the dead Bootstrap 2 class
`uneditable-input` in Python, which a template cannot remove.

## Hand-edited templates

Only two templates are edited by hand (`HAND_EDITED` in `vendored.py`); the vendoring script refuses to overwrite them
without `--force`. The rationale is in
`dev/crispy_coreui_hand_edits.md` in the GitHub repository jacob-consulting/django-crud-views-coreui (maintainer notes, not on this site).

| Template | Edit |
|---|---|
| `field.html` | A `type="range"` input gets `form-range` alone and `type="color"` gets `form-control form-control-color`; upstream gives both `form-control`, which styles a range as a text box. |
| `layout/uneditable_input.html` | `form-label` on the non-horizontal label, so its spacing matches every other label. |

The Tabler pack hand-edits four more (form footer, fieldset, and the `fs-6` legends of the inline radio and checkbox
templates); those edits answer Tabler-only classes or styling, and upstream's markup is right for CoreUI, so they are
not carried over.

## Coverage: the `showcase` demo app

The demo's `showcase` app (`/showcase/create/`) renders one crispy template branch per field, so the pack can be judged
field by field. `example/showcase/tests.py` pins one marker per render path: if a field is removed from the form's
layout, the matching test fails. The coverage includes plain and textarea fields, selects, checkbox and radio groups
(also inline), prepended and appended text, range and colour inputs, date and time inputs, a checkbox and a switch, a
floating field, a file field, an uneditable field, a fieldset, form actions and the filter form's `NullBooleanSelect`
and inline checkboxes.

A gotcha worth remembering: `InlineRadios("shipping")` only swaps the template. Without `widget=forms.RadioSelect` on
the field the widget stays a `Select` and renders `<input type="select">`, which is invalid HTML.

## Provenance

The pack was ported from `crispy_tabler` (itself copied from `jacob-consulting/crispy-tabler`) and re-vendored from
crispy-bootstrap5. It keeps its templates in `templates/crispy_coreui/`, its template tags in
`templatetags/crispy_coreui_field.py` and its Python in `django_coreui.crispy`. The compatible crispy-bootstrap5
releases are `CRISPY_BOOTSTRAP5_COMPATIBLE` (2026.3 and 2026.9); `django_coreui` never imports `crud_views`.
