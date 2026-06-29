"""Django settings for AI Assistant Platform."""
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Load .env ─────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET", "django-insecure-dev-key-change-in-production")

# ── LLM Configuration ──────────────────────────────────
LLM_API_KEY      = os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL     = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
LLM_MODEL_NAME   = os.getenv("OPENAI_MODEL", "deepseek-chat")
LLM_MAX_TOKENS   = int(os.getenv("LLM_MAX_TOKENS", "4096"))
LLM_TIMEOUT      = int(os.getenv("LLM_TIMEOUT", "60"))
LLM_MAX_RETRIES  = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_RETRY_DELAY  = float(os.getenv("LLM_RETRY_DELAY", "1.0"))

DEBUG = True
ALLOWED_HOSTS = ["*"]

# ── Apps ──────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # local
    "assistant",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ── Database ───────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── Custom User ────────────────────────────────────────
AUTH_USER_MODEL = "assistant.User"

# ── Password ───────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = []
LOGIN_URL = "/admin/login/"

# ── Internationalization ───────────────────────────────
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True
DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"

# ── Static & Media ─────────────────────────────────────
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── DRF ────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "UNICODE_JSON": True,
}

# ── JWT ────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ── CORS ───────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# ── Default primary key ────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
