"""
Development settings.

Never use these settings in production.
"""

from __future__ import annotations

import os

from .base import *  # noqa: F403


# -----------------------
# Core (DEV)
# -----------------------
DEBUG = False

# Use env var if provided; otherwise fall back to a dev-only key.
# This prevents accidentally shipping a real production key in git.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-insecure-secret-key-change-me",
)

# Local dev hosts only (NOT "*")
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
]

# If you're using ngrok/cloudflared locally, add your tunnel host here:
# ALLOWED_HOSTS += ["xxxx.ngrok-free.app"]


# -----------------------
# Email (DEV)
# -----------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@example.com")


# -----------------------
# Optional per-machine overrides
# -----------------------
# Import local.py if present (ignored by git).
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
