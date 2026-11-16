# Local-only settings: same as settings.py but uses SQLite instead of PostgreSQL.
# Run with: python manage.py runserver --settings=intellearn.settings_local
from .settings import *  # noqa: F401,F403
from .settings import BASE_DIR

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
