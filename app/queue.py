from arq import create_pool
from arq.connections import ArqRedis, RedisSettings


redis_settings = RedisSettings(
    host="127.0.0.1",
    port=6379,
    database=0,
)


async def create_redis_pool() -> ArqRedis:
    return await create_pool(redis_settings)
