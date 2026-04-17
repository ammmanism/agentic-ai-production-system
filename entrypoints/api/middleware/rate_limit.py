from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from safety.rate_limiter.token_bucket import TokenBucketRateLimiter
from core.config import settings

# Global rate limiter instance (initialized once, uses Redis)
_rate_limiter = None

def get_rate_limiter() -> TokenBucketRateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = TokenBucketRateLimiter(
            redis_url=settings.REDIS_URL,
            default_tokens=settings.RATE_LIMIT_TOKENS,
            default_refill_rate=settings.RATE_LIMIT_REFILL_RATE
        )
    return _rate_limiter

async def rate_limit_dependency(
    request: Request,
    limiter: TokenBucketRateLimiter = Depends(get_rate_limiter)
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not await limiter.consume(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests")

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # The dependency approach is preferred for FastAPI routes, 
        # but this middleware is here if needed for global filtering.
        return await call_next(request)
