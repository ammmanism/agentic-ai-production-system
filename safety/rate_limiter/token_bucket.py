import redis.asyncio as redis
import time
from typing import Optional

class TokenBucketRateLimiter:
    """
    Redis-backed atomic token bucket rate limiter using Lua scripting.
    Ensures thread-safety and scalability across multiple API instances.
    """
    def __init__(self, redis_url: str, default_tokens: int = 10, default_refill_rate: float = 1.0):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_tokens = default_tokens
        self.default_refill_rate = default_refill_rate

        # Lua script: consume tokens atomically
        self.consume_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local requested = tonumber(ARGV[2])
        local capacity = tonumber(ARGV[3])
        local refill_rate = tonumber(ARGV[4])

        local bucket = redis.call('hmget', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1])
        local last_refill = tonumber(bucket[2])

        if tokens == nil then
            tokens = capacity
            last_refill = now
        end

        local elapsed = now - last_refill
        local new_tokens = math.min(capacity, tokens + elapsed * refill_rate)

        if new_tokens >= requested then
            new_tokens = new_tokens - requested
            redis.call('hmset', key, 'tokens', new_tokens, 'last_refill', now)
            redis.call('expire', key, 3600)  -- expire after 1h idle
            return 1
        else
            return 0
        end
        """

    async def consume(self, client_id: str, tokens: int = 1) -> bool:
        """
        Consumes tokens for a given client_id. Returns True if allowed, False otherwise.
        """
        now = time.time()
        key = f"rate_limit:{client_id}"
        result = await self.redis.eval(
            self.consume_script,
            1,
            key,
            now,
            tokens,
            self.default_tokens,
            self.default_refill_rate
        )
        return bool(result)
