"""CoreUI's CSS and JavaScript for the free edition: jsDelivr URLs pinned to an exact version, with SRI hashes.

Only ``django_coreui/includes/assets.html`` uses these. The hashes were computed with
``curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A``; recompute both when the version changes.
"""

COREUI_VERSION = "5.9.1"

COREUI_CSS = f"https://cdn.jsdelivr.net/npm/@coreui/coreui@{COREUI_VERSION}/dist/css/coreui.min.css"
COREUI_CSS_SRI = "sha384-hLBsN3gpx96kCbLUCbANpmr8cdCNM1sH85tJfeZT61uxTNIvelafstACefvdVnuP"

# The bundle includes Popper (dropdowns, tooltips, popovers).
COREUI_JS = f"https://cdn.jsdelivr.net/npm/@coreui/coreui@{COREUI_VERSION}/dist/js/coreui.bundle.min.js"
COREUI_JS_SRI = "sha384-yW+X2pqDqevsUW8M2p1APhb8cm2i5jneCZe2pkEvKVATzd6517WyXz6ElE46++OE"
