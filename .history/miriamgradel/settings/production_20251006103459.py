# miriamgradel/settings/production.py  (TEMPORARY rollback)
from .base import *

DEBUG = False

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}

if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")


