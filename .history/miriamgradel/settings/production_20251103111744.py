# miriamgradel/settings/production.py
from .base import *

DEBUG = False

# ✅ Let base.py choose WhiteNoise's CompressedManifest when DEBUG=False.
# (Do NOT override STORAGES["staticfiles"] to StaticFilesStorage.)

# Ensure WhiteNoise middleware is present right after SecurityMiddleware
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Trust Heroku's proxy for scheme
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Force HTTPS in prod
SECURE_SSL_REDIRECT = True

# Optional: simple console logging (helpful on Heroku)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
