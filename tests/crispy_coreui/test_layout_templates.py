from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Fieldset, Submit

from django_coreui.crispy.layout import UneditableField
from tests.crispy_coreui.helpers import render_horizontal, render_layout


def test_uneditable_field_is_a_plaintext_control():
    html = render_layout(UneditableField("char"))
    assert "form-control-plaintext" in html and "uneditable-input" not in html


def test_uneditable_field_label_is_a_form_label():
    assert '<label class="form-label ' in render_layout(UneditableField("char"))


def test_form_actions_keep_the_upstream_spacing():
    html = render_layout(FormActions(Submit("save", "Save")))
    assert "mb-3" in html and "form-footer" not in html


def test_fieldset_is_a_plain_fieldset_with_its_css_class():
    html = render_layout(Fieldset("Internal", "char", css_class="custom"))
    assert 'class="custom"' in html and "form-fieldset" not in html


def test_a_horizontal_form_keeps_its_label_columns():
    html = render_horizontal(UneditableField("char"))
    assert "col-form-label" in html


def test_uneditable_field_keeps_an_explicit_css_class():
    html = render_layout(UneditableField("char", css_class="extra"))
    assert "form-control-plaintext extra" in html and "uneditable-input" not in html
