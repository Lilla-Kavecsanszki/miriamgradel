from .base import *

DEBUG = False

try:
    from .local import *
except ImportError:
    pass


# Force manifest storage in prod (order-proof)
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}

# (Optional safety) ensure middleware present
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
