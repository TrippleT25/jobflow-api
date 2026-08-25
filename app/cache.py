import json

from redis.asyncio import Redis

from app.config import settings


redis_client = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def get_cache(key: str):
    value = await redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


async def set_cache(
    key: str,
    value,
    expire: int = 60,
):
    await redis_client.set(
        key,
        json.dumps(value, default=str),
        ex=expire,
    )


async def delete_cache_pattern(pattern: str):
    keys = []

    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)

    if keys:
        await redis_client.delete(*keys)