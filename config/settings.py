import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("Renseignez DJANGO_SECRET_KEY dans .env ou dans l’environnement.")
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "apps.utilisateurs.apps.UtilisateursConfig",
    "apps.evenements.apps.EvenementsConfig",
    "apps.prestataires.apps.PrestatairesConfig",
    "apps.programmes.apps.ProgrammesConfig",
    "apps.participants.apps.ParticipantsConfig",
    "apps.ressources.apps.RessourcesConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.dashboard.apps.DashboardConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "libraries": {"evenza_ui": "apps.dashboard.templatetags.evenza_ui"},
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "apps.core.context_processors.navigation",
        ],
    },
}]
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / os.getenv("DJANGO_DB_PATH", "db.sqlite3"),
    "OPTIONS": {"timeout": 20, "transaction_mode": "IMMEDIATE"},
}}
AUTH_USER_MODEL = "gestion.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Tunis"
USE_I18N = USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
SESSION_COOKIE_AGE = 7200
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG
EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("DJANGO_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("DJANGO_EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.getenv("DJANGO_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("DJANGO_EMAIL_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("DJANGO_EMAIL_TLS") == "1"
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_FROM_EMAIL", "evenza@localhost")
