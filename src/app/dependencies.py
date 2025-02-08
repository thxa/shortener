import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from .config import settings

rate_limit = RateLimiter(times=settings.RATE_LIMIT_TIMES, seconds=settings.RATE_LIMIT_SECONDS)

async def init_limiter():
    # redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    redis_connection = redis.from_url(settings.REDIS_URL, encoding="utf8")
    await FastAPILimiter.init(redis_connection)

async def close_limiter():
    await FastAPILimiter.close()
