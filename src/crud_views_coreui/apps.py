from django.apps import AppConfig


class CrudViewsCoreuiConfig(AppConfig):
    """CoreUI theme for django-crud-views.

    Overrides the package's templates under the ``crud_views/`` namespace, so it must be listed before ``crud_views``
    in INSTALLED_APPS. Registers the ``coreui`` icon library, a CoreUI icon for every semantic name, the CoreUI button
    classes and the theme's assets, so projects need no icon or button settings.
    """

    name = "crud_views_coreui"
    verbose_name = "django-crud-views CoreUI theme"

    def ready(self):
        from crud_views.lib.assets import register_assets
        from crud_views.lib.button_classes import register_button_classes
        from crud_views.lib.icons import register_icon_library, register_icons
        from crud_views.lib.view.label_mode import register_label_mode_defaults

        import crud_views_coreui.checks  # noqa: F401
        from crud_views_coreui.buttons import COREUI_BUTTON_CLASSES
        from crud_views_coreui.icons import COREUI_ICONS

        register_icon_library("coreui", renderer="crud_views_coreui.icons.render")
        register_icons(COREUI_ICONS)
        register_label_mode_defaults({"form": "both"})
        register_button_classes(
            {
                key: value
                for key, value in COREUI_BUTTON_CLASSES.items()
                if not key.startswith("workflow:") or self.apps.is_installed("crud_views_workflow")
            }
        )
        # coreui-adapters.js points cv.adapters at window.coreui (tracker U4); coreui-tabs.js, after it, initialises
        # the object-detail tabs, whose upstream init selects data-bs-toggle (tracker U2); the CSS feeds upstream's
        # --bs-* custom properties from CoreUI's --cui-* (tracker U5).
        register_assets(
            "crud_views_coreui",
            js=["crud_views_coreui/coreui-adapters.js", "crud_views_coreui/coreui-tabs.js"],
            css=["crud_views_coreui/crud_views_coreui.css"],
        )
