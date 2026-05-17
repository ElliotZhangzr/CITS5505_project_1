import json
import time
from threading import RLock


# Redis-compatible in-process store; avoids a Redis dependency in development
class InMemoryStore:
    def __init__(self):
        self._values = {}
        self._expires_at = {}
        self._lock = RLock()

    def _purge_if_expired(self, key):
        expires_at = self._expires_at.get(key)

        if expires_at is not None and expires_at <= time.time():
            self._values.pop(key, None)
            self._expires_at.pop(key, None)
            return True

        return False

    def get(self, key):
        with self._lock:
            if self._purge_if_expired(key):
                return None

            return self._values.get(key)

    def set(self, key, value, ex=None):
        with self._lock:
            self._values[key] = value

            if ex is None:
                self._expires_at.pop(key, None)
            else:
                self._expires_at[key] = time.time() + int(ex)

    def delete(self, key):
        with self._lock:
            self._values.pop(key, None)
            self._expires_at.pop(key, None)

    def ttl(self, key):
        with self._lock:
            if self._purge_if_expired(key) or key not in self._values:
                return -2

            expires_at = self._expires_at.get(key)

            if expires_at is None:
                return -1

            return max(0, int(expires_at - time.time()))

    def rpush(self, key, *values):
        with self._lock:
            if self._purge_if_expired(key) or key not in self._values:
                self._values[key] = []

            self._values[key].extend(values)

    def lrange(self, key, start, end):
        with self._lock:
            if self._purge_if_expired(key):
                return []

            values = self._values.get(key, [])

            if end == -1:
                return list(values[start:])

            return list(values[start:end + 1])

    def clear(self):
        with self._lock:
            self._values.clear()
            self._expires_at.clear()


_memory_store = InMemoryStore()


def get_memory_client():
    return _memory_store


def clear_memory_store():
    _memory_store.clear()


def get_json(key):
    value = get_memory_client().get(key)

    if value is None:
        return None

    return json.loads(value)


def set_json(key, value, ex=None):
    get_memory_client().set(key, json.dumps(value), ex=ex)
