from arq.connections import RedisSettings

from app.tasks import analyze_vacancy


class WorkerSettings:
    functions = [
        analyze_vacancy,
    ]

    redis_settings = RedisSettings(
        host="127.0.0.1",
        port=6379,
        database=0,
    )
