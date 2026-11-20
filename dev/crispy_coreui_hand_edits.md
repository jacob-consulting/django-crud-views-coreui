# crispy_coreui: hand-edited templates

`crispy_tabler` hand-edits six templates; CoreUI 5 uses Bootstrap 5.3's form markup, so only two stay
(`HAND_EDITED` in `src/django_coreui/crispy/vendored.py`). Every other template is `provenance + rewrite(upstream)`.

- `field.html`: kept. Adds `form-range` (range) and `form-control form-control-color` (colour) branches, which CoreUI documents; upstream gives a range input `form-control`, which styles it as a text box. Loads `crispy_coreui_field`.
- `layout/uneditable_input.html`: kept. Adds `form-label` to the non-horizontal label so its spacing matches every other label (CoreUI's form docs put `form-label` on each label); the `form-control-plaintext` class itself is swapped in Python (`UneditableField`).
- `layout/formactions.html`: dropped. Tabler's `form-footer` is Tabler-only; upstream's `mb-3` spacing suits CoreUI.
- `layout/fieldset.html`: dropped. `form-fieldset` is Tabler-only; a plain `<fieldset>` is right for CoreUI.
- `layout/radioselect_inline.html`: dropped. Upstream's `fs-6` on the legend is correct against Bootstrap's reboot, which CoreUI shares; Tabler removed it for its own legend styling.
- `layout/checkboxselectmultiple_inline.html`: dropped. Same as `radioselect_inline.html`.
- `field.html` also keeps upstream's `fs-6` on a fieldset legend (Tabler removed it); that is not a hand-edit.
