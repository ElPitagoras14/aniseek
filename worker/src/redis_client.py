import redis
from config import general_settings

REDIS_URL = general_settings.REDIS_URL

redis_db = redis.Redis.from_url(f"{REDIS_URL}/2")
