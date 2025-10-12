from pathlib import Path
import os
from dotenv import load_dotenv


# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env") 

# ──────────────────────────────────────────────────────────────────────────────
# Core
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY = "django-insecure-gv8x30iyc@dt-hka)tco4ro6=a9xao^@#6xb0lg%-6_z)3^(2o"
DEBUG = True
ALLOWED_HOSTS: list[str] = []  # ใส่โดเมน/ไอพีตอน deploy

# ──────────────────────────────────────────────────────────────────────────────
# Apps
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Project apps
    "authen",     # custom user
    "course",
    "dashboard",
    "payment",
    "progress",
    "quiz",
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

ROOT_URLCONF = "intellearn.urls"

# ──────────────────────────────────────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # โฟลเดอร์ template กลางของโปรเจกต์
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "intellearn.wsgi.application"

# ──────────────────────────────────────────────────────────────────────────────
# Database (PostgreSQL)
# ──────────────────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "intellearn",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# Password validation
# ──────────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ──────────────────────────────────────────────────────────────────────────────
# i18n / tz
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"  # ถ้าอยากเป็นเวลาไทยใช้ "Asia/Bangkok"
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────────
# Static & Media
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"

# ให้ Django หา static ในโฟลเดอร์ ./static (ตอน dev)
STATICFILES_DIRS = [BASE_DIR / "static"]

# ที่เก็บไฟล์ static ที่ collect ตอน deploy
STATIC_ROOT = BASE_DIR / "staticfiles"

# อัปโหลดไฟล์มีเดีย (เช่น สลิปการโอน)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ──────────────────────────────────────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "authen.User"

LOGIN_URL = "/auth/login/"
LOGOUT_REDIRECT_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"

# ──────────────────────────────────────────────────────────────────────────────
# Stripe (Test Mode)
# ตั้งค่าจาก ENV จะปลอดภัยกว่า: export STRIPE_SECRET_KEY=..., ฯลฯ
# ──────────────────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")          # ใส่ sk_test_xxx ตอนทดสอบ
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")# ใส่ pk_test_xxx
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")  # ใส่ whsec_xxx จาก Stripe CLI
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")       # ใช้สำหรับ success/cancel URL

# ──────────────────────────────────────────────────────────────────────────────
# Django defaults
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
