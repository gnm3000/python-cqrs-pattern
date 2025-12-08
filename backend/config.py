from __future__ import annotations

import os
from typing import Final

REDIS_HOST: Final = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: Final = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB: Final = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD: Final | None = os.getenv("REDIS_PASSWORD")
