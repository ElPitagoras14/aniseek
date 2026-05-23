import redis
from loguru import logger

from config import general_settings

# Sync redis client shared across the process. Thread-safe; pool managed
# internally by redis-py.
redis_db = redis.Redis.from_url(f"{general_settings.REDIS_URL}/2")


def download_lock_key(franchise_id: str) -> str:
    return f"lock:franchise:{franchise_id}:download"


def ordering_lock_key(franchise_id: str) -> str:
    return f"lock:franchise:{franchise_id}:ordering"


def stream_add_event(franchise_id: str, event: str) -> None:
    redis_db.xadd(f"stream:franchise:{franchise_id}", {"event": event})


def stream_wait_event(franchise_id: str, event_type: str) -> None:
    stream_key = f"stream:franchise:{franchise_id}"
    last_id = "$"
    logger.debug(f"Waiting for event '{event_type}' on {stream_key}")

    while True:
        messages = redis_db.xread({stream_key: last_id}, block=0)
        for _, entries in messages:
            for _msg_id, fields in entries:
                if fields[b"event"].decode() == event_type:
                    return
