"""
Development Settings
Local development configuration with debug enabled.
"""

from .base import *

# =============================================================================
# DEBUG SETTINGS
# =============================================================================

DEBUG = True
ALLOWED_HOSTS = ["*"]

# =============================================================================
# DATABASE
# =============================================================================



# =============================================================================
# =============================================================================
# DEBUG TOOLS
# =============================================================================

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
        "django_extensions",
    ]

    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
        "0.0.0.0",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TEMPLATE_CONTEXT": True,
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }

    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]
# =============================================================================
# EMAIL
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# STATIC & MEDIA
# =============================================================================

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# =============================================================================
# LOGGING
# =============================================================================

LOGGING["loggers"]["django"]["level"] = "DEBUG"
LOGGING["loggers"]["apps"]["level"] = "DEBUG"

# =============================================================================
# CACHING
# =============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# =============================================================================
# CELERY
# =============================================================================

CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously in development
CELERY_TASK_EAGER_PROPAGATES = True
