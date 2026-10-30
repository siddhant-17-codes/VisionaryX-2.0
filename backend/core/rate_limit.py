import math
import threading
import time
from collections import deque

from fastapi import Request

from config.settings import get_settings
from core.exceptions import RateLimitError


def client_ip(request: Request) -> str:
    """The visitor's IP behind Render's proxies.

    On Render every public request passes through Cloudflare, which overwrites
    CF-Connecting-IP, so a caller cannot forge it. X-Forwarded-For is only a fallback:
    proxies append to it, so the leftmost entries are whatever the caller sent. Count
    TRUSTED_PROXY_HOPS entries in from the right instead.
    """
    cf_ip = request.headers.get("cf-connecting-ip", "").strip()
    if cf_ip:
        return cf_ip
    forwarded = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    hops = get_settings().trusted_proxy_hops
    if hops > 0 and len(forwarded) >= hops:
        return forwarded[-hops]
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """Sliding-window limit per key, in memory. Fine for a single Render instance;
    counts reset when the process restarts."""

    def __init__(self, name: str, limit: int, window: int = 60):
        self.name, self.limit, self.window = name, limit, window
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def __call__(self, request: Request) -> None:
        now = time.monotonic()
        key = client_ip(request)
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= now - self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                raise RateLimitError(retry_after=max(1, math.ceil(hits[0] + self.window - now)))
            hits.append(now)
            if len(self._hits) > 10_000:  # drop idle keys so memory stays bounded
                self._hits = {k: v for k, v in self._hits.items() if v and v[-1] > now - self.window}

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


# Per IP per minute. Gemini routes share one budget so a visitor cannot multiply it
# by switching pages.
gemini_limit = RateLimiter("gemini", limit=20)
upload_limit = RateLimiter("upload", limit=5)
generate_limit = RateLimiter("generate", limit=10)
sessions_limit = RateLimiter("sessions", limit=60)

ALL_LIMITERS = (gemini_limit, upload_limit, generate_limit, sessions_limit)
