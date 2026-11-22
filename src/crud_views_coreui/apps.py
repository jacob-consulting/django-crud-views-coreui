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
        from crud_views.lib import register_data_prefix, register_js_namespace, register_tooltip_placements
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
        # CoreUI's data API reads only data-coreui-*: upstream's templates and object-detail tabs.js write the
        # registered prefix (upstream #391, tracker U1/U2). The stock modal adapter names its events after it too
        # (hidden.coreui.modal; upstream #403, tracker U13).
        register_data_prefix("coreui")
        # CoreUI's bundle exposes its components on window.coreui, not window.bootstrap; upstream's stock adapters
        # resolve the registered name on every call (upstream #398, tracker U4).
        register_js_namespace("coreui")
        # Toolbar tooltips open below the buttons, so they do not cover the page header; the rest keep CoreUI's
        # default. A data-coreui-placement on the button wins.
        register_tooltip_placements({"context": "bottom"})
        # The CSS sets upstream's --cv-* tokens from CoreUI's --cui-* (tracker U5, U12).
        register_assets("crud_views_coreui", css=["crud_views_coreui/crud_views_coreui.css"])
