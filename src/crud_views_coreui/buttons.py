"""CoreUI classes for django-crud-views' button class table, registered from CrudViewsCoreuiConfig.ready().

The key set is exactly the Tabler theme's (``crud_views_tabler.buttons.TABLER_BUTTON_CLASSES``); the values are CoreUI 5
free classes (coreui.io/bootstrap/docs). How the Tabler classes translate:

- Tabler's plain ``btn`` is a bordered surface button; CoreUI's plain ``.btn`` is transparent, so ``btn
  btn-outline-secondary`` stands in for it.
- ``btn-ghost-*`` exists in CoreUI under the same name.
- ``btn-icon`` does not exist in CoreUI: icon-only buttons (every ``:icon`` key, the menu toggles and the formset and
  card-order controls) get the theme's ``cv-coreui-icon-btn`` (``crud_views_coreui.css``), which makes them square.
- Tabler's light badges ``bg-<colour>-lt`` are CoreUI's ``bg-<colour>-subtle text-<colour>-emphasis``.
- ``btn-list`` is ``d-flex flex-wrap gap-2``; ``nav-bordered`` is ``nav nav-underline-border``; ``table-vcenter`` is
  ``align-middle``; ``badge-outline`` is ``border`` with a subtle border colour, and ``text-body-secondary`` for the
  text: on a transparent badge, CoreUI's ``text-<colour>-emphasis`` stays dark in dark mode.
- Tabler's named colours: ``green``, ``red`` and ``yellow`` are CoreUI's ``success``, ``danger`` and ``warning``, and
  ``azure`` is ``info`` (CoreUI's info, #39f, is an azure). ``blue`` and ``pink`` have no theme colour: CoreUI 5 defines
  them as palette variables (``--cui-blue``, ``--cui-pink``) but ships no utility classes for them, a CoreUI palette
  gap, not an upstream one. The theme's ``cv-coreui-badge-blue`` / ``cv-coreui-badge-pink`` (``crud_views_coreui.css``)
  build subtle badges from those variables, light and dark. Never ``primary``: the manage page's legend names the
  colours ("Blue: required permission · Magenta: required group"), and a project's primary may be any colour.
"""

COREUI_BUTTON_CLASSES: dict[str, str] = {
    "workflow:badge-primary": "badge bg-primary-subtle text-primary-emphasis",
    "workflow:badge-secondary": "badge bg-secondary-subtle text-secondary-emphasis",
    "workflow:badge-success": "badge bg-success-subtle text-success-emphasis",
    "workflow:badge-danger": "badge bg-danger-subtle text-danger-emphasis",
    "workflow:badge-warning": "badge bg-warning-subtle text-warning-emphasis",
    "workflow:badge-info": "badge bg-info-subtle text-info-emphasis",
    "workflow:badge-light": "badge bg-light-subtle text-light-emphasis",
    "workflow:badge-dark": "badge bg-dark-subtle text-dark-emphasis",
    # Workflow transition buttons by the transition's custom["variant"] (upstream #362): upstream's Bootstrap
    # defaults, which are CoreUI classes too; declared so the theme's look is explicit and project-visible.
    "workflow:transition-primary": "btn btn-primary",
    "workflow:transition-secondary": "btn btn-secondary",
    "workflow:transition-success": "btn btn-success",
    "workflow:transition-danger": "btn btn-danger",
    "workflow:transition-warning": "btn btn-warning",
    "workflow:transition-info": "btn btn-info",
    "workflow:transition-light": "btn btn-light",
    "workflow:transition-dark": "btn btn-dark",
    # The workflow history sits on the page, not in a card: a plain table with vertically centred cells.
    "workflow:history-table": "table align-middle",
    "context:primary": "btn btn-primary",
    "context:secondary": "btn btn-outline-secondary",
    "context:tertiary": "btn btn-outline-secondary",
    "context:danger": "btn btn-outline-danger",
    "list:primary": "btn btn-sm btn-ghost-primary",
    "list:secondary": "btn btn-sm btn-ghost-secondary",
    "list:tertiary": "btn btn-sm btn-ghost-secondary",
    "list:danger": "btn btn-sm btn-ghost-danger",
    "card:primary": "btn btn-sm btn-primary",
    "card:secondary": "btn btn-sm btn-outline-secondary",
    "card:tertiary": "btn btn-sm btn-ghost-secondary",
    "card:danger": "btn btn-sm btn-ghost-danger",
    # Icon-only buttons (label mode "icon", the toolbar and row default) are square: cv-coreui-icon-btn.
    "context:primary:icon": "btn btn-primary cv-coreui-icon-btn",
    "context:secondary:icon": "btn btn-outline-secondary cv-coreui-icon-btn",
    "context:tertiary:icon": "btn btn-outline-secondary cv-coreui-icon-btn",
    "context:danger:icon": "btn btn-outline-danger cv-coreui-icon-btn",
    "list:primary:icon": "btn btn-sm btn-ghost-primary cv-coreui-icon-btn",
    "list:secondary:icon": "btn btn-sm btn-ghost-secondary cv-coreui-icon-btn",
    "list:tertiary:icon": "btn btn-sm btn-ghost-secondary cv-coreui-icon-btn",
    "list:danger:icon": "btn btn-sm btn-ghost-danger cv-coreui-icon-btn",
    "card:primary:icon": "btn btn-sm btn-primary cv-coreui-icon-btn",
    "card:secondary:icon": "btn btn-sm btn-outline-secondary cv-coreui-icon-btn",
    "card:tertiary:icon": "btn btn-sm btn-ghost-secondary cv-coreui-icon-btn",
    "card:danger:icon": "btn btn-sm btn-ghost-danger cv-coreui-icon-btn",
    "context:container": "d-flex flex-wrap gap-2",
    "list:container": "d-flex flex-nowrap justify-content-end gap-1",
    "card:container": "d-flex flex-wrap gap-2",
    "context:menu-toggle": "btn btn-outline-secondary cv-coreui-icon-btn",
    "list:menu-toggle": "btn btn-sm btn-ghost-secondary cv-coreui-icon-btn",
    "card:menu-toggle": "btn btn-sm btn-outline-secondary cv-coreui-icon-btn",
    # The stock card grid (view_card.content.html) is a .row without a vertical gutter: the card keeps upstream's bottom
    # margin, at CoreUI's mb-4 spacing.
    "card:root": "card mb-4",
    "context:menu-wrapper": "dropdown",
    "list:menu-wrapper": "dropdown",
    "form:delete": "btn btn-danger",
    "form:actions": "d-flex flex-wrap gap-2",
    "form:filter-actions": "d-flex flex-wrap gap-1",
    "alert:dismissible": "alert-dismissible fade show",
    "alert:close": "btn-close",
    "card-order:toggle": "btn btn-outline-secondary cv-coreui-icon-btn",
    "card-order:container": "btn-group",
    # ViewSet Navigation (upstream #384): CoreUI's underline tabs instead of the stock pills. nav-underline-border
    # spaces the tabs with a flex gap (no item margin, so a wrapped row is not indented); row-gap-1 keeps a wrapped
    # row off the active underline above it. CoreUI's .nav-link is a block, so d-flex and gap-2 space icon and label.
    "navbar:nav": "nav nav-underline-border flex-wrap row-gap-1",
    "navbar:item": "nav-item mw-100",
    "navbar:link": "nav-link d-flex align-items-center mw-100 text-break gap-2",
    "formset:control": "btn btn-outline-secondary cv-coreui-icon-btn",
    "formset:control-danger": "btn btn-danger cv-coreui-icon-btn",
    "conditional:legend": "cv-coreui-section-legend",
    "formset:legend": "cv-coreui-section-legend",
    # The structured manage page (#366, #370, #372): subtle badges, as for the workflow state. Named colours, not the
    # project's primary, because the page's legend names them ("Blue: required permission · Magenta: required group ·
    # Green: Guardian policy"); see the module docstring for the colour substitutions and the two theme badge classes.
    "manage:badge-model": "badge bg-secondary-subtle text-secondary-emphasis",
    "manage:badge-resource": "badge bg-info-subtle text-info-emphasis",
    "manage:badge-objects": "badge border border-secondary-subtle text-body-secondary",
    "manage:badge-permission": "badge cv-coreui-badge-blue",
    "manage:badge-group": "badge cv-coreui-badge-pink",
    "manage:badge-policy-global": "badge bg-success-subtle text-success-emphasis",
    "manage:badge-policy-strict": "badge bg-success-subtle text-success-emphasis",
    "manage:badge-policy-na": "badge bg-secondary-subtle text-secondary-emphasis",
    # outline-secondary, so upstream's contrast rule for the help button (manage.css) applies; see the theme CSS.
    "manage:help": "btn btn-sm btn-outline-secondary",
    "manage:trace-allowed": "badge bg-success-subtle text-success-emphasis",
    "manage:trace-passed": "badge bg-success-subtle text-success-emphasis",
    "manage:trace-denied": "badge bg-danger-subtle text-danger-emphasis",
    "manage:trace-not-found": "badge bg-warning-subtle text-warning-emphasis",
    "manage:trace-login-redirect": "badge bg-warning-subtle text-warning-emphasis",
    "manage:trace-error": "badge bg-warning-subtle text-warning-emphasis",
    "manage:trace-no-such-route": "badge bg-warning-subtle text-warning-emphasis",
    "manage:trace-not-evaluated": "badge bg-warning-subtle text-warning-emphasis",
    "manage:trace-skipped": "badge bg-secondary-subtle text-secondary-emphasis",
    "manage:trace-not-reached": "badge bg-secondary-subtle text-secondary-emphasis",
}
