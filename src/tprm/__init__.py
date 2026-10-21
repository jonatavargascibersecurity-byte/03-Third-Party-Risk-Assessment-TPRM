"""Public API."""

from __future__ import annotations

from .loader import DataError, TPRMSet, load_tprm

__version__ = "1.0.0"
__all__ = ["DataError", "TPRMSet", "load_tprm"]
