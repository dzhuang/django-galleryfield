from galleryfield import conf


def static_context_processor(request):
    return {
        "jquery_location": conf.JQUERY_LOCATION,
        "bootstrap_css_location": conf.BOOTSTRAP_CSS_LOCATION,
        "bootstrap_js_location": conf.BOOTSTRAP_JS_LOCATION,
        "bootstrap_version": conf.BOOTSTRAP_VERSION
    }
