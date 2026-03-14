"""
Django Base Settings - Production-Grade Configuration
Shared settings across all environments.
"""

import os
from pathlib import Path

import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

# Environment Configuration
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ""),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, ""),
    REDIS_URL=(str, ""),
    CELERY_BROKER_URL=(str, ""),
    CELERY_RESULT_BACKEND=(str, ""),
    EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    EMAIL_HOST=(str, ""),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    DEFAULT_FROM_EMAIL=(str, "noreply@example.com"),
    AWS_ACCESS_KEY_ID=(str, None),
    AWS_SECRET_ACCESS_KEY=(str, None),
    AWS_STORAGE_BUCKET_NAME=(str, ""),
    AWS_S3_REGION_NAME=(str, ""),
    AWS_S3_CUSTOM_DOMAIN=(str, ""),
    STATICFILES_STORAGE=(str, "django.contrib.staticfiles.storage.StaticFilesStorage"),
    DEFAULT_FILE_STORAGE=(str, "django.core.files.storage.FileSystemStorage"),
    STRIPE_PUBLIC_KEY=(str, ""),
    STRIPE_SECRET_KEY=(str, ""),
    STRIPE_WEBHOOK_SECRET=(str, ""),
)

# Read .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# =============================================================================
# CORE DJANGO SETTINGS
# =============================================================================

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Application Definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    # Future: django-rest-framework
    # Future: django-cors-headers
    # Future: django-filter
    # Future: drf-spectacular
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.products",
    "apps.orders",
    "apps.payments",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

# URL Configuration
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                # Custom context processors
                "apps.products.context_processors.categories",
                "apps.orders.context_processors.cart_item_count",
            ],
            "builtins": [
                "django.templatetags.static",
            ],
        },
    },
]

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    "default": env.db("DATABASE_URL")
}

# Connection pooling for production
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =============================================================================
# AUTHENTICATION
# =============================================================================

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Session Configuration
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

SITE_ID = 1

# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# =============================================================================
# MEDIA FILES
# =============================================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# =============================================================================
# LOGGING
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# =============================================================================
# CACHING (Redis-ready placeholder)
# =============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Redis configuration (uncomment when Redis is available)
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "PARSER_CLASS": "redis.connection.HiredisParser",
#             "CONNECTION_POOL_CLASS": "redis.connection.BlockingConnectionPool",
#             "CONNECTION_POOL_CLASS_KWARGS": {
#                 "max_connections": 50,
#                 "timeout": 20,
#             },
#             "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#         },
#         "KEY_PREFIX": "django_ecommerce",
#         "TIMEOUT": 300,
#     }
# }

# =============================================================================
# CELERY CONFIGURATION (Placeholder for future async tasks)
# =============================================================================

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# =============================================================================
# STRIPE PAYMENT CONFIGURATION
# =============================================================================

STRIPE_PUBLIC_KEY = env("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")

# =============================================================================
# E-COMMERCE SPECIFIC SETTINGS
# =============================================================================

# Currency
DEFAULT_CURRENCY = "USD"
DEFAULT_CURRENCY_SYMBOL = "$"

# Order Settings
ORDER_EXPIRY_HOURS = 24
CART_SESSION_ID = "cart"

# Shipping
FREE_SHIPPING_THRESHOLD = 100.00
FLAT_SHIPPING_RATE = 9.99

# Pagination
PRODUCTS_PER_PAGE = 12
ORDERS_PER_PAGE = 10

# =============================================================================
# SECURITY SETTINGS (Base - overridden in production)
# =============================================================================

# These are base settings - production.py will override with secure values
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Content Security Policy (future: django-csp)
# CSP_DEFAULT_SRC = ("'self'",)
# CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
