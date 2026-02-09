# box_picker/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "local-dev-only"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "packer",
]

# request/response pipeline
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", # Adds basic security headers
    "django.contrib.sessions.middleware.SessionMiddleware", # Enables session support (not heavily used here but good to have)
    "django.middleware.common.CommonMiddleware", # Handles common tasks like URL normalization
]

ROOT_URLCONF = "box_picker.urls"

TEMPLATES = [] # No server-side templates needed for this API-only app
WSGI_APPLICATION = "box_picker.wsgi.application" # Django’s server entry hook

# DB technically configured but NOT USED by the app (stateless + in-memory).
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = False
