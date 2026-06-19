from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared Limiter instance: imported by main.py (to wire the middleware and
# exception handler) and by individual routers (to decorate specific
# endpoints with a tighter limit). Routes without an explicit @limiter.limit
# fall back to default_limits.
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
