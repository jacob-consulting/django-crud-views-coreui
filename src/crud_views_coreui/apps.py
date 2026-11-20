from django.apps import AppConfig


class CrudViewsCoreuiConfig(AppConfig):
    """CoreUI theme for django-crud-views.

    Overrides the package's templates under the ``crud_views/`` namespace, so it must be listed before ``crud_views``
    in INSTALLED_APPS. Registration of icons, button classes and assets is added in later tasks.
    """

    name = "crud_views_coreui"
    verbose_name = "django-crud-views CoreUI theme"

    def ready(self):
        pass
