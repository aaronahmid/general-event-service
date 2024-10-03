"""dev.py
settings for dev environments

WARNING: This settings must not be used in production
to use this settings: set your the environment variable ENV=dev
"""

from config.settings.base import *
from config.settings.base import REST_FRAMEWORK, INSTALLED_APPS, MIDDLEWARE
from config.settings import getenv
from django.core.exceptions import ImproperlyConfigured
import environ
import os
from datetime import timedelta
import ssl
from celery.schedules import crontab

TOKEN_EXPIRE_AT = 60

ALLOWED_HOSTS = ["*"]

# DEV APPS
# NOT ALL LIBRARIES
# HERE MIGHT MAKE IT TO
# STAGING OR PRODUCTION
DEV_APPS = [
    "knox",
    "drf_yasg",
    "coreapi",
    "drf_standardized_errors",
    "django_filters",
    "django_celery_results",
]

INSTALLED_APPS.extend(DEV_APPS)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(DEBUG=(bool, True))
env_file = os.path.join(BASE_DIR, "envs/.env.dev")
env.read_env(env_file)


def getvar(name: str):
    """tries to get the environmental vairable using\
         env or getenv.

        env is bound to this settings while getenv is global.
        getenv gets global, dynamic or user specific environmental\
            variables.
    """
    # first try getting the variable using env
    # if failed, then use getenv
    try:
        var = env(name)
    except ImproperlyConfigured:
        var = getenv(name)
    return var


SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getvar("DBNAME"),
        "USER": getvar("DB_USER"),
        "PASSWORD": getvar("DB_PASSWORD"),
        "HOST": getvar("DB_HOST"),
        "PORT": getvar("DB_PORT"),
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "sslmode": "require",
            # You can also specify other SSL options here if needed
            # "sslrootcert": "/path/to/rootcert",
            # "sslcert": "/path/to/cert",
            # "sslkey": "/path/to/key"
        },
    }
}

CORS_ORIGIN_ALLOW_ALL = True

REST_KNOX = {
    "SECURE_HASH_ALGORITHM": "cryptography.hazmat.primitives.hashes.SHA512",
    "AUTH_TOKEN_CHARACTER_LENGTH": 64,
    "TOKEN_TTL": timedelta(days=5),
    "USER_SERIALIZER": "knox.serializers.UserSerializer",
    "TOKEN_LIMIT_PER_USER": 1,
    "AUTO_REFRESH": True,
    # 'EXPIRY_DATETIME_FORMAT': api_settings.DATETME_FORMAT,
}

# REST FRAMEWORK DEV SETTINGS
REST_FRAMEWORK.update(
    {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "services.authservice.backends.OAuth2ClientCredentialAuthentication",
            "knox.auth.TokenAuthentication",
        ),
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
        "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
        "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    }
)

# OAUTH2 DEV SETTINGS
OAUTH2_PROVIDER = {
    # parses OAuth2 data from application/json requests
    "OAUTH2_BACKEND_CLASS": "oauth2_provider.oauth2_backends.JSONOAuthLibCore",
    # this is the list of available scopes
    "SCOPES": {"read": "Read scope", "write": "Write scope"},
}

# STATIC_URL = "/static/"
# BASE_DIR = BASE_DIR.split("/")
# BASE_DIR.pop()
# BASE_DIR = "/".join(BASE_DIR)
# # STATIC_ROOT = BASE_DIR + "/static"
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Set STATIC_ROOT to the directory where you want to collect static files during deployment
STATIC_ROOT = "/var/www/booking-dev-staticfiles"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URI"),
        # "OPTIONS": {"ssl_cert_reqs": None},
    },
    "fallback": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    },
}

ssl_context = ssl.SSLContext()
ssl_context.check_hostname = False

heroku_redis_ssl_host = {
    "address": getvar("REDIS_URI2"),  # The 'rediss' schema denotes a SSL connection.
    # "ssl_cert_reqs": None,
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_rabbitmq.core.RabbitmqChannelLayer",
        "CONFIG": {"host": getvar("RABBIT_MQ_URI")},
    },
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    }
}


# Result backend (optional, to store task results)
CELERY_RESULT_BACKEND = getvar("CELERY_RESULT_BACKEND")
CELERY_BROKER_URL = getvar("CELERY_BROKER_URL")
# CELERY_BROKER_URL = "redis://localhost:6379"
# CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_TIMEZONE = "Africa/Lagos"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"


# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
# AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME")
# AWS_S3_REGION_NAME = getenv("AWS_S3_REGION_NAME")
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

EMAIL_HOST_USER = getvar("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = getvar("EMAIL_HOST_PASSWORD")

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"

TRUSTED_ORIGINS = ["",]

CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS

TWILIO_ACCOUNT_SID = getvar("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = getvar("TWILIO_AUTH_TOKEN")
TWILIO_SENDER = getvar("TWILIO_SENDER")

# SESSION_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_REDIRECT_EXEMPT = ", "
# SECURE_SSL_HOST = None
# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = "HTTP_X_FORWARDED_PROTO, https"
