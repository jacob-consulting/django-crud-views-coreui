SECRET_KEY = "test-only-not-secret"

# django_coreui alone: no crispy, no crud_views (it must not need them).
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.messages",
    "django_coreui",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

# The shell's templates reverse the auth URLs and load their static files.
ROOT_URLCONF = "tests.django_coreui.urls"
STATIC_URL = "/static/"
