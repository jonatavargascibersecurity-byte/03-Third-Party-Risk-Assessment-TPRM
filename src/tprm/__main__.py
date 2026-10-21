"""Allow ``python -m tprm``."""

from __future__ import annotations

from .cli import main

raise SystemExit(main())
