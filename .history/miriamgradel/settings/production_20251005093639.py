from .base import *

DEBUG = False

# Force manifest storage in prod (order-proof)
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}

# (Optional safety) ensure WhiteNoise middleware is present early
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
