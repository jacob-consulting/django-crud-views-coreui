from django.apps import AppConfig


class DjangoCoreuiConfig(AppConfig):
    """Shared CoreUI page templates, template tags and icons for Django projects."""

    name = "django_coreui"
    verbose_name = "Django CoreUI"

    def ready(self):
        from django_coreui import checks  # noqa: F401  (registers the system checks)
