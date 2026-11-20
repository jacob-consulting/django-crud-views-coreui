from importlib.metadata import version

import crud_views_coreui
import django_coreui


def test_versions_match_distribution():
    assert version("django-crud-views-coreui") == crud_views_coreui.__version__ == django_coreui.__version__ == "0.1.0"
