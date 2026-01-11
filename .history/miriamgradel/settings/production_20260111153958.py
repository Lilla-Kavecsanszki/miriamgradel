"""
Production settings.

Keeps production overrides minimal and explicit.
"""

from __future__ import annotations

from .base import *  # noqa: F403  (base defines the full settings surface)


# -----------------------
# Core
# -----------------------
DEBUG = False


# -----------------------
# WhiteNoise
# -----------------------
# Ensure WhiteNoise middleware is present right after SecurityMiddleware
_WHITENOISE = "whitenoise.middleware.WhiteNoiseMiddleware"

if _WHITENOISE not in MIDDLEWARE:  # noqa: F405
    try:
        security_index = MIDDLEWARE.index(  # noqa: F405
            "django.middleware.security.SecurityMiddleware"
        )
    except ValueError:
        security_index = 0

    MIDDLEWARE.insert(security_index + 1, _WHITENOISE)  # noqa: F405


# -----------------------
# Security / HTTPS
# -----------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

# Strongly recommended secure headers (safe defaults in production)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# If you have any HTTP pages embedding HTTPS assets, you may need:
# SECURE_CONTENT_TYPE_NOSNIFF = True  # usually set in base already


# -----------------------
# Logging
# -----------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
