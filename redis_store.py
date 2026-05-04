import json
import os

from dotenv import load_dotenv
import redis


load_dotenv()

DEFAULT_REDIS_URL = "redis://localhost:6379/0"


def get_redis_client():
    redis_url = os.environ.get("REDIS_URL", DEFAULT_REDIS_URL)
    return redis.Redis.from_url(redis_url, decode_responses=True)


def get_json(key):
    value = get_redis_client().get(key)

    if value is None:
        return None

    return json.loads(value)


def set_json(key, value, ex=None):
    get_redis_client().set(key, json.dumps(value), ex=ex)
