from loguru import logger
from redis_client import redis_db


def get_download_key(franchise_id: str):
    return f"lock:franchise:{franchise_id}:download"


def get_ordering_key(franchise_id: str):
    return f"lock:franchise:{franchise_id}:ordering"


def stream_add_event(franchise_id: str, event: str):
    redis_db.xadd(f"stream:franchise:{franchise_id}", {"event": event})


def stream_wait_event(franchise_id: str, event_type: str):
    stream_key = f"stream:franchise:{franchise_id}"
    last_id = "$"
    logger.debug(f"Waiting for event '{event_type}' on {stream_key}")

    while True:
        messages = redis_db.xread(
            {stream_key: last_id},
            block=0,
        )
        for _, entries in messages:
            for msg_id, fields in entries:
                if fields[b"event"].decode() == event_type:
                    return
