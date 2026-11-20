"""scripts/check_dist.py: the wheel must carry the templates and static files, and nothing outside the allowlist."""

import io
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_dist.py"

REQUIRED = [
    "django_coreui/templates/django_coreui/base.html",
    "django_coreui/templates/crispy_coreui/field.html",
    "django_coreui/static/django_coreui/layout-switch.js",
    "crud_views_coreui/templates/crud_views_coreui/page.html",
    "crud_views_coreui/static/crud_views_coreui/crud_views_coreui.css",
    "crud_views_coreui/static/crud_views_coreui/coreui-adapters.js",
]


def build(tmp_path, wheel_names, sdist_names=("pyproject.toml", "src/x.py")):
    with zipfile.ZipFile(tmp_path / "pkg-0.1.0-py3-none-any.whl", "w") as whl:
        for name in wheel_names:
            whl.writestr(name, "x")
    with tarfile.open(tmp_path / "pkg-0.1.0.tar.gz", "w:gz") as tar:
        for name in sdist_names:
            info = tarfile.TarInfo(f"pkg-0.1.0/{name}")
            info.size = 1
            tar.addfile(info, io.BytesIO(b"x"))
    return subprocess.run([sys.executable, str(SCRIPT), str(tmp_path)], capture_output=True, text=True)


def test_complete_wheel_passes(tmp_path):
    result = build(tmp_path, [*REQUIRED, "pkg-0.1.0.dist-info/METADATA"])
    assert result.returncode == 0, result.stdout


def test_wheel_without_templates_fails(tmp_path):
    result = build(tmp_path, [n for n in REQUIRED if "templates" not in n])
    assert result.returncode == 1
    assert "django_coreui/templates/django_coreui/base.html" in result.stdout


def test_wheel_with_tests_or_bytecode_fails(tmp_path):
    for extra in ("django_coreui/tests.py", "django_coreui/__pycache__/x.cpython-314.pyc"):
        result = build(tmp_path, [*REQUIRED, extra])
        assert result.returncode == 1, extra


def test_wheel_with_foreign_top_level_fails(tmp_path):
    assert build(tmp_path, [*REQUIRED, "example/settings.py"]).returncode == 1


def test_sdist_outside_allowlist_fails(tmp_path):
    assert build(tmp_path, REQUIRED, ("pyproject.toml", "superpowers/plan.md")).returncode == 1
