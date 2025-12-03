"""
Database package exports.
Exposes Base and imports models to populate metadata.
"""

from .base import Base as Base  # re-export for consumers

# Import models to register them on Base.metadata
from . import models  # noqa: F401
from .models import *  # noqa: F401, F403

__all__ = ["Base"]
