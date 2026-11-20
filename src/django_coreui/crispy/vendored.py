"""Provenance of the vendored templates."""

import re

CRISPY_BOOTSTRAP5_VERSION = "2026.9"
"""The crispy-bootstrap5 release the templates were copied from (scripts/vendor_templates.py).

Each vendored template's first line names it; the vendoring script refuses another installed release.
"""

CRISPY_BOOTSTRAP5_COMPATIBLE = ("2026.3", "2026.9")
"""crispy-bootstrap5 releases whose templates and ``bootstrap5.py`` are byte-identical to the vendored release.

2026.3 is the newest release that installs on Django 4.2 (2026.9 requires Django >= 5.2), so the pack runs unchanged
there. tests/crispy_coreui/test_pack_parity.py proves the identity against whichever release is installed; add a
release here only when that test passes with it.
"""

HAND_EDITED = (
    "field.html",
    "layout/uneditable_input.html",
)
"""Templates edited by hand after vendoring; a re-run of the vendoring script would silently revert them.

dev/crispy_coreui_hand_edits.md records why these two need it and why the other four that crispy_tabler edits do not.
"""

INCLUDE_PREFIX = re.compile(r"""(['"])bootstrap5/""")
"""The quoted include prefix that ``rewrite`` changes to ``crispy_coreui/``."""

DATA_PREFIX = re.compile(r"\bdata-bs-")
"""Bootstrap's data attribute prefix; CoreUI's JavaScript reads ``data-coreui-`` instead."""

UPSTREAM_SHA256 = {
    # The crispy-bootstrap5 originals of the hand-edited templates, and bootstrap5.py (FloatingField, Switch are
    # subclassed in django_coreui.crispy.layout), as vendored. The parity test compares the installed files with them.
    "field.html": "1c6d91cfb43dd8909234f977c7934c9d9cc787fba77c33dec505d7717dfc1b99",
    "layout/uneditable_input.html": "c5c85803e8560c72004f1b96d706b7b4858fdd5293fea91be1deb0da69b754d0",
    "bootstrap5.py": "1ad443567a543685475661401139e6ad593264f63e1d84a6c19180cf45b8d134",
}


def rewrite(text: str) -> str:
    """The two changes made to every vendored template: the include prefix and the data attribute prefix."""
    return DATA_PREFIX.sub("data-coreui-", INCLUDE_PREFIX.sub(r"\1crispy_coreui/", text))
